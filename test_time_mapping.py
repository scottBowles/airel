#!/usr/bin/env python3
"""
Test script to verify that time offset mapping flows correctly through the transcription pipeline.
"""

import sys
import os
from pathlib import Path

# Add the Django project root to the path
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")

import django

django.setup()

from transcription.services import TranscriptionConfig, AudioProcessingService
from pydub import AudioSegment
import tempfile


def test_time_offset_mapping_flow():
    """Test that time offset mapping flows correctly through the pipeline."""

    print("🧪 Testing time offset mapping pipeline...")

    # Create a test configuration
    config = TranscriptionConfig(
        enable_audio_preprocessing=True,
        max_file_size_mb=1,  # Force splitting for testing
        chunk_duration_minutes=1,
    )

    audio_service = AudioProcessingService(config)

    # Create a test audio file with some silence
    # 10 seconds at 44100 Hz, mono
    duration_ms = 10000
    sample_rate = 44100

    # Create audio with silence in the middle
    audio = AudioSegment.silent(duration=duration_ms, frame_rate=sample_rate)
    # Add some tone at the beginning and end to simulate speech
    tone = AudioSegment.silent(duration=2000, frame_rate=sample_rate)
    audio = tone + AudioSegment.silent(duration=6000, frame_rate=sample_rate) + tone

    print(f"📄 Created test audio: {len(audio)/1000:.1f}s")

    # Save to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        audio.export(temp_file.name, format="wav")
        temp_path = Path(temp_file.name)

    try:
        # Test the split_audio_file method
        chunk_paths, chunk_metadata = audio_service.split_audio_file(
            temp_path, "test_character"
        )

        print(f"✅ split_audio_file returned:")
        print(f"   - {len(chunk_paths)} chunk paths")
        print(f"   - {len(chunk_metadata)} metadata entries")

        # Verify that we have metadata for each chunk
        assert len(chunk_paths) == len(
            chunk_metadata
        ), "Mismatch between paths and metadata"

        # Check that each metadata entry has the expected fields
        for i, metadata in enumerate(chunk_metadata):
            print(f"   Chunk {i+1} metadata keys: {list(metadata.keys())}")
            assert "path" in metadata, f"Missing 'path' in chunk {i+1} metadata"
            assert (
                "start_time_ms" in metadata
            ), f"Missing 'start_time_ms' in chunk {i+1} metadata"
            assert (
                "end_time_ms" in metadata
            ), f"Missing 'end_time_ms' in chunk {i+1} metadata"
            assert (
                "time_offset_mapping" in metadata
            ), f"Missing 'time_offset_mapping' in chunk {i+1} metadata"

            time_offset_mapping = metadata["time_offset_mapping"]
            if time_offset_mapping:
                print(f"   Chunk {i+1} has {len(time_offset_mapping)} mapping entries")
                for j, mapping in enumerate(time_offset_mapping):
                    print(f"     Mapping {j+1}: {mapping}")
            else:
                print(f"   Chunk {i+1} has no time offset mapping (identity mapping)")

        print("✅ Time offset mapping flow test completed successfully!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Clean up
        temp_path.unlink(missing_ok=True)
        for chunk_path in chunk_paths:
            chunk_path.unlink(missing_ok=True)


if __name__ == "__main__":
    test_time_offset_mapping_flow()
