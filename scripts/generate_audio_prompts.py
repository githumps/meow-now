#!/usr/bin/env python3
"""
Generate audio prompts using Piper TTS
Run this to create all required IVR audio files
"""
import sys
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings

PROMPTS = {
    "welcome": "Welcome to Meow Now, the premier cat-based voice experience!",
    "main_menu": "Press 1 to have your voice mocked by a cat. Press 2 to hear from our talkative feline friends.",
    "menu_prompt": "Press 1 for meow mockery, or press 2 for talkative cats.",
    "meow_instructions": "Get ready to be mocked! After the beep, start talking. You have 60 seconds. Press pound when you're finished.",
    "meow_goodbye": "Thanks for letting us mock you! Meow!",
    "cats_intro": "Connecting you to one of our talkative cats. Please hold.",
    "goodbye": "Thank you for calling Meow Now. Goodbye!",
    "error": "We're sorry, something went wrong. Please try again later."
}


def generate_prompt(name: str, text: str):
    """Generate a single audio prompt"""
    output_file = settings.PROMPTS_DIR / f"{name}.wav"

    print(f"Generating {name}.wav...")

    try:
        # Use Piper TTS
        if settings.PIPER_MODEL_PATH.exists():
            cmd = [
                "piper",
                "--model", str(settings.PIPER_MODEL_PATH),
                "--output_file", str(output_file)
            ]

            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            stdout, stderr = process.communicate(input=text.encode())

            if process.returncode == 0:
                print(f"  ✓ Created {output_file}")

                # Convert to 8kHz mono for telephony
                temp_file = output_file.with_suffix('.tmp.wav')
                output_file.rename(temp_file)

                convert_cmd = [
                    "sox",
                    str(temp_file),
                    "-r", "8000",
                    "-c", "1",
                    str(output_file)
                ]

                result = subprocess.run(convert_cmd, capture_output=True)

                if result.returncode == 0:
                    temp_file.unlink()
                    print(f"  ✓ Converted to 8kHz mono")
                else:
                    print(f"  ⚠ Warning: Couldn't convert to 8kHz (sox not installed?)")
                    temp_file.rename(output_file)

                return True
            else:
                print(f"  ✗ Failed: {stderr.decode()}")
                return False
        else:
            print(f"  ✗ Piper model not found at {settings.PIPER_MODEL_PATH}")
            print(f"  → Download from: https://github.com/rhasspy/piper/releases")
            return False

    except FileNotFoundError:
        print(f"  ✗ Piper not installed")
        print(f"  → Install with: pip install piper-tts")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    print("=" * 60)
    print("Meow-Now Audio Prompt Generator")
    print("=" * 60)
    print()

    # Check requirements
    print("Checking requirements...")

    if not settings.PIPER_MODEL_PATH.exists():
        print()
        print("ERROR: Piper model not found!")
        print(f"Expected: {settings.PIPER_MODEL_PATH}")
        print()
        print("Download a model:")
        print("1. Visit: https://github.com/rhasspy/piper/releases")
        print("2. Download en_US-lessac-medium.onnx (and .json)")
        print("3. Place in models/piper/ directory")
        print()
        return 1

    print(f"  ✓ Piper model found")
    print()

    # Generate all prompts
    print(f"Generating {len(PROMPTS)} audio prompts...")
    print()

    success_count = 0
    for name, text in PROMPTS.items():
        if generate_prompt(name, text):
            success_count += 1
        print()

    # Summary
    print("=" * 60)
    print(f"Generated {success_count}/{len(PROMPTS)} prompts successfully")
    print("=" * 60)
    print()

    if success_count < len(PROMPTS):
        print("Some prompts failed to generate.")
        print("You can:")
        print("1. Create them manually with Audacity")
        print("2. Download from: https://www.asterisksounds.org/")
        print("3. Use different TTS service")
        print()
        return 1

    print("All prompts generated successfully!")
    print(f"Location: {settings.PROMPTS_DIR}")
    print()
    print("Next steps:")
    print("1. Test prompts by playing them")
    print("2. Adjust volume if needed (use sox)")
    print("3. Start the application: python app.py")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
