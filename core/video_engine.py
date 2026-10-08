"""
Video generation engine.
Renders styled frames (matching Design/Preview) + TTS audio via ffmpeg.
"""

from __future__ import annotations

import asyncio
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional

from core.mcq_parser import MCQ
from core.design_config import DesignConfig

# frame_renderer needs PyQt6 — imported lazily in generate()


QUALITY_PRESETS = {
    "basic": {
        "crf": 28, "preset": "veryfast", "audio_bitrate": "96k",
        "label": "Fast — smaller file, quicker export",
    },
    "standard": {
        "crf": 23, "preset": "medium", "audio_bitrate": "128k",
        "label": "Classroom — recommended for most lessons",
    },
    "high": {
        "crf": 20, "preset": "slow", "audio_bitrate": "192k",
        "label": "High quality — sharper text, larger file",
    },
    "excellent": {
        "crf": 18, "preset": "slow", "audio_bitrate": "256k",
        "label": "Best quality — slowest export",
    },
}


def _run_ffmpeg(cmd: list, timeout: int = 600) -> tuple[bool, str]:
    try:
        r = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, timeout=timeout,
        )
        if r.returncode == 0:
            return True, ""
        err = (r.stderr or r.stdout or "").strip()
        return False, "\n".join(err.splitlines()[-15:]) or f"exit {r.returncode}"
    except subprocess.TimeoutExpired:
        return False, "ffmpeg timed out"
    except Exception as e:
        return False, str(e)


# Codec id → human label (order = preference for Auto)
CODEC_OPTIONS = [
    ("auto", "Auto (best available)"),
    ("libx264", "CPU H.264 (libx264)"),
    ("h264_nvenc", "NVIDIA GPU (NVENC)"),
    ("h264_qsv", "Intel Quick Sync (QSV)"),
    ("h264_amf", "AMD AMF"),
    ("libx265", "CPU H.265 (libx265)"),
]


def list_available_encoders() -> list[tuple[str, str]]:
    """Return (codec_id, label) pairs that ffmpeg reports as available."""
    try:
        out = subprocess.check_output(
            ["ffmpeg", "-hide_banner", "-encoders"],
            stderr=subprocess.STDOUT, text=True, timeout=10,
        )
    except Exception:
        return [("libx264", "CPU H.264 (libx264)")]

    available = [("auto", "Auto (best available)")]
    for codec_id, label in CODEC_OPTIONS:
        if codec_id == "auto":
            continue
        # ffmpeg encoder list lines look like:  V..... libx264
        if codec_id in out:
            available.append((codec_id, label))
    if len(available) == 1:
        available.append(("libx264", "CPU H.264 (libx264)"))
    return available


def detect_encoder() -> tuple[str, str]:
    """Pick the best hardware encoder if available, else libx264."""
    try:
        out = subprocess.check_output(
            ["ffmpeg", "-hide_banner", "-encoders"],
            stderr=subprocess.STDOUT, text=True, timeout=10,
        )
    except Exception:
        return "libx264", "CPU H.264 (libx264)"

    for codec_id, label in [
        ("h264_nvenc", "NVIDIA GPU (NVENC)"),
        ("h264_qsv", "Intel Quick Sync (QSV)"),
        ("h264_amf", "AMD AMF"),
    ]:
        if codec_id not in out:
            continue
        ok, _ = _run_ffmpeg(
            [
                "ffmpeg", "-hide_banner", "-y",
                "-f", "lavfi", "-i", "color=c=black:s=64x64:d=0.2",
                "-c:v", codec_id, "-f", "null", "-",
            ],
            timeout=20,
        )
        if ok:
            return codec_id, label
    return "libx264", "CPU H.264 (libx264)"


def resolve_encoder(codec_preference: str) -> tuple[str, str]:
    """Resolve 'auto' or a specific codec id to (encoder, label)."""
    if not codec_preference or codec_preference == "auto":
        return detect_encoder()
    for cid, label in CODEC_OPTIONS:
        if cid == codec_preference:
            return cid, label
    return codec_preference, codec_preference


def audio_duration(path: Path) -> float:
    """Return duration in seconds; 0.0 if file missing/unreadable."""
    if not path or not Path(path).exists() or Path(path).stat().st_size < 32:
        return 0.0
    r = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(path),
        ],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
    )
    try:
        return max(0.0, float(r.stdout.strip()))
    except Exception:
        return 0.0


def make_silence(out: Path, seconds: float):
    """Write a valid silent audio file (wav or mp3 based on suffix)."""
    seconds = max(0.05, float(seconds))
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
        "-t", f"{seconds:.3f}",
    ]
    if out.suffix.lower() == ".mp3":
        cmd += ["-c:a", "libmp3lame", "-q:a", "9"]
    else:
        cmd += ["-c:a", "pcm_s16le"]
    cmd.append(str(out))
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _run_edge_tts(text: str, voice: str, rate: str, out_path: Path) -> bool:
    """Run edge-tts in a fresh event loop (safe under Qt)."""
    import edge_tts

    async def _save():
        communicate = edge_tts.Communicate(text, voice, rate=rate or "+0%")
        await communicate.save(str(out_path))

    try:
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(_save())
        finally:
            loop.close()
        return out_path.exists() and out_path.stat().st_size > 100
    except Exception:
        return False


def _run_gtts(text: str, voice: str, out_path: Path) -> bool:
    try:
        from gtts import gTTS
        lang = "ta" if (voice or "").startswith("ta") else "en"
        gTTS(text=text, lang=lang).save(str(out_path))
        return out_path.exists() and out_path.stat().st_size > 100
    except Exception:
        return False


def tts(text: str, voice: str, rate: str, out_path: Path) -> float:
    """
    Synthesize speech to out_path.
    Returns measured duration in seconds (0.3 minimum silence on total failure).
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    text = (text or "").strip()
    if not text:
        make_silence(out_path, 0.3)
        return 0.3

    voice = voice or "en-IN-NeerjaNeural"
    rate = rate or "+0%"

    # Primary: Microsoft Edge neural voices
    if _run_edge_tts(text, voice, rate, out_path):
        dur = audio_duration(out_path)
        if dur >= 0.2:
            return dur

    # Fallback: gTTS
    if _run_gtts(text, voice, out_path):
        dur = audio_duration(out_path)
        if dur >= 0.2:
            return dur

    # Last resort: silence (keeps timeline valid)
    make_silence(out_path, 1.0)
    return 1.0


def _is_tamil_voice(voice: str) -> bool:
    return (voice or "").startswith("ta")


def _text_has_tamil(text: str) -> bool:
    return any("\u0b80" <= ch <= "\u0bff" for ch in (text or ""))


def _mcqs_are_tamil(mcqs) -> bool:
    for m in mcqs or []:
        if _text_has_tamil(getattr(m, "question", "") or ""):
            return True
        for o in getattr(m, "options", None) or []:
            if _text_has_tamil(o):
                return True
    return False


def _resolve_voice_for_content(voice: str, mcqs) -> str:
    """If content is Tamil but voice is English (or empty), force a Tamil neural voice."""
    voice = (voice or "").strip()
    if _mcqs_are_tamil(mcqs) and not _is_tamil_voice(voice):
        return "ta-IN-PallaviNeural"
    if not voice:
        return "en-IN-NeerjaNeural"
    return voice


def _speakable(text: str) -> str:
    """Light normalization so TTS does not spell abbreviations oddly."""
    t = (text or "").strip()
    # Expand common initials so neural voices do not letter-spell them
    replacements = [
        ("பி.ஆர்.", "பி ஆர்"),
        ("பி.ஆர்", "பி ஆர்"),
        ("P.R.", "P R"),
        ("P. R.", "P R"),
        ("வி.வி.", "வி வி"),
        ("வி.வி", "வி வி"),
        ("V.V.", "V V"),
        ("V. V.", "V V"),
        ("Dr.", "Doctor "),
        ("டாக்டர்.", "டாக்டர் "),
    ]
    for a, b in replacements:
        t = t.replace(a, b)
    # Punctuation that edge-tts often swallows or clips around
    for ch in ("!", "?", "…", "—", ";"):
        t = t.replace(ch, ".")
    while ".." in t:
        t = t.replace("..", ".")
    # Collapse repeated spaces
    while "  " in t:
        t = t.replace("  ", " ")
    return t.strip(" .")


# Latin option letters → Tamil phonetics (long vowels so Edge TTS is clear).
# Short "டி" is often clipped/misread; "டீ" reads as a clear option letter.
_TAMIL_LETTER = {"A": "ஏ", "B": "பீ", "C": "சீ", "D": "டீ"}


def _option_speech(letter: str, option_text: str, voice: str) -> str:
    """Spoken line for one MCQ option — letter must always be audible."""
    L = (letter or "").upper()
    body = _speakable(option_text)
    if _is_tamil_voice(voice):
        ta = _TAMIL_LETTER.get(L, L)
        # Letter + answer only (no "விருப்பம்" / Option prefix)
        if body:
            return f"{ta}. {body}".strip()
        return ta
    # English: pad with "Option" so short letters are not clipped
    return f"Option {L}. {body}".strip() if body else f"Option {L}"


def _correct_phrase(mcq: MCQ, voice: str) -> str:
    """Spoken line when the correct option is revealed."""
    ans_idx = ord(mcq.correct) - 65
    ans_text = _speakable(mcq.options[ans_idx]) if 0 <= ans_idx < len(mcq.options) else ""
    letter = (mcq.correct or "").upper()
    if _is_tamil_voice(voice):
        ta = _TAMIL_LETTER.get(letter, letter)
        if ans_text:
            return f"சரியான விடை, {ta}. {ans_text}"
        return f"சரியான விடை, {ta}"
    if ans_text:
        return f"The correct answer is {letter}. {ans_text}"
    return f"The correct answer is {letter}"


@dataclass
class GenerationResult:
    success: bool
    output_path: Optional[str] = None
    message: str = ""
    encoder_used: str = ""


class VideoEngine:
    def __init__(self, work_dir: Optional[Path] = None):
        self.work_dir = work_dir or Path(tempfile.mkdtemp(prefix="vqg_"))
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self._cancel = False
        self.encoder, self.encoder_label = detect_encoder()

    def cancel(self):
        self._cancel = True

    def reset_cancel(self):
        self._cancel = False

    def _clip_from_image(
        self, image: Path, duration: float, out_mp4: Path, width: int, height: int
    ) -> bool:
        """Create a video clip from a still image for `duration` seconds."""
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(image),
            "-t", f"{duration:.3f}",
            "-vf", f"scale={width}:{height}",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "ultrafast",
            "-r", "30",
            str(out_mp4),
        ]
        ok, _ = _run_ffmpeg(cmd, timeout=120)
        return ok

    def generate(
        self,
        mcqs: List[MCQ],
        config: DesignConfig,
        output_path: str,
        preview_only: bool = False,
        progress_cb: Optional[Callable[[int, str], None]] = None,
    ) -> GenerationResult:
        self.reset_cancel()
        from core.frame_renderer import (
            render_intro_frame,
            render_outro_frame,
            render_question_frame,
            save_frame,
        )
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        if not mcqs:
            return GenerationResult(False, message="No questions to generate.")

        items = mcqs[:1] if preview_only else mcqs
        fmt = config.format or "youtube"
        width, height = (1920, 1080) if fmt == "youtube" else (1080, 1920)
        quality = QUALITY_PRESETS.get(config.quality, QUALITY_PRESETS["standard"])
        voice = _resolve_voice_for_content(config.voice.voice_name or "", mcqs)
        rate = config.voice.rate or "+0%"
        # Honour user codec choice (auto → best available)
        self.encoder, self.encoder_label = resolve_encoder(
            getattr(config, "codec", "auto") or "auto"
        )

        def prog(p: int, msg: str):
            if progress_cb:
                progress_cb(p, msg)

        try:
            prog(2, f"Encoder: {self.encoder_label}")
            # Each entry: (video_clip_path, audio_path) — will be muxed then concatenated
            segment_videos: List[Path] = []
            segment_audios: List[Path] = []
            seg_i = 0

            def add_segment(img: Path, audio: Path, duration: float):
                """Queue a still-frame clip. Duration is authoritative."""
                nonlocal seg_i
                duration = max(0.3, float(duration))
                vpath = self.work_dir / f"seg_{seg_i:04d}.mp4"
                if not self._clip_from_image(img, duration, vpath, width, height):
                    raise RuntimeError(f"Failed to build clip from {img.name}")
                # Store intended duration alongside paths for exact mux padding
                segment_videos.append(vpath)
                segment_audios.append((audio, duration))
                seg_i += 1

            # ---- Intro ----
            if config.intro.enabled and not self._cancel:
                prog(5, "Generating intro...")
                intro_img = self.work_dir / "intro.png"
                save_frame(render_intro_frame(width, height, config), intro_img)
                # Hold intro card silently before speech (default 2s)
                before_intro = max(0.0, float(getattr(config.intervals, "before_intro", 2.0) or 0))
                if before_intro > 0.05:
                    pre = self.work_dir / "intro_pre.wav"
                    make_silence(pre, before_intro)
                    add_segment(intro_img, pre, before_intro)
                intro_audio = self.work_dir / "intro.mp3"
                # Soften punctuation so "Quiz Time!" is not clipped to "Time"
                intro_text = _speakable(
                    f"{config.intro.title}. {config.intro.subtitle}"
                )
                speech = tts(intro_text, voice, rate, intro_audio)
                # Never cut speech short; hold at least configured duration
                d = max(float(config.intro.duration or 3.0), speech + 0.25)
                d = min(d, 10.0)  # hard safety cap
                add_segment(intro_img, intro_audio, d)
                # Explicit pause before first question (default 3s)
                after_intro = max(0.0, float(getattr(config.intervals, "after_intro", 3.0) or 0))
                if after_intro > 0.05:
                    gap = self.work_dir / "intro_gap.wav"
                    make_silence(gap, after_intro)
                    add_segment(intro_img, gap, after_intro)

            # ---- Questions ----
            n = len(items)
            for qi, mcq in enumerate(items):
                if self._cancel:
                    return GenerationResult(False, message="Cancelled by user.")

                pct = 10 + int(70 * (qi / max(n, 1)))
                prog(pct, f"Question {qi + 1}/{n}...")

                # --- Question text (no option highlight) ---
                q_img = self.work_dir / f"q{qi}.png"
                save_frame(
                    render_question_frame(
                        width, height, config, mcq, qi, n,
                        highlight_correct=False, highlight_option=None,
                    ),
                    q_img,
                )
                q_audio = self.work_dir / f"q{qi}_q.mp3"
                q_speech = tts(_speakable(mcq.question), voice, rate, q_audio)
                after_q = max(0.0, float(config.intervals.after_question or 0))
                add_segment(q_img, q_audio, q_speech + after_q)

                # --- Each option: highlight while spoken ---
                between = max(0.0, float(config.intervals.between_options or 0))
                for oi, opt in enumerate(mcq.options[:4]):
                    letter = chr(65 + oi)
                    o_img = self.work_dir / f"q{qi}_o{oi}.png"
                    save_frame(
                        render_question_frame(
                            width, height, config, mcq, qi, n,
                            highlight_correct=False, highlight_option=oi,
                        ),
                        o_img,
                    )
                    oa = self.work_dir / f"q{qi}_o{oi}.mp3"
                    o_speech = tts(_option_speech(letter, opt, voice), voice, rate, oa)
                    add_segment(o_img, oa, o_speech + between)

                # Pause after all options — countdown clock under answers
                total_wait = max(0.0, float(config.intervals.before_answer or 0))
                if total_wait > 0.05:
                    whole = max(1, int(round(total_wait)))
                    elapsed = 0.0
                    for sec_left in range(whole, 0, -1):
                        if self._cancel:
                            break
                        c_img = self.work_dir / f"q{qi}_cd{sec_left}.png"
                        save_frame(
                            render_question_frame(
                                width, height, config, mcq, qi, n,
                                highlight_correct=False, highlight_option=None,
                                countdown_seconds=sec_left,
                            ),
                            c_img,
                        )
                        if sec_left == 1:
                            dur = max(0.3, total_wait - elapsed)
                        else:
                            dur = 1.0
                            elapsed += 1.0
                        gap = self.work_dir / f"q{qi}_cd{sec_left}.wav"
                        make_silence(gap, dur)
                        add_segment(c_img, gap, dur)

                # Frame: answer highlight + full "சரியான விடை" / correct announcement
                a_img = self.work_dir / f"q{qi}_ans.png"
                save_frame(
                    render_question_frame(
                        width, height, config, mcq, qi, n, highlight_correct=True
                    ),
                    a_img,
                )
                a_audio = self.work_dir / f"q{qi}_ans.mp3"
                phrase = _correct_phrase(mcq, voice)
                tts_dur = tts(phrase, voice, rate, a_audio)
                if tts_dur < 0.6:
                    # Retry with a shorter guaranteed line
                    L = (mcq.correct or "").upper()
                    if _is_tamil_voice(voice):
                        simple = f"சரியான விடை {_TAMIL_LETTER.get(L, L)}"
                    else:
                        simple = f"Correct answer is {L}"
                    tts_dur = tts(simple, voice, rate, a_audio)
                hold = max(0.5, float(config.intervals.answer_duration or 2.0))
                # Full speech always plays; then hold to answer_duration if needed
                a_dur = max(tts_dur + 0.5, hold)
                add_segment(a_img, a_audio, a_dur)

                # Pause before next question / outro (default 3s)
                after_ans = max(0.0, float(getattr(config.intervals, "after_answer", 3.0) or 0))
                if after_ans > 0.05:
                    gap = self.work_dir / f"q{qi}_after_ans.wav"
                    make_silence(gap, after_ans)
                    add_segment(a_img, gap, after_ans)

            if self._cancel:
                return GenerationResult(False, message="Cancelled by user.")

            # ---- Outro ----
            if config.outro.enabled and not preview_only:
                prog(82, "Generating outro...")
                outro_img = self.work_dir / "outro.png"
                save_frame(render_outro_frame(width, height, config), outro_img)
                outro_audio = self.work_dir / "outro.mp3"
                outro_text = f"{config.outro.title}. {config.outro.subtitle}".strip(". ")
                speech = tts(outro_text, voice, rate, outro_audio)
                # Never cut speech; soft cap so outro cannot run away
                d = max(float(config.outro.duration or 3.0), speech + 0.25)
                d = min(d, 8.0)
                add_segment(outro_img, outro_audio, d)

            # ---- Mux each segment: pad audio UP to duration (never cut speech) ----
            prog(88, "Muxing segments...")
            muxed: List[Path] = []
            for i, (vp, ap_info) in enumerate(zip(segment_videos, segment_audios)):
                if self._cancel:
                    return GenerationResult(False, message="Cancelled by user.")
                ap, dur = ap_info
                ap = Path(ap)
                speech_len = audio_duration(ap)
                # If speech is longer than planned video, extend freeze-frame video
                if speech_len > dur + 0.05:
                    dur = speech_len + 0.15
                    extended = self.work_dir / f"seg_ext_{i:04d}.mp4"
                    ok_ext, _ = _run_ffmpeg([
                        "ffmpeg", "-y", "-stream_loop", "-1", "-i", str(vp),
                        "-t", f"{dur:.3f}",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "ultrafast",
                        str(extended),
                    ], timeout=120)
                    if ok_ext:
                        vp = extended

                mp = self.work_dir / f"mux_{i:04d}.mp4"
                # Pad audio with silence to match video length — never trim speech
                ok, err = _run_ffmpeg([
                    "ffmpeg", "-y",
                    "-i", str(vp),
                    "-i", str(ap),
                    "-filter_complex",
                    f"[1:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=mono,"
                    f"apad=whole_dur={dur:.3f},atrim=0:{dur:.3f},asetpts=PTS-STARTPTS[a]",
                    "-map", "0:v", "-map", "[a]",
                    "-t", f"{dur:.3f}",
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-b:a", quality["audio_bitrate"],
                    str(mp),
                ], timeout=120)
                if not ok:
                    ok, err = _run_ffmpeg([
                        "ffmpeg", "-y",
                        "-i", str(vp),
                        "-i", str(ap),
                        "-f", "lavfi", "-t", f"{dur:.3f}", "-i", "anullsrc=r=44100:cl=mono",
                        "-filter_complex",
                        f"[1:a]aresample=44100,aformat=channel_layouts=mono[a1];"
                        f"[2:a][a1]acrossfade=d=0.01:c1=tri:c2=tri,"
                        f"apad=whole_dur={dur:.3f},atrim=0:{dur:.3f}[a]",
                        "-map", "0:v", "-map", "[a]",
                        "-t", f"{dur:.3f}",
                        "-c:v", "copy",
                        "-c:a", "aac",
                        "-b:a", quality["audio_bitrate"],
                        str(mp),
                    ], timeout=120)
                if not ok:
                    # Last resort: video + audio with -shortest disabled, hard -t
                    ok, err = _run_ffmpeg([
                        "ffmpeg", "-y",
                        "-i", str(vp),
                        "-i", str(ap),
                        "-c:v", "copy",
                        "-c:a", "aac",
                        "-b:a", quality["audio_bitrate"],
                        "-t", f"{dur:.3f}",
                        str(mp),
                    ], timeout=120)
                if not ok:
                    return GenerationResult(False, message=f"Mux failed:\n{err}")
                muxed.append(mp)

            # ---- Concat ----
            prog(92, f"Rendering final video ({self.encoder_label})...")
            list_path = self.work_dir / "concat.txt"
            with open(list_path, "w", encoding="utf-8") as f:
                for m in muxed:
                    p = str(m.resolve()).replace("'", r"'\''")
                    f.write(f"file '{p}'\n")

            # First concat to intermediate with copy
            intermediate = self.work_dir / "all.mp4"
            ok, err = _run_ffmpeg([
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", str(list_path),
                "-c", "copy",
                str(intermediate),
            ], timeout=300)
            if not ok:
                return GenerationResult(False, message=f"Concat failed:\n{err}")

            # Optional background music under the narration
            music_path = (config.voice.music_path or "").strip()
            if config.voice.background_music and music_path and Path(music_path).exists():
                prog(93, "Mixing background music...")
                vol = max(0.05, min(1.0, float(config.voice.music_volume or 0.3)))
                with_music = self.work_dir / "all_music.mp4"
                ok, err = _run_ffmpeg([
                    "ffmpeg", "-y",
                    "-i", str(intermediate),
                    "-stream_loop", "-1", "-i", music_path,
                    "-filter_complex",
                    f"[1:a]volume={vol:.3f}[bg];[0:a][bg]amix=inputs=2:duration=first:dropout_transition=2[aout]",
                    "-map", "0:v", "-map", "[aout]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", quality["audio_bitrate"],
                    "-shortest",
                    str(with_music),
                ], timeout=300)
                if ok:
                    intermediate = with_music
                else:
                    prog(93, f"Music mix skipped: {err[:80]}")

            # Re-encode with target encoder / quality
            encoders = [(self.encoder, self.encoder_label)]
            if self.encoder != "libx264" and self.encoder != "libx265":
                encoders.append(("libx264", "CPU H.264 (libx264) fallback"))

            last_err = ""
            for enc, label in encoders:
                cmd = [
                    "ffmpeg", "-y", "-i", str(intermediate),
                    "-c:v", enc,
                    "-c:a", "aac",
                    "-b:a", quality["audio_bitrate"],
                    "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart",
                ]
                if enc in ("libx264", "libx265"):
                    cmd += ["-crf", str(quality["crf"]), "-preset", quality["preset"]]
                elif "nvenc" in enc:
                    cmd += ["-cq", str(max(15, quality["crf"] - 5)), "-preset", "p4"]
                elif "qsv" in enc:
                    cmd += ["-global_quality", str(quality["crf"]), "-preset", "medium"]
                elif "amf" in enc:
                    cmd += ["-rc", "cqp", "-qp_i", str(quality["crf"])]
                cmd.append(str(out))
                ok, err = _run_ffmpeg(cmd, timeout=900)
                if ok:
                    prog(100, "Done!")
                    return GenerationResult(
                        True, str(out), f"Video saved ({label})", label
                    )
                last_err = err

            return GenerationResult(
                False,
                message=f"ffmpeg failed:\n{last_err}",
            )

        except Exception as e:
            return GenerationResult(False, message=str(e))

    def _concat_audio(self, parts: List[Path], out: Path, bitrate: str):
        list_path = self.work_dir / (out.stem + "_list.txt")
        with open(list_path, "w", encoding="utf-8") as f:
            for a in parts:
                p = str(a.resolve()).replace("'", r"'\''")
                f.write(f"file '{p}'\n")
        ok, err = _run_ffmpeg([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(list_path),
            "-c:a", "aac", "-b:a", bitrate,
            str(out),
        ])
        if not ok:
            raise RuntimeError(f"Audio concat failed: {err}")
