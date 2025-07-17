#!/usr/bin/env python3
"""
Test script to analyze actual context size and its impact on Whisper API costs.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")

import django

django.setup()

from transcription.services import TranscriptionConfig, CampaignContextService


def analyze_context_size():
    """Analyze the actual size of campaign context and its impact on pricing."""

    print("🔍 Analyzing D&D Campaign Context Size and Cost Impact")
    print("=" * 60)

    # Create configuration and context service
    config = TranscriptionConfig()
    context_service = CampaignContextService(config)

    # Get formatted context (what actually gets sent to Whisper)
    formatted_context = context_service.get_formatted_context(max_length=800)

    # Get raw context for analysis
    try:
        raw_context = context_service.get_campaign_context()
        has_database = True
    except Exception as e:
        print(f"⚠️  Database not available: {e}")
        has_database = False
        raw_context = None

    print(f"📊 Context Analysis Results:")
    print(f"   • Max allowed length: 800 characters")
    print(f"   • Actual context length: {len(formatted_context)} characters")
    print(f"   • Characters used: {len(formatted_context)/800*100:.1f}% of limit")
    print()

    if formatted_context:
        print(f"📝 Actual Context Content:")
        print(f"   {repr(formatted_context)}")
        print()
    else:
        print("📝 No campaign context available (empty database or no entities)")
        print()

    if has_database and raw_context:
        print(f"🎲 Database Entity Counts:")
        for category, entities in raw_context.items():
            print(f"   • {category.capitalize()}: {len(entities)} entities")
        print()

    # Analyze prompt components
    print(f"🎯 Complete Whisper Prompt Analysis:")

    # Base prompt (without context)
    base_prompt = """This is a session of a homebrew Dungeons & Dragons game. The player characters include Darnit, Hrothulf, Ego (aka Carlos), Izar, and Dorinda. The last session's transcript is provided below, followed by any chunks transcribed thus far for this player. Distinguish between narration, banter, and in-character dialogue when possible. This is the 1st session for TestPlayer."""

    campaign_context_addition = (
        f"\n\nCampaign Context: {formatted_context}" if formatted_context else ""
    )

    full_prompt = base_prompt + campaign_context_addition

    print(f"   • Base prompt: {len(base_prompt)} characters")
    print(
        f"   • Campaign context addition: {len(campaign_context_addition)} characters"
    )
    print(f"   • Total prompt: {len(full_prompt)} characters")
    print()

    # Cost impact analysis
    print(f"💰 Cost Impact Analysis:")

    # Whisper API pricing: $0.006 per minute of audio
    # The prompt text does NOT affect pricing - Whisper charges by audio duration only!
    print(f"   ✅ GOOD NEWS: Whisper API charges by audio duration only!")
    print(f"   ✅ Prompt text length does NOT affect pricing")
    print(f"   ✅ Campaign context adds ZERO extra cost")
    print()

    print(f"🎉 Summary:")
    print(
        f"   • Context is limited to 800 chars max (actually using {len(formatted_context)})"
    )
    print(f"   • This adds valuable D&D-specific context for better transcription")
    print(
        f"   • No additional cost - Whisper charges $0.006 per minute regardless of prompt"
    )
    print(f"   • Your 12+ hours of audio will still cost ~$4.44 total")


if __name__ == "__main__":
    analyze_context_size()
