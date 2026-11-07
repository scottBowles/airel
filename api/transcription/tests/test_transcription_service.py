"""
Behavior tests for TranscriptionService.process_session_audio.

The service is driven through its public API with a fake transcriber standing in
for the OpenAI boundary. Splitting is stubbed with real AudioData chunks whose
time-offset mappings say where each chunk sits in the original recording.
"""

from unittest.mock import patch

import httpx
from django.test import TestCase
from pydub import AudioSegment

from nucleus import ai
from nucleus.models import GameLog, SessionAudio
from transcription.models import AudioTranscript, TranscriptChunk
from transcription.services.AudioProcessingService import AudioData
from transcription.services.AudioProcessors_DEPRECATED import (
    TimeOffsetMapping,
    TimeOffsetMappingEntry,
)
from transcription.services.TranscriptionConfig import TranscriptionConfig
from transcription.services.TranscriptionService import TranscriptionService

LOW_QUALITY_TEXT = " ".join(["roll"] * 20)


def api_error(message="boom") -> ai.APIError:
    return ai.APIError(
        message, request=httpx.Request("POST", "https://api.openai.com"), body=None
    )


def whisper(text, segments=()):
    return {"text": text, "segments": [dict(s) for s in segments]}


def segment(start, end, text="..."):
    return {"start": start, "end": end, "text": text}


class FakeTranscriber:
    """Returns queued responses in order (raising any that are exceptions) and records prompts."""

    def __init__(self, *responses):
        self.responses = list(responses)
        self.prompts = []

    def __call__(self, file, *, prompt=None):
        assert file.read(), "transcriber should get an open, readable audio file"
        self.prompts.append(prompt)
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def chunk_at(original_start: float, seconds: float = 30.0) -> AudioData:
    """An audio chunk whose processed time 0 is `original_start` in the original file."""
    mapping = TimeOffsetMapping(
        [
            TimeOffsetMappingEntry(
                original_start=original_start,
                original_end=original_start + seconds,
                processed_start=0.0,
                processed_end=seconds,
            )
        ]
    )
    return AudioData.from_audio_segment(
        AudioSegment.silent(duration=int(seconds * 1000)),
        time_offset_mappings=[mapping],
    )


class ProcessSessionAudioTests(TestCase):
    def setUp(self):
        with patch("nucleus.models.GameLog.update_from_google"):
            self.gamelog = GameLog.objects.create(title="Session", url="session")
        self.session_audio = SessionAudio.objects.create(
            gamelog=self.gamelog,
            file="audio/Izar.mp3",
            original_filename="Izar.mp3",
        )
        self.session_audio.file.chunks = lambda: [b"uploaded audio bytes"]
        self.config = TranscriptionConfig(
            enable_audio_preprocessing=False, delay_between_requests=0
        )

    def process(self, transcriber, chunks, **kwargs):
        service = TranscriptionService(self.config, transcriber=transcriber)
        with patch.object(
            service.audio_service, "split_audio_file", return_value=chunks
        ):
            return service.process_session_audio(self.session_audio, **kwargs)

    def test_single_chunk_saves_transcript_on_original_timeline(self):
        transcriber = FakeTranscriber(
            whisper("We attack the void spider.", [segment(2.0, 4.0)])
        )

        result = self.process(transcriber, [chunk_at(50.0)])

        self.assertTrue(result)
        transcript = AudioTranscript.objects.get(session_audio=self.session_audio)
        self.assertEqual(transcript.transcript_text, "We attack the void spider.")
        self.assertEqual(transcript.character_name, "Izar")
        self.assertFalse(transcript.was_split)
        self.assertEqual(transcript.num_chunks, 1)
        seg = transcript.whisper_response["segments"][0]
        self.assertEqual((seg["start"], seg["end"]), (52.0, 54.0))
        self.assertAlmostEqual(transcript.duration_minutes, 54.0 / 60)
        self.assertFalse(TranscriptChunk.objects.exists())

    def test_prompt_carries_character_notes_and_previous_transcript(self):
        transcriber = FakeTranscriber(whisper("Hello."))

        self.process(
            transcriber,
            [chunk_at(0.0)],
            previous_transcript="Last time on Airel",
            session_notes="Joel arrived late.",
        )

        (prompt,) = transcriber.prompts
        self.assertIn("This is Izar", prompt)
        self.assertIn("Joel arrived late.", prompt)
        self.assertIn("Last time on Airel", prompt)

    def test_split_audio_offsets_each_chunk_once(self):
        transcriber = FakeTranscriber(
            whisper("First part.", [segment(0.0, 10.0)]),
            whisper("Second part.", [segment(5.0, 20.0)]),
        )
        chunks = [chunk_at(0.0), chunk_at(100.0)]

        result = self.process(transcriber, chunks)

        self.assertTrue(result)
        transcript = AudioTranscript.objects.get(session_audio=self.session_audio)
        self.assertTrue(transcript.was_split)
        self.assertEqual(transcript.num_chunks, 2)
        self.assertRegex(transcript.transcript_text, r"^First part\.\s+Second part\.$")
        times = [
            (s["start"], s["end"]) for s in transcript.whisper_response["segments"]
        ]
        self.assertEqual(times, [(0.0, 10.0), (105.0, 120.0)])

        saved_chunks = list(transcript.chunks.order_by("chunk_number"))
        self.assertEqual([c.chunk_number for c in saved_chunks], [1, 2])
        self.assertEqual([c.start_time_offset for c in saved_chunks], [0.0, 100.0])
        self.assertEqual([c.duration_seconds for c in saved_chunks], [30.0, 30.0])
        self.assertEqual(
            [c.chunk_text for c in saved_chunks], ["First part.", "Second part."]
        )

    def test_later_chunk_prompts_include_earlier_chunk_text(self):
        transcriber = FakeTranscriber(whisper("Dorinda opens the hatch."), whisper(""))

        self.process(transcriber, [chunk_at(0.0), chunk_at(30.0)])

        first, second = transcriber.prompts
        self.assertIn("the 1st chunk of 2", first)
        self.assertNotIn("Dorinda opens the hatch.", first)
        self.assertIn("the 2nd chunk of 2", second)
        self.assertIn("Dorinda opens the hatch.", second)

    def test_low_quality_transcript_is_retried_without_prompt(self):
        transcriber = FakeTranscriber(whisper(LOW_QUALITY_TEXT), whisper("Clean text."))

        self.process(transcriber, [chunk_at(0.0)])

        self.assertEqual(len(transcriber.prompts), 2)
        self.assertIsNotNone(transcriber.prompts[0])
        self.assertIsNone(transcriber.prompts[1])
        transcript = AudioTranscript.objects.get(session_audio=self.session_audio)
        self.assertEqual(transcript.transcript_text, "Clean text.")

    def test_failed_retry_keeps_first_attempt(self):
        transcriber = FakeTranscriber(whisper(LOW_QUALITY_TEXT), api_error())

        result = self.process(transcriber, [chunk_at(0.0)])

        self.assertTrue(result)
        transcript = AudioTranscript.objects.get(session_audio=self.session_audio)
        # Saved text is cleaned of repetition, so only check it came from attempt one
        self.assertIn("roll", transcript.transcript_text)

    def test_api_failure_saves_nothing(self):
        result = self.process(FakeTranscriber(api_error()), [chunk_at(0.0)])

        self.assertFalse(result)
        self.assertFalse(AudioTranscript.objects.exists())

    def test_invalid_response_saves_nothing(self):
        result = self.process(FakeTranscriber({"no": "text"}), [chunk_at(0.0)])

        self.assertFalse(result)
        self.assertFalse(AudioTranscript.objects.exists())

    def test_failed_chunk_is_skipped_and_the_rest_saved(self):
        transcriber = FakeTranscriber(
            api_error(), whisper("Second part.", [segment(0.0, 5.0)])
        )

        result = self.process(transcriber, [chunk_at(0.0), chunk_at(100.0)])

        self.assertTrue(result)
        transcript = AudioTranscript.objects.get(session_audio=self.session_audio)
        self.assertEqual(transcript.transcript_text, "Second part.")
        (saved_chunk,) = transcript.chunks.all()
        self.assertEqual(saved_chunk.chunk_number, 2)
        self.assertEqual(saved_chunk.start_time_offset, 100.0)

    def test_programming_errors_are_not_swallowed(self):
        with self.assertRaises(TypeError):
            self.process(FakeTranscriber(TypeError("bug")), [chunk_at(0.0)])

    def test_no_chunks_saves_nothing(self):
        result = self.process(FakeTranscriber(), [])

        self.assertFalse(result)
        self.assertFalse(AudioTranscript.objects.exists())
