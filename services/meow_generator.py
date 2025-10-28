"""
Improved Meow Generation Service with better fallbacks
"""
import logging
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
import soundfile as sf
import time
import uuid

from config import settings
from services.voice_analyzer import VoiceAnalyzer

logger = logging.getLogger(__name__)


class MeowSynthesizer:
    """Synthesizes meow sounds matching voice characteristics"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sample_rate = settings.SAMPLE_RATE

    def generate_meow(self, target_pitch: float, duration: float,
                     pitch_variance: float = 0.3) -> np.ndarray:
        """
        Generate a single meow sound at specified pitch
        """
        # Clamp duration
        duration = max(settings.MEOW_DURATION_MIN,
                      min(duration, settings.MEOW_DURATION_MAX))

        n_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, n_samples)

        # Create pitch contour (meows rise and fall)
        pitch_contour = np.zeros_like(t)
        third = len(t) // 3

        # Rise phase (0 to 1/3)
        pitch_contour[:third] = np.linspace(0.8, 1.2, third)

        # Peak phase (1/3 to 2/3)
        pitch_contour[third:2*third] = 1.2 + 0.1 * np.sin(np.linspace(0, 4*np.pi, third))

        # Fall phase (2/3 to end)
        pitch_contour[2*third:] = np.linspace(1.2, 0.7, len(t) - 2*third)

        # Add some randomness
        if pitch_variance > 0:
            noise = np.random.randn(len(t)) * pitch_variance * 0.1
            pitch_contour += noise

        # Generate base meow using multiple harmonics
        meow = np.zeros_like(t)

        # Fundamental frequency
        phase = 2 * np.pi * target_pitch * t * pitch_contour
        meow += np.sin(phase)

        # Add harmonics for more cat-like quality
        meow += 0.5 * np.sin(2 * phase)  # 2nd harmonic
        meow += 0.3 * np.sin(3 * phase)  # 3rd harmonic
        meow += 0.2 * np.sin(4 * phase)  # 4th harmonic
        meow += 0.1 * np.sin(5 * phase)  # 5th harmonic

        # Add some noise for breathiness
        noise = np.random.randn(len(t)) * 0.1
        meow += noise

        # Apply amplitude envelope (attack, sustain, release)
        envelope = np.ones_like(t)

        # Attack (first 10%)
        attack_len = int(0.1 * len(t))
        envelope[:attack_len] = np.linspace(0, 1, attack_len)

        # Release (last 30%)
        release_len = int(0.3 * len(t))
        envelope[-release_len:] = np.linspace(1, 0, release_len)

        meow *= envelope

        # Normalize
        if np.max(np.abs(meow)) > 0:
            meow = meow / np.max(np.abs(meow)) * 0.8

        return meow.astype(np.float32)

    def generate_meow_sequence(self, voice_analysis: Dict) -> np.ndarray:
        """
        Generate sequence of meows matching the voice analysis
        IMPROVED: Better handling of poor pitch detection
        """
        self.logger.info("Generating meow sequence from voice analysis")

        segments = voice_analysis['speech_segments']
        rhythm = voice_analysis['rhythm_pattern']
        duration = voice_analysis.get('duration', 0)
        mean_pitch = voice_analysis.get('mean_pitch', settings.MEOW_BASE_PITCH)

        # IMPROVED: If we have very few segments but long recording, generate based on duration
        if len(segments) == 0 or (len(segments) < 3 and duration > 3):
            self.logger.warning(f"Poor speech detection ({len(segments)} segments for {duration:.1f}s recording)")
            self.logger.info("Using duration-based meow generation")
            return self._generate_duration_based_meows(duration, mean_pitch)

        # Generate meows for each segment
        meow_sequence = []

        for i, (start, end, pitch) in enumerate(segments):
            # Adjust pitch to cat range
            cat_pitch = self._human_to_cat_pitch(pitch)

            # Get duration from rhythm pattern
            duration = rhythm[i * 2] if i * 2 < len(rhythm) else 0.5

            # Generate meow
            meow = self.generate_meow(
                cat_pitch,
                duration,
                settings.MEOW_PITCH_VARIANCE
            )
            meow_sequence.append(meow)

            # Add silence between meows
            if i * 2 + 1 < len(rhythm):
                silence_duration = abs(rhythm[i * 2 + 1])
                silence = np.zeros(int(silence_duration * self.sample_rate))
                meow_sequence.append(silence)

        # Concatenate all meows
        full_meow = np.concatenate(meow_sequence)

        self.logger.info(f"Generated {len(segments)} meows, total duration: {len(full_meow)/self.sample_rate:.2f}s")

        return full_meow

    def _generate_duration_based_meows(self, recording_duration: float, base_pitch: float) -> np.ndarray:
        """
        Generate meows based on recording duration when speech detection fails
        Creates a sequence of varied meows that roughly match the recording length
        """
        # Target about 30-40% of the original duration (cats are more concise)
        target_duration = min(recording_duration * 0.4, 15.0)  # Cap at 15 seconds
        
        cat_pitch = self._human_to_cat_pitch(base_pitch)
        
        meow_sequence = []
        current_time = 0
        
        # Generate varied meows
        while current_time < target_duration:
            # Random meow duration between 0.4 and 1.0 seconds
            meow_duration = np.random.uniform(0.4, 1.0)
            
            # Vary pitch slightly for each meow
            pitch_variation = cat_pitch * (1 + np.random.uniform(-0.2, 0.2))
            
            # Generate meow
            meow = self.generate_meow(pitch_variation, meow_duration, 0.3)
            meow_sequence.append(meow)
            current_time += meow_duration
            
            # Add random silence between meows (0.1 to 0.4 seconds)
            if current_time < target_duration:
                silence_duration = np.random.uniform(0.1, 0.4)
                silence = np.zeros(int(silence_duration * self.sample_rate))
                meow_sequence.append(silence)
                current_time += silence_duration
        
        full_meow = np.concatenate(meow_sequence)
        
        self.logger.info(f"Generated duration-based meows: {len(full_meow)/self.sample_rate:.2f}s "+
                        f"from {recording_duration:.2f}s recording")
        
        return full_meow

    def _human_to_cat_pitch(self, human_pitch: float) -> float:
        """Convert human pitch to appropriate cat meow pitch"""
        # Human voice: ~85-255 Hz (male), ~165-255 Hz (female)
        # Cat meows: ~200-600 Hz

        min_human = settings.MIN_PITCH
        max_human = settings.MAX_PITCH
        min_cat = 200
        max_cat = 600

        # Linear scaling
        normalized = (human_pitch - min_human) / (max_human - min_human)
        normalized = max(0, min(1, normalized))  # Clamp to 0-1

        cat_pitch = min_cat + normalized * (max_cat - min_cat)

        # Add some randomness
        cat_pitch += np.random.randn() * 30

        # Clamp to reasonable range
        cat_pitch = max(min_cat, min(max_cat, cat_pitch))

        return cat_pitch


class MeowMockeryHandler:
    """Handles the meow mockery call flow"""

    def __init__(self, session):
        self.session = session
        self.logger = logging.getLogger(__name__)
        self.analyzer = VoiceAnalyzer()
        self.synthesizer = MeowSynthesizer()

    def run(self):
        """Execute meow mockery flow"""
        try:
            # Record caller's voice (max 60 seconds, stop on #)
            recording_id = str(uuid.uuid4())
            recording_path = settings.RECORDINGS_DIR / f"caller_{recording_id}"

            self.logger.info(f"Recording caller speech: {recording_path}")

            # Record with 60 second timeout, 3 seconds of silence ends recording
            result = self.session.record_file(
                str(recording_path),
                format="wav",
                escape_digits="#",
                timeout=settings.MAX_RECORDING_DURATION * 1000,  # milliseconds
                silence=3  # 3 seconds of silence
            )

            self.logger.info(f"Recording complete: {result}")

            # Analyze the recording
            recording_file = Path(f"{recording_path}.wav")

            if not recording_file.exists():
                self.logger.error(f"Recording file not found: {recording_file}")
                return

            # Analyze voice
            analysis = self.analyzer.analyze_audio_file(recording_file)

            # Generate meow mockery
            meow_audio = self.synthesizer.generate_meow_sequence(analysis)

            # Save meow audio
            meow_file = settings.GENERATED_DIR / f"meow_{recording_id}.wav"
            sf.write(meow_file, meow_audio, settings.SAMPLE_RATE)

            self.logger.info(f"Generated meow mockery: {meow_file}")

            # Play back the meows
            meow_path_no_ext = str(meow_file).replace('.wav', '')
            self.session.stream_file(meow_path_no_ext)

            # Cleanup
            try:
                recording_file.unlink()
                # Keep meow file for a bit in case needed
            except Exception as e:
                self.logger.warning(f"Cleanup error: {e}")

        except Exception as e:
            self.logger.error(f"Error in meow mockery: {e}", exc_info=True)
