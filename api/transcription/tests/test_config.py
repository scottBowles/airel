"""
Tests for TranscriptionConfig class.
"""

from django.test import TestCase

from transcription.services.TranscriptionConfig import TranscriptionConfig


class TranscriptionConfigTests(TestCase):
    """Test the TranscriptionConfig class instance-based configuration."""

    def test_default_initialization(self):
        """Test that config initializes with default values."""
        config = TranscriptionConfig()

        self.assertEqual(config.max_file_size_mb, 10)
        self.assertEqual(config.chunk_duration_minutes, 1)
        self.assertEqual(config.delay_between_requests, 21)
        self.assertEqual(config.recent_threshold_days, 180)
        self.assertEqual(
            config.audio_extensions, [".flac", ".wav", ".aac", ".m4a", ".mp3"]
        )

    def test_custom_initialization(self):
        """Test that config can be initialized with custom values."""
        config = TranscriptionConfig(
            max_file_size_mb=15,
            chunk_duration_minutes=5,
            delay_between_requests=10,
            recent_threshold_days=90,
        )

        self.assertEqual(config.max_file_size_mb, 15)
        self.assertEqual(config.chunk_duration_minutes, 5)
        self.assertEqual(config.delay_between_requests, 10)
        self.assertEqual(config.recent_threshold_days, 90)
