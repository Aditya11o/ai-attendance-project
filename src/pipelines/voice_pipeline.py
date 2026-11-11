import io
import re

import librosa
import numpy as np
import streamlit as st
from faster_whisper import WhisperModel
from resemblyzer import VoiceEncoder, preprocess_wav


CONTRACTION_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bi['’]m\b"), "i am"),
    (re.compile(r"\bim\b"), "i am"),
    (re.compile(r"\bisn['’]?t\b"), "is not"),
    (re.compile(r"\baren['’]?t\b"), "are not"),
    (re.compile(r"\bwasn['’]?t\b"), "was not"),
    (re.compile(r"\bweren['’]?t\b"), "were not"),
    (re.compile(r"\bdon['’]?t\b"), "do not"),
    (re.compile(r"\bdoesn['’]?t\b"), "does not"),
    (re.compile(r"\bdidn['’]?t\b"), "did not"),
    (re.compile(r"\bcan['’]?t\b"), "can not"),
    (re.compile(r"\bcannot\b"), "can not"),
    (re.compile(r"\bcouldn['’]?t\b"), "could not"),
    (re.compile(r"\bwon['’]?t\b"), "will not"),
    (re.compile(r"\bain['’]?t\b"), "is not"),
    (re.compile(r"\bma['’]?am\b"), "maam"),
)

NEGATED_PRESENT_RE = re.compile(
    r"\b(?:not|no|never|neither|nor|without)\s+(?:\w+\s+){0,2}present\b"
)
POSITIVE_PRESENT_RE = re.compile(r"\bpresent\b")
ABSENT_RE = re.compile(r"\babsent\b")

WHISPER_INITIAL_PROMPT = (
    "Classroom roll call: Present, I am present, Present sir, Yes present, "
    "Here present, I am not present, Absent."
)


@st.cache_resource
def load_voice_encoder():
    """Load and cache the Resemblyzer speaker encoder."""
    return VoiceEncoder()


@st.cache_resource
def load_speech_recognizer():
    """Load and cache the Faster-Whisper English speech-to-text model."""
    return WhisperModel("tiny.en", device="cpu", compute_type="int8")


def _l2_normalize(vec) -> np.ndarray | None:
    """Return an L2-normalized float32 1-D vector, or None when invalid."""
    if vec is None:
        return None
    arr = np.asarray(vec, dtype=np.float32).reshape(-1)
    if arr.size == 0:
        return None
    norm = float(np.linalg.norm(arr))
    if norm <= 1e-12:
        return None
    return arr / norm


def normalize_transcript(text: str) -> str:
    """Lowercase, expand contractions, strip punctuation, and collapse whitespace."""
    if not text:
        return ""
    cleaned = text.lower().strip()
    for pattern, replacement in CONTRACTION_PATTERNS:
        cleaned = pattern.sub(replacement, cleaned)
    cleaned = re.sub(r"[^a-z0-9\s]", " ", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def detect_attendance_intent(transcript: str) -> dict[str, object]:
    """Detect positive attendance intent using word-boundary and negation rules."""
    normalized = normalize_transcript(transcript)
    if not normalized:
        return {
            "intent": "none",
            "is_positive": False,
            "normalized_transcript": normalized,
        }

    if NEGATED_PRESENT_RE.search(normalized):
        return {
            "intent": "negated",
            "is_positive": False,
            "normalized_transcript": normalized,
        }

    if POSITIVE_PRESENT_RE.search(normalized):
        return {
            "intent": "present",
            "is_positive": True,
            "normalized_transcript": normalized,
        }

    if ABSENT_RE.search(normalized):
        return {
            "intent": "absent",
            "is_positive": False,
            "normalized_transcript": normalized,
        }

    return {
        "intent": "none",
        "is_positive": False,
        "normalized_transcript": normalized,
    }


def transcribe_audio_segment(audio_array: np.ndarray, sr: int = 16000) -> tuple[str, float]:
    """Transcribe a 16 kHz audio segment and return (text, stt_confidence)."""
    audio_f32 = np.asarray(audio_array, dtype=np.float32).reshape(-1)
    if audio_f32.size == 0:
        return "", 0.0

    # Pad short clips with silence so Whisper captures edge consonants like 'p'/'t'.
    if audio_f32.size < int(sr * 1.5):
        pad = np.zeros(int(sr * 0.25), dtype=np.float32)
        audio_f32 = np.concatenate([pad, audio_f32, pad])

    recognizer = load_speech_recognizer()
    segments, _ = recognizer.transcribe(
        audio_f32,
        language="en",
        beam_size=5,
        vad_filter=False,
        condition_on_previous_text=False,
        initial_prompt=WHISPER_INITIAL_PROMPT,
    )
    segment_list = list(segments)
    if not segment_list:
        return "", 0.0

    transcript = " ".join(seg.text.strip() for seg in segment_list if seg.text).strip()
    logprobs = [float(seg.avg_logprob) for seg in segment_list if hasattr(seg, "avg_logprob")]
    stt_confidence = float(np.clip(np.mean(np.exp(logprobs)), 0.0, 1.0)) if logprobs else 0.0
    return transcript, stt_confidence


def get_voice_embedding(audio_bytes):
    """Extract a normalized 256-D speaker embedding from uploaded audio bytes."""
    try:
        encoder = load_voice_encoder()

        audio, _ = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        wav = preprocess_wav(audio)
        embedding = _l2_normalize(encoder.embed_utterance(wav))
        return embedding.tolist() if embedding is not None else None
    except Exception:
        st.error("Voice recog error")
        return None


def identify_speaker(new_embedding, candidates_dict, threshold: float = 0.62):
    """Identify the best matching candidate by L2-normalized cosine similarity."""
    query_vec = _l2_normalize(new_embedding)
    if query_vec is None or not candidates_dict:
        return None, 0.0

    best_sid = None
    best_score = -1.0

    for sid, stored_embedding in candidates_dict.items():
        candidate_vec = _l2_normalize(stored_embedding)
        if candidate_vec is None or candidate_vec.shape != query_vec.shape:
            continue
        similarity = float(np.dot(query_vec, candidate_vec))
        if similarity > best_score:
            best_score = similarity
            best_sid = sid

    if best_score >= threshold:
        return best_sid, best_score

    return None, max(best_score, 0.0)


def _segment_speech(audio: np.ndarray, sr: int) -> list[tuple[int, int]]:
    """Split audio into speech intervals, merging short inter-word pauses."""
    if audio.size == 0:
        return []

    raw_segments = librosa.effects.split(audio, top_db=28, frame_length=1024, hop_length=256)
    if len(raw_segments) == 0:
        return []

    merge_gap = int(sr * 0.45)
    merged: list[list[int]] = [[int(raw_segments[0][0]), int(raw_segments[0][1])]]
    for start, end in raw_segments[1:]:
        if int(start) - merged[-1][1] <= merge_gap:
            merged[-1][1] = int(end)
        else:
            merged.append([int(start), int(end)])

    min_len = int(sr * 0.20)
    pad_samples = int(sr * 0.08)
    final_segments: list[tuple[int, int]] = []
    for start, end in merged:
        if (end - start) < min_len:
            continue
        padded_start = max(0, start - pad_samples)
        padded_end = min(audio.size, end + pad_samples)
        final_segments.append((padded_start, padded_end))
    return final_segments


def process_bulk_audio(
    audio_bytes,
    candidates_dict,
    threshold: float = 0.62,
    return_details: bool = False,
):
    """Detect positive 'present' utterances via STT and attribute speakers via voice ID."""
    empty_details = {
        "identified": {},
        "unidentified_segments": [],
        "rejected_segments": [],
    }
    try:
        encoder = load_voice_encoder()
        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        segments = _segment_speech(audio, sr)

        identified_scores: dict[object, float] = {}
        identified_details: dict[object, dict[str, object]] = {}
        unidentified_segments: list[dict[str, object]] = []
        rejected_segments: list[dict[str, object]] = []

        for start, end in segments:
            segment_audio = audio[start:end]
            transcript, stt_confidence = transcribe_audio_segment(segment_audio, sr=sr)
            intent_info = detect_attendance_intent(transcript)

            if not intent_info["is_positive"]:
                if transcript:
                    rejected_segments.append(
                        {
                            "start_sec": round(start / sr, 2),
                            "end_sec": round(end / sr, 2),
                            "transcript": transcript,
                            "intent": intent_info["intent"],
                            "stt_confidence": stt_confidence,
                        }
                    )
                continue

            wav = preprocess_wav(segment_audio)
            if wav.size == 0:
                unidentified_segments.append(
                    {
                        "start_sec": round(start / sr, 2),
                        "end_sec": round(end / sr, 2),
                        "transcript": transcript,
                        "stt_confidence": stt_confidence,
                        "best_speaker_score": 0.0,
                    }
                )
                continue

            embedding = encoder.embed_utterance(wav)
            sid, speaker_score = identify_speaker(embedding, candidates_dict, threshold)

            if sid is not None:
                if sid not in identified_scores or speaker_score > identified_scores[sid]:
                    identified_scores[sid] = speaker_score
                    identified_details[sid] = {
                        "speaker_score": float(speaker_score),
                        "stt_confidence": float(stt_confidence),
                        "transcript": transcript,
                        "intent": intent_info["intent"],
                    }
            else:
                unidentified_segments.append(
                    {
                        "start_sec": round(start / sr, 2),
                        "end_sec": round(end / sr, 2),
                        "transcript": transcript,
                        "stt_confidence": float(stt_confidence),
                        "best_speaker_score": float(speaker_score),
                    }
                )

        if return_details:
            return {
                "identified": identified_details,
                "unidentified_segments": unidentified_segments,
                "rejected_segments": rejected_segments,
            }
        return identified_scores
    except Exception:
        st.error("Bulk process error")
        return empty_details if return_details else {}
