"""
Tests for AudioProcessingService: splitting a recording into voiced chunks
that remember where they came from in the original audio.
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.test import TestCase
from pydub import AudioSegment

from transcription.services.AudioProcessingService import (
    AudioProcessingService,
    cleanup_audio_data_files,
)
from transcription.services.TranscriptionConfig import TranscriptionConfig

VAD = "transcription.services.AudioProcessingService.VADProcessingService.extract_voiced_segments"


class SplitAudioFileTests(TestCase):
    def setUp(self):
        self.temp_path = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.temp_path, ignore_errors=True)
        self.recording = self.temp_path / "Izar.wav"
        AudioSegment.silent(duration=100_000).export(self.recording, format="wav")

    def split(self, voiced_segments, chunk_seconds):
        service = AudioProcessingService(
            TranscriptionConfig(chunk_duration_minutes=chunk_seconds / 60)
        )
        with patch(VAD, return_value=voiced_segments):
            chunks = service.split_audio_file(self.recording, "Izar")
        self.addCleanup(cleanup_audio_data_files, chunks)
        return chunks

    def test_groups_voiced_segments_up_to_chunk_duration(self):
        chunks = self.split([(0, 20), (30, 50), (70, 90)], chunk_seconds=40)

        self.assertEqual(len(chunks), 2)
        self.assertAlmostEqual(chunks[0].duration, 40.0, places=1)
        self.assertAlmostEqual(chunks[1].duration, 20.0, places=1)
        self.assertTrue(all(c.character_name == "Izar" for c in chunks))
        self.assertTrue(all(c.file_path.exists() for c in chunks))

    def test_chunk_times_map_back_to_original_recording(self):
        first, second = self.split([(0, 20), (30, 50), (70, 90)], chunk_seconds=40)

        # Silence between voiced segments is cut out of the chunk audio...
        self.assertAlmostEqual(first.convert_processed_to_original_timestamp(5), 5)
        self.assertAlmostEqual(first.convert_processed_to_original_timestamp(25), 35)
        # ...and later chunks start where their audio started in the recording
        self.assertAlmostEqual(second.convert_processed_to_original_timestamp(0), 70)
        self.assertAlmostEqual(second.convert_processed_to_original_timestamp(10), 80)

    def test_no_voiced_audio_gives_no_chunks(self):
        self.assertEqual(self.split([], chunk_seconds=60), [])

    def test_unreadable_file_gives_no_chunks(self):
        garbage = self.temp_path / "broken.mp3"
        garbage.write_bytes(b"not audio")
        service = AudioProcessingService(TranscriptionConfig())

        self.assertEqual(service.split_audio_file(garbage, "Izar"), [])


class FileSizeTests(TestCase):
    def test_file_size_in_megabytes(self):
        with tempfile.NamedTemporaryFile() as f:
            f.write(b"x" * 1024 * 1024)
            f.flush()
            self.assertAlmostEqual(
                AudioProcessingService.get_file_size_mb(Path(f.name)), 1.0
            )

    def test_missing_file_is_zero(self):
        self.assertEqual(
            AudioProcessingService.get_file_size_mb(Path("/nonexistent.mp3")), 0.0
        )
