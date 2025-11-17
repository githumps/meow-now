#!/usr/bin/env python3
"""
Setup script to generate all required audio files for Meow Now
This includes:
1. Realistic cat meow samples
2. IVR audio prompts using TTS
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.real_meow_generator import RealMeowGenerator
from config import settings
import logging
import numpy as np
import soundfile as sf

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_meow_samples():
    """Generate realistic cat meow samples"""
    logger.info("=== Generating Cat Meow Samples ===")

    generator = RealMeowGenerator(sample_rate=settings.SAMPLE_RATE)

    # The RealMeowGenerator automatically generates samples in __init__
    # if none exist, so they should already be created

    samples_dir = Path("audio/meow_samples")
    samples = list(samples_dir.glob("*.wav"))

    logger.info(f"Generated {len(samples)} cat meow samples:")
    for sample in samples:
        logger.info(f"  - {sample.name}")

    return len(samples) > 0


def generate_simple_tone_prompt(text: str, filename: str, duration: float = 0.5):
    """Generate a simple beep tone as a placeholder prompt"""
    logger.info(f"Generating placeholder tone for: {filename}")

    # Generate a simple pleasant tone
    sample_rate = settings.SAMPLE_RATE
    t = np.linspace(0, duration, int(duration * sample_rate))

    # Two-tone sound (like a phone menu)
    tone1 = 0.3 * np.sin(2 * np.pi * 600 * t[:len(t)//2])
    tone2 = 0.3 * np.sin(2 * np.pi * 800 * t[len(t)//2:])
    audio = np.concatenate([tone1, tone2])

    # Apply envelope
    envelope = np.concatenate([
        np.linspace(0, 1, len(audio)//4),
        np.ones(len(audio)//2),
        np.linspace(1, 0, len(audio)//4)
    ])
    audio *= envelope

    output_path = settings.PROMPTS_DIR / filename
    sf.write(output_path, audio, sample_rate)
    logger.info(f"  Created: {output_path}")


def generate_tts_prompt(text: str, filename: str):
    """Generate audio prompt using TTS if available, otherwise use tone"""
    output_path = settings.PROMPTS_DIR / filename

    try:
        # Try espeak if available (simple, usually pre-installed on Linux)
        import subprocess

        logger.info(f"Generating TTS for: {text[:50]}...")

        # Use espeak to generate WAV file
        result = subprocess.run(
            ['espeak', '-w', str(output_path), '-s', '150', text],
            capture_output=True,
            timeout=10
        )

        if result.returncode == 0 and output_path.exists():
            logger.info(f"  Created TTS prompt: {filename}")

            # Convert to 8kHz if needed
            audio, sr = sf.read(output_path)
            if sr != settings.SAMPLE_RATE:
                # Simple resampling
                duration = len(audio) / sr
                target_length = int(duration * settings.SAMPLE_RATE)
                indices = np.linspace(0, len(audio) - 1, target_length)
                audio = np.interp(indices, np.arange(len(audio)), audio)
                sf.write(output_path, audio, settings.SAMPLE_RATE)
                logger.info(f"  Resampled to {settings.SAMPLE_RATE}Hz")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        logger.warning(f"TTS failed ({e}), using tone placeholder")

    # Fallback to tone
    generate_simple_tone_prompt(text, filename)
    return True


def generate_ivr_prompts():
    """Generate all IVR audio prompts"""
    logger.info("=== Generating IVR Prompts ===")

    prompts = {
        "welcome.wav": "Welcome to Meow Now!",
        "main_menu.wav": "Press 1 for meow mockery, where a cat will mock your voice. Press 2 to hear from our talkative cats.",
        "meow_instructions.wav": "Get ready to be mocked by a cat! Start talking after the beep. You have 60 seconds. Press pound when finished.",
        "meow_goodbye.wav": "Thank you for being mocked. Meow!",
        "cats_intro.wav": "Connecting you to one of our talkative felines.",
        "goodbye.wav": "Goodbye from Meow Now!",
        "error.wav": "Invalid selection. Goodbye.",
    }

    for filename, text in prompts.items():
        prompt_path = settings.PROMPTS_DIR / filename
        if prompt_path.exists():
            logger.info(f"Prompt already exists: {filename}")
            continue

        generate_tts_prompt(text, filename)

    logger.info(f"IVR prompts complete in {settings.PROMPTS_DIR}")
    return True


def verify_audio_files():
    """Verify all required audio files exist"""
    logger.info("=== Verifying Audio Files ===")

    required_prompts = [
        "welcome.wav",
        "main_menu.wav",
        "meow_instructions.wav",
        "meow_goodbye.wav",
        "cats_intro.wav",
        "goodbye.wav",
        "error.wav"
    ]

    all_good = True
    for prompt in required_prompts:
        path = settings.PROMPTS_DIR / prompt
        if path.exists():
            size = path.stat().st_size
            logger.info(f"  ✓ {prompt} ({size} bytes)")
        else:
            logger.error(f"  ✗ {prompt} MISSING")
            all_good = False

    # Check meow samples
    samples_dir = Path("audio/meow_samples")
    samples = list(samples_dir.glob("*.wav"))
    logger.info(f"  ✓ {len(samples)} meow samples")

    if len(samples) < 3:
        logger.warning("  ⚠ Consider adding more meow variety")

    return all_good


def main():
    """Main setup function"""
    logger.info("=" * 60)
    logger.info("Meow Now Audio Setup")
    logger.info("=" * 60)

    # Ensure directories exist
    logger.info("Creating directories...")
    for directory in [settings.PROMPTS_DIR, settings.CATS_DIR,
                     settings.RECORDINGS_DIR, settings.GENERATED_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"  ✓ {directory}")

    # Generate meow samples
    success = generate_meow_samples()
    if not success:
        logger.error("Failed to generate meow samples!")
        return 1

    # Generate IVR prompts
    success = generate_ivr_prompts()
    if not success:
        logger.error("Failed to generate IVR prompts!")
        return 1

    # Verify everything
    if not verify_audio_files():
        logger.warning("Some audio files are missing!")
        logger.info("\nNote: You can record professional prompts and replace the generated ones")
        return 1

    logger.info("=" * 60)
    logger.info("✓ Audio setup complete!")
    logger.info("=" * 60)
    logger.info("\nNext steps:")
    logger.info("1. Listen to the generated prompts:")
    logger.info(f"   ls -lh {settings.PROMPTS_DIR}/")
    logger.info("2. Replace with professional recordings if desired")
    logger.info("3. Test the cat meow samples:")
    logger.info(f"   ls -lh audio/meow_samples/")
    logger.info("4. Start the application:")
    logger.info("   docker-compose up -d")

    return 0


if __name__ == "__main__":
    sys.exit(main())
