"""
Tests for TranscriptionConfig class.
"""

import tempfile
import shutil
from pathlib import Path

from django.test import TestCase

from transcription.services.TranscriptionConfig import TranscriptionConfig


class TranscriptionConfigTests(TestCase):
    """Test the TranscriptionConfig class instance-based configuration."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        # Clean up temp directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_default_initialization(self):
        """Test that config initializes with default values."""
        config = TranscriptionConfig()

        self.assertEqual(config.max_file_size_mb, 10)
        self.assertEqual(config.chunk_duration_minutes, 10)
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

    def test_multiple_config_instances_independence(self):
        """Test that multiple config instances don't interfere with each other."""
        config1 = TranscriptionConfig(max_file_size_mb=10)
        config2 = TranscriptionConfig(max_file_size_mb=25)

        # Verify configs are independent
        self.assertNotEqual(config1.max_file_size_mb, config2.max_file_size_mb)

    def test_no_shared_state_between_instances(self):
        """Test that modifying one config doesn't affect another."""
        config1 = TranscriptionConfig(max_file_size_mb=10)
        config2 = TranscriptionConfig(max_file_size_mb=20)

        # Modify config1
        config1.max_file_size_mb = 15

        # Verify config2 is unchanged
        self.assertEqual(config2.max_file_size_mb, 20)
        self.assertNotEqual(config1.max_file_size_mb, config2.max_file_size_mb)
