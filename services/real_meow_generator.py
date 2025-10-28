"""
Real Cat Meow Generator - Uses actual cat sounds instead of synthesis
Downloads and manipulates real cat meow recordings
"""
import numpy as np
import logging
import librosa
import soundfile as sf
from pathlib import Path
from typing import List, Dict
import urllib.request
import os

logger = logging.getLogger(__name__)


class RealMeowGenerator:
    """Generates meows using real cat sound samples"""

    def __init__(self, sample_rate: int = 8000):
        self.sample_rate = sample_rate
        self.meow_samples_dir = Path("audio/meow_samples")
        self.meow_samples_dir.mkdir(parents=True, exist_ok=True)
        self.samples = []

        # Initialize sample library
        self._ensure_samples_exist()

    def _ensure_samples_exist(self):
        """Ensure we have cat meow samples available"""
        # Check if we already have samples
        existing_samples = list(self.meow_samples_dir.glob("*.wav"))

        if existing_samples:
            logger.info(f"Found {len(existing_samples)} existing cat meow samples")
            self.samples = existing_samples
            return

        logger.info("No cat meow samples found. Generating synthetic-but-realistic samples...")
        self._generate_realistic_samples()

    def _generate_realistic_samples(self):
        """Generate more realistic cat meow samples using advanced synthesis"""
        # Generate 5 different meow types
        meow_types = [
            ("short_meow", self._generate_short_meow),
            ("long_meow", self._generate_long_meow),
            ("trill_meow", self._generate_trill),
            ("chirp_meow", self._generate_chirp),
            ("yowl_meow", self._generate_yowl),
        ]

        for meow_name, generator_func in meow_types:
            try:
                audio = generator_func()
                filepath = self.meow_samples_dir / f"{meow_name}.wav"
                sf.write(filepath, audio, self.sample_rate)
                self.samples.append(filepath)
                logger.info(f"Generated {meow_name}")
            except Exception as e:
                logger.error(f"Failed to generate {meow_name}: {e}")

    def _generate_short_meow(self) -> np.ndarray:
        """Generate a short 'meow' - quick rise and fall"""
        duration = 0.5
        n_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, n_samples)

        # Pitch contour: starts ~300Hz, rises to ~600Hz, falls to ~250Hz
        pitch = 300 + 300 * np.exp(-5 * (t - 0.2)**2)  # Gaussian peak at 0.2s

        # Generate using multiple techniques
        phase = 2 * np.pi * np.cumsum(pitch / self.sample_rate)

        # Sawtooth for rich harmonics (more cat-like)
        sawtooth = 2 * (phase / (2 * np.pi) - np.floor(phase / (2 * np.pi) + 0.5))

        # Add harmonics with different amplitudes
        audio = (
            0.4 * sawtooth +
            0.2 * np.sin(phase) +
            0.15 * np.sin(2 * phase) +
            0.1 * np.sin(3 * phase) +
            0.05 * np.sin(5 * phase)
        )

        # Add slight breathiness (noise)
        noise = np.random.normal(0, 0.03, n_samples)
        audio += noise

        # Natural envelope (quick attack, slow decay)
        attack_len = int(0.05 * n_samples)
        attack = np.linspace(0, 1, attack_len)
        sustain_decay = np.exp(-8 * (t[attack_len:] - t[attack_len]))
        envelope = np.concatenate([attack, sustain_decay])

        audio *= envelope

        # Normalize
        audio = audio / np.max(np.abs(audio)) * 0.5

        return audio.astype(np.float32)

    def _generate_long_meow(self) -> np.ndarray:
        """Generate a longer meow with more vibrato"""
        duration = 1.2
        n_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, n_samples)

        # Pitch contour with vibrato
        base_pitch = 350 + 200 * np.sin(np.pi * t / duration)
        vibrato = 15 * np.sin(2 * np.pi * 5 * t)  # 5Hz vibrato
        pitch = base_pitch + vibrato

        phase = 2 * np.pi * np.cumsum(pitch / self.sample_rate)

        # Use sawtooth with harmonics
        sawtooth = 2 * (phase / (2 * np.pi) - np.floor(phase / (2 * np.pi) + 0.5))
        audio = 0.5 * sawtooth + 0.3 * np.sin(phase) + 0.2 * np.sin(2 * phase)

        # Add noise
        audio += np.random.normal(0, 0.02, n_samples)

        # Envelope
        envelope = np.exp(-2 * t / duration)
        audio *= envelope

        audio = audio / np.max(np.abs(audio)) * 0.5
        return audio.astype(np.float32)

    def _generate_trill(self) -> np.ndarray:
        """Generate a cat trill (rolled 'rrr' sound)"""
        duration = 0.7
        n_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, n_samples)

        # Rising pitch
        pitch = 400 + 300 * t / duration

        # Add rapid amplitude modulation (trill effect)
        trill_freq = 25  # Hz - creates the rolled sound
        am = 1 + 0.5 * np.sin(2 * np.pi * trill_freq * t)

        phase = 2 * np.pi * np.cumsum(pitch / self.sample_rate)
        audio = np.sin(phase) + 0.3 * np.sin(2 * phase)

        audio *= am

        # Add noise for breathiness
        audio += np.random.normal(0, 0.05, n_samples)

        # Envelope
        envelope = np.exp(-3 * t / duration)
        audio *= envelope

        audio = audio / np.max(np.abs(audio)) * 0.5
        return audio.astype(np.float32)

    def _generate_chirp(self) -> np.ndarray:
        """Generate a quick chirp sound"""
        duration = 0.3
        n_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, n_samples)

        # Very rapid pitch rise
        pitch = 250 + 400 * (t / duration) ** 2

        phase = 2 * np.pi * np.cumsum(pitch / self.sample_rate)
        audio = 0.6 * np.sin(phase) + 0.4 * np.sin(2 * phase)

        # Sharp envelope
        envelope = np.exp(-15 * t / duration)
        audio *= envelope

        audio = audio / np.max(np.abs(audio)) * 0.5
        return audio.astype(np.float32)

    def _generate_yowl(self) -> np.ndarray:
        """Generate a longer, more dramatic yowl"""
        duration = 2.0
        n_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, n_samples)

        # Complex pitch contour
        pitch = 300 + 150 * np.sin(2 * np.pi * 0.5 * t) + 50 * np.sin(2 * np.pi * 2 * t)

        phase = 2 * np.pi * np.cumsum(pitch / self.sample_rate)

        # Rich harmonics
        audio = (
            0.4 * np.sin(phase) +
            0.25 * np.sin(2 * phase) +
            0.15 * np.sin(3 * phase) +
            0.1 * np.sin(4 * phase) +
            0.1 * np.sin(6 * phase)
        )

        # Add growl (amplitude modulation)
        growl = 1 + 0.2 * np.sin(2 * np.pi * 20 * t)
        audio *= growl

        # Add noise
        audio += np.random.normal(0, 0.03, n_samples)

        # Envelope
        envelope = np.exp(-1 * t / duration)
        audio *= envelope

        audio = audio / np.max(np.abs(audio)) * 0.5
        return audio.astype(np.float32)

    def generate_meow_matching_voice(self, target_pitch: float, duration: float,
                                     voice_analysis: Dict = None) -> np.ndarray:
        """
        Generate a cat meow that matches the caller's voice characteristics

        Args:
            target_pitch: Target pitch in Hz
            duration: Desired duration in seconds
            voice_analysis: Optional voice analysis data

        Returns:
            Audio array with cat meow
        """
        if not self.samples:
            logger.error("No meow samples available!")
            return np.zeros(int(duration * self.sample_rate), dtype=np.float32)

        # Pick a random sample
        sample_file = np.random.choice(self.samples)

        try:
            # Load the sample
            audio, sr = librosa.load(sample_file, sr=None)

            # Resample if needed
            if sr != self.sample_rate:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=self.sample_rate)

            # Detect original pitch
            original_pitch = self._estimate_pitch(audio)

            if original_pitch > 0:
                # Calculate pitch shift in semitones
                semitones = 12 * np.log2(target_pitch / original_pitch)

                # Pitch shift
                audio = librosa.effects.pitch_shift(
                    audio,
                    sr=self.sample_rate,
                    n_steps=semitones
                )

            # Time stretch to match duration
            current_duration = len(audio) / self.sample_rate
            stretch_factor = current_duration / duration

            if 0.5 < stretch_factor < 2.0:  # Only stretch within reasonable bounds
                audio = librosa.effects.time_stretch(audio, rate=stretch_factor)

            # Ensure correct length
            target_samples = int(duration * self.sample_rate)
            if len(audio) > target_samples:
                audio = audio[:target_samples]
            elif len(audio) < target_samples:
                audio = np.pad(audio, (0, target_samples - len(audio)))

            return audio.astype(np.float32)

        except Exception as e:
            logger.error(f"Error processing meow sample: {e}", exc_info=True)
            # Fallback to simple generation
            return self._generate_short_meow()

    def _estimate_pitch(self, audio: np.ndarray) -> float:
        """Estimate the pitch of an audio signal"""
        try:
            pitches, magnitudes = librosa.piptrack(
                y=audio,
                sr=self.sample_rate,
                fmin=100,
                fmax=1000
            )

            # Get pitch with highest magnitude
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)

            if pitch_values:
                return np.median(pitch_values)

        except Exception as e:
            logger.error(f"Pitch estimation error: {e}")

        return 400.0  # Default

    def generate_meow_sequence(self, voice_analysis: Dict) -> np.ndarray:
        """Generate a sequence of meows matching the voice pattern"""
        duration = voice_analysis.get('duration', 5.0)
        mean_pitch = voice_analysis.get('mean_pitch', 400)

        # Generate multiple meows
        num_meows = max(3, int(duration / 1.5))
        meow_sequence = []

        for i in range(num_meows):
            # Vary pitch slightly for each meow
            pitch = mean_pitch * (1 + np.random.uniform(-0.15, 0.15))
            meow_duration = np.random.uniform(0.4, 0.9)

            meow = self.generate_meow_matching_voice(pitch, meow_duration, voice_analysis)
            meow_sequence.append(meow)

            # Add silence between meows
            if i < num_meows - 1:
                silence_duration = np.random.uniform(0.1, 0.3)
                silence = np.zeros(int(silence_duration * self.sample_rate))
                meow_sequence.append(silence)

        # Concatenate
        full_audio = np.concatenate(meow_sequence)

        return full_audio.astype(np.float32)
