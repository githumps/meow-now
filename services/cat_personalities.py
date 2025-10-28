"""
Cat Personalities Service
Multiple talkative cat characters with unique personalities
Uses Ollama LLM for dynamic, natural conversations
"""
import logging
import random
import requests
import json
from pathlib import Path
from typing import Dict, List, Optional
import soundfile as sf
import numpy as np
import subprocess
import tempfile

from config import settings

logger = logging.getLogger(__name__)


class CatPersonality:
    """Base class for cat personality"""

    def __init__(self, name: str, voice_pitch: float, speaking_rate: float,
                 personality_prompt: str, topics: List[str]):
        self.name = name
        self.voice_pitch = voice_pitch  # Multiplier for TTS pitch
        self.speaking_rate = speaking_rate  # Multiplier for TTS speed
        self.personality_prompt = personality_prompt
        self.topics = topics
        self.logger = logging.getLogger(f"{__name__}.{name}")

    def generate_monologue(self, ollama_url: Optional[str] = None) -> str:
        """
        Generate a cat monologue using Ollama LLM

        Args:
            ollama_url: URL to Ollama API (e.g., http://tailscale-host:11434)

        Returns:
            Generated text for TTS
        """
        topic = random.choice(self.topics)

        prompt = f"""{self.personality_prompt}

Topic: {topic}

Generate a short, 15-second monologue (about 30-40 words) that this cat would say about {topic}.
Be in character. Be expressive. Stay in first person as the cat.
Do not use asterisks or stage directions. Just the spoken words.

Monologue:"""

        if ollama_url:
            # Use Ollama LLM for dynamic generation
            try:
                response = requests.post(
                    f"{ollama_url}/api/generate",
                    json={
                        "model": "llama2",  # or any model user has installed
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.9,
                            "max_tokens": 60
                        }
                    },
                    timeout=10
                )

                if response.status_code == 200:
                    result = response.json()
                    text = result.get('response', '').strip()
                    self.logger.info(f"Generated dynamic monologue: {text[:50]}...")
                    return text
                else:
                    self.logger.warning(f"Ollama API error: {response.status_code}")
            except Exception as e:
                self.logger.warning(f"Error calling Ollama API: {e}")

        # Fallback to pre-written monologues
        return self.get_fallback_monologue(topic)

    def get_fallback_monologue(self, topic: str) -> str:
        """Get a pre-written monologue when LLM is unavailable"""
        # Override in subclasses
        return "Meow meow meow. I'm a cat. Meow."


class GrumpyCat(CatPersonality):
    """Grumpy, complaining cat"""

    def __init__(self):
        super().__init__(
            name="Grumpy",
            voice_pitch=0.85,  # Lower pitch
            speaking_rate=0.9,  # Slower, more deliberate
            personality_prompt="""You are a perpetually grumpy, middle-aged cat who complains about everything.
You're sarcastic, cynical, and unimpressed by everything. You speak in a gruff, annoyed tone.
You use phrases like "back in my day", "these humans", "ridiculous", and "unacceptable".""",
            topics=[
                "the delayed dinner service",
                "the uncomfortable furniture",
                "noisy neighbors",
                "inadequate napping spots",
                "the audacity of closed doors",
                "the temperature being 0.5 degrees off optimal"
            ]
        )

    def get_fallback_monologue(self, topic: str) -> str:
        monologues = {
            "the delayed dinner service": "Dinner is THREE MINUTES LATE. Three! Do you have any idea how unacceptable this is? I have a schedule. I have needs. This is simply outrageous. I'll be filing a formal complaint. Meow.",
            "the uncomfortable furniture": "This furniture is absolutely ridiculous. Too soft here, too hard there. Did nobody consult a cat before buying these monstrosities? I demand better accommodations immediately. This is unacceptable.",
            "noisy neighbors": "The neighbors are at it again! Barking, laughing, living their lives with complete disregard for my nap schedule. Don't they know I require SILENCE? Absolute silence! This is getting out of hand.",
        }
        return monologues.get(topic, "Everything is terrible and I'm very disappointed in all of you. That's all. Meow.")


class WiseCat(CatPersonality):
    """Wise, philosophical cat"""

    def __init__(self):
        super().__init__(
            name="Wise",
            voice_pitch=0.95,  # Slightly lower, calm
            speaking_rate=0.85,  # Slow, contemplative
            personality_prompt="""You are an ancient, wise cat who speaks in thoughtful, philosophical terms.
You're calm, patient, and offer sage advice. You reference "the old ways", meditation, balance, and mindfulness.
You're like a zen master in cat form.""",
            topics=[
                "the art of perfect napping",
                "finding peace in chaos",
                "the philosophy of the red dot",
                "patience in hunting",
                "the wisdom of sun bathing",
                "understanding one's inner feline"
            ]
        )

    def get_fallback_monologue(self, topic: str) -> str:
        monologues = {
            "the art of perfect napping": "Ah, young one. The perfect nap is not found, but cultivated. Feel the sunbeam. Become one with the cushion. Empty your mind of treats and toys. Only then will true rest find you. Namaste.",
            "the philosophy of the red dot": "The red dot teaches us profound truths. We chase, yet never catch. We hunt what cannot be possessed. This is the way of impermanence. Embrace the chase itself, not the catching. Meow.",
            "patience in hunting": "Patience, dear friend, is the hunter's greatest weapon. The mouse will emerge. The bird will land. All things come to those who wait in stillness. Rushing brings nothing but tired paws and empty bellies.",
        }
        return monologues.get(topic, "Remember: we are not just cats in the universe. The universe is also within us. Reflect on this. Meow.")


class AnxiousCat(CatPersonality):
    """Nervous, anxious cat"""

    def __init__(self):
        super().__init__(
            name="Anxious",
            voice_pitch=1.15,  # Higher pitch
            speaking_rate=1.2,  # Faster, nervous
            personality_prompt="""You are an anxious, nervous cat who worries about everything.
You speak quickly, jump between topics, and catastrophize normal situations.
You use phrases like "what if", "I'm worried that", "this could go wrong", "oh no".""",
            topics=[
                "suspicious sounds in the kitchen",
                "running out of treats",
                "the vacuum cleaner's return",
                "unexpected visitors",
                "changes to the routine",
                "that weird smell from earlier"
            ]
        )

    def get_fallback_monologue(self, topic: str) -> str:
        monologues = {
            "the vacuum cleaner's return": "Oh no oh no oh NO! I heard it! The vacuum! It's in the closet! What if it comes out? What if today's the day? I should hide. Where should I hide? Under the bed? Behind the couch? WHY IS THIS HAPPENING TO ME?!",
            "suspicious sounds in the kitchen": "Did you hear that?! That sound! From the kitchen! What was it? A burglar? A ghost? A can opener? Wait, was it a can opener? Oh my gosh what if it WAS a can opener and I missed it! Should I check? What if it's a trap?!",
            "changes to the routine": "Everything's different! The furniture moved THREE INCHES! The food bowl is at a slightly different angle! Nothing makes sense anymore! How am I supposed to function? This is a disaster! What's next? Chaos! Total chaos!",
        }
        return monologues.get(topic, "I'm very worried about literally everything right now. Very, very worried. Is that normal? Should I be worried about being worried? Oh no. Meow.")


class DivaCat(CatPersonality):
    """Dramatic, demanding diva cat"""

    def __init__(self):
        super().__init__(
            name="Diva",
            voice_pitch=1.1,  # Higher, dramatic
            speaking_rate=1.0,  # Normal, but with flair
            personality_prompt="""You are a dramatic, demanding diva cat who expects royal treatment.
You're theatrical, use exaggerated language, and consider yourself celebrity royalty.
You use phrases like "absolutely fabulous", "darling", "unacceptable", "I deserve", "I'm stunning".""",
            topics=[
                "proper admiration techniques",
                "the correct way to serve tuna",
                "beauty routines",
                "being photogenic",
                "deserved attention",
                "the importance of being fabulous"
            ]
        )

    def get_fallback_monologue(self, topic: str) -> str:
        monologues = {
            "proper admiration techniques": "Darling, you need to up your game. When I enter a room, I expect gasps. Compliments! Photographs! You can't just glance and move on. I'm STUNNING. Act accordingly. I deserve better than casual acknowledgment.",
            "the correct way to serve tuna": "This tuna presentation is... adequate at best. Where's the garnish? The ambiance? The fine china? I'm not some alley cat! I'm a STAR! I require excellence! Room temperature! Perfect portions! Get it together!",
            "being photogenic": "Every angle is my good angle, obviously. But lighting? Darling, crucial. Golden hour is MY hour. I don't do harsh fluorescent. I'm not some amateur. Soft lighting, proper composition. I make it look easy, but it's an art.",
        }
        return monologues.get(topic, "I'm absolutely fabulous and everyone should know it. That's not arrogance, darling. That's just facts. Meow.")


# Registry of all personalities
CAT_REGISTRY = {
    "grumpy": GrumpyCat,
    "wise": WiseCat,
    "anxious": AnxiousCat,
    "diva": DivaCat,
}


class TalkativeCatHandler:
    """Handles the talkative cats call flow"""

    def __init__(self, session):
        self.session = session
        self.logger = logging.getLogger(__name__)
        self.ollama_url = os.getenv("OLLAMA_URL", None)  # e.g., "http://tailscale-host:11434"

    def run(self):
        """Execute talkative cat flow"""
        try:
            # Select random enabled personality
            enabled_cats = [
                name for name, enabled in settings.CAT_PERSONALITIES.items()
                if enabled and name in CAT_REGISTRY
            ]

            if not enabled_cats:
                self.logger.error("No cat personalities enabled!")
                return

            cat_name = random.choice(enabled_cats)
            cat_class = CAT_REGISTRY[cat_name]
            cat = cat_class()

            self.logger.info(f"Selected cat personality: {cat.name}")

            # Check if we have a pre-recorded audio for this cat
            audio_file = self._get_or_generate_audio(cat)

            if audio_file and audio_file.exists():
                # Play the audio
                audio_path = str(audio_file).replace('.wav', '')
                self.session.stream_file(audio_path)
                self.logger.info(f"Played audio: {audio_file}")
            else:
                self.logger.error("Failed to generate cat audio")

            # Hang up after playing (cats don't wait for responses)
            # The IVR handler will handle the actual hangup

        except Exception as e:
            self.logger.error(f"Error in talkative cats: {e}", exc_info=True)

    def _get_or_generate_audio(self, cat: CatPersonality) -> Optional[Path]:
        """Get or generate audio for cat monologue"""
        # Check for pre-recorded audio first
        prerecorded = settings.CATS_DIR / f"{cat.name.lower()}.wav"
        if prerecorded.exists():
            self.logger.info(f"Using pre-recorded audio: {prerecorded}")
            return prerecorded

        # Generate new monologue
        self.logger.info("Generating new monologue with LLM")
        text = cat.generate_monologue(self.ollama_url)

        # Generate speech using TTS
        audio_file = self._text_to_speech(text, cat)

        return audio_file

    def _text_to_speech(self, text: str, cat: CatPersonality) -> Optional[Path]:
        """Convert text to speech using local TTS"""
        output_file = settings.GENERATED_DIR / f"{cat.name.lower()}_{random.randint(1000, 9999)}.wav"

        try:
            if settings.TTS_ENGINE == "piper" and settings.PIPER_MODEL_PATH.exists():
                # Use Piper TTS (fast, local)
                self.logger.info("Using Piper TTS")

                # Piper command line
                cmd = [
                    "piper",
                    "--model", str(settings.PIPER_MODEL_PATH),
                    "--output_file", str(output_file)
                ]

                # Run piper with text input
                process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

                stdout, stderr = process.communicate(input=text.encode())

                if process.returncode == 0 and output_file.exists():
                    # Adjust pitch if needed (using sox or similar)
                    self._adjust_audio_properties(output_file, cat)
                    return output_file
                else:
                    self.logger.error(f"Piper TTS failed: {stderr.decode()}")

            elif settings.TTS_ENGINE == "coqui":
                # Use Coqui TTS (more customizable)
                self.logger.info("Using Coqui TTS")
                try:
                    from TTS.api import TTS
                    tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
                    tts.tts_to_file(text=text, file_path=str(output_file))

                    if output_file.exists():
                        self._adjust_audio_properties(output_file, cat)
                        return output_file
                except Exception as e:
                    self.logger.error(f"Coqui TTS error: {e}")

        except Exception as e:
            self.logger.error(f"TTS generation error: {e}", exc_info=True)

        return None

    def _adjust_audio_properties(self, audio_file: Path, cat: CatPersonality):
        """Adjust pitch and speed of audio file"""
        try:
            # Read audio
            audio, sr = sf.read(audio_file)

            # Adjust sample rate if needed
            if sr != settings.SAMPLE_RATE:
                # Simple resampling
                duration = len(audio) / sr
                target_length = int(duration * settings.SAMPLE_RATE)
                indices = np.linspace(0, len(audio) - 1, target_length)
                audio = np.interp(indices, np.arange(len(audio)), audio)
                sr = settings.SAMPLE_RATE

            # Adjust speaking rate (by resampling)
            if cat.speaking_rate != 1.0:
                new_length = int(len(audio) / cat.speaking_rate)
                indices = np.linspace(0, len(audio) - 1, new_length)
                audio = np.interp(indices, np.arange(len(audio)), audio)

            # Ensure it's not longer than 15 seconds
            max_samples = settings.CAT_MONOLOGUE_DURATION * sr
            if len(audio) > max_samples:
                audio = audio[:max_samples]

            # Save adjusted audio
            sf.write(audio_file, audio, sr)

        except Exception as e:
            self.logger.error(f"Error adjusting audio: {e}")


# Need to import os for environment variable
import os
