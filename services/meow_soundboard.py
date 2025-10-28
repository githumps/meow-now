"""
Multiple Cat Meow Synthesis Methods - Soundboard for Testing
Let's find which one actually sounds like a cat!
"""
import numpy as np
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class MeowSoundboard:
    """Different approaches to synthesizing cat meows"""

    def __init__(self, sample_rate: int = 8000):
        self.sample_rate = sample_rate

    def method_1_simple_sine(self, pitch: float = 400, duration: float = 0.8) -> Tuple[np.ndarray, str]:
        """Method 1: Simple sine wave (current approach - probably sounds like beep)"""
        n_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, n_samples)

        # Pitch contour
        pitch_contour = pitch * (0.8 + 0.4 * np.sin(np.linspace(0, np.pi, n_samples)))

        # Generate sine wave
        phase = 2 * np.pi * np.cumsum(pitch_contour / self.sample_rate)
        audio = 0.3 * np.sin(phase)

        # Envelope
        envelope = np.exp(-3 * t / duration)
        audio *= envelope

        return audio.astype(np.float32), "Simple Sine Wave (beep-like)"

    def method_2_harmonics(self, pitch: float = 400, duration: float = 0.8) -> Tuple[np.ndarray, str]:
        """Method 2: Multiple harmonics (richer tone)"""
        n_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, n_samples)

        # Pitch contour with rise and fall
        pitch_contour = pitch * (0.7 + 0.6 * np.sin(np.linspace(0, np.pi, n_samples)))

        # Generate multiple harmonics
        phase = 2 * np.pi * np.cumsum(pitch_contour / self.sample_rate)
        audio = (
            0.5 * np.sin(phase) +           # Fundamental
            0.3 * np.sin(2 * phase) +       # 2nd harmonic
            0.15 * np.sin(3 * phase) +      # 3rd harmonic
            0.05 * np.sin(5 * phase)        # 5th harmonic
        )

        # Envelope (quick attack, slow decay)
        attack = np.linspace(0, 1, n_samples // 10)
        decay = np.exp(-4 * np.linspace(0, 1, n_samples - len(attack)))
        envelope = np.concatenate([attack, decay])
        audio *= envelope

        return audio.astype(np.float32), "Multiple Harmonics (richer)"

    def method_3_formants(self, pitch: float = 400, duration: float = 0.8) -> Tuple[np.ndarray, str]:
        """Method 3: Formant synthesis (vowel-like resonances)"""
        n_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, n_samples)

        # Pitch contour
        pitch_contour = pitch * (0.6 + 0.8 * np.sin(np.linspace(0, np.pi, n_samples)))

        # Generate sawtooth wave (richer harmonics)
        phase = np.cumsum(pitch_contour / self.sample_rate)
        sawtooth = 2 * (phase - np.floor(phase)) - 1

        # Apply formant filters (resonant peaks like /ae/ vowel)
        # Cat meows have formants around 800Hz, 1200Hz, 2400Hz
        audio = sawtooth

        # Simple formant simulation by adding filtered versions
        from scipy import signal

        # Formant 1: ~800Hz
        b1, a1 = signal.butter(2, [700/self.sample_rate*2, 900/self.sample_rate*2], 'band')
        f1 = signal.lfilter(b1, a1, audio)

        # Formant 2: ~1200Hz
        b2, a2 = signal.butter(2, [1100/self.sample_rate*2, 1300/self.sample_rate*2], 'band')
        f2 = signal.lfilter(b2, a2, audio)

        audio = 0.5 * audio + 0.8 * f1 + 0.5 * f2

        # Envelope
        envelope = np.exp(-3 * t / duration)
        audio *= envelope

        # Normalize
        audio = audio / np.max(np.abs(audio)) * 0.3

        return audio.astype(np.float32), "Formant Synthesis (vowel-like)"

    def method_4_noisy(self, pitch: float = 400, duration: float = 0.8) -> Tuple[np.ndarray, str]:
        """Method 4: Harmonics + noise (breathier, more natural)"""
        n_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, n_samples)

        # Pitch contour
        pitch_contour = pitch * (0.7 + 0.6 * np.sin(np.linspace(0, np.pi, n_samples)))

        # Harmonic content
        phase = 2 * np.pi * np.cumsum(pitch_contour / self.sample_rate)
        harmonics = (
            0.6 * np.sin(phase) +
            0.3 * np.sin(2 * phase) +
            0.15 * np.sin(3 * phase) +
            0.05 * np.sin(5 * phase)
        )

        # Add noise component (breathiness)
        noise = np.random.normal(0, 0.15, n_samples)

        # Mix harmonics and noise
        audio = 0.7 * harmonics + 0.3 * noise

        # Envelope
        envelope = np.exp(-3 * t / duration)
        audio *= envelope

        return audio.astype(np.float32), "Harmonics + Noise (breathy)"

    def method_5_fm_synthesis(self, pitch: float = 400, duration: float = 0.8) -> Tuple[np.ndarray, str]:
        """Method 5: FM synthesis (metallic, complex)"""
        n_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, n_samples)

        # Carrier frequency (base pitch)
        carrier_freq = pitch * (0.7 + 0.6 * np.sin(np.linspace(0, np.pi, n_samples)))

        # Modulator frequency (creates sidebands)
        mod_freq = carrier_freq * 1.5
        mod_index = 3.0

        # FM synthesis
        modulator = mod_index * np.sin(2 * np.pi * np.cumsum(mod_freq / self.sample_rate))
        carrier_phase = 2 * np.pi * np.cumsum(carrier_freq / self.sample_rate)
        audio = 0.3 * np.sin(carrier_phase + modulator)

        # Envelope
        envelope = np.exp(-3 * t / duration)
        audio *= envelope

        return audio.astype(np.float32), "FM Synthesis (metallic)"

    def method_6_triangle_wave(self, pitch: float = 400, duration: float = 0.8) -> Tuple[np.ndarray, str]:
        """Method 6: Triangle wave with harmonics"""
        n_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, n_samples)

        # Pitch contour
        pitch_contour = pitch * (0.7 + 0.6 * np.sin(np.linspace(0, np.pi, n_samples)))

        # Generate triangle wave
        phase = np.cumsum(pitch_contour / self.sample_rate)
        triangle = 2 * np.abs(2 * (phase - np.floor(phase + 0.5))) - 1

        # Add some harmonics
        phase_rad = 2 * np.pi * phase
        audio = 0.6 * triangle + 0.2 * np.sin(2 * phase_rad) + 0.1 * np.sin(3 * phase_rad)

        # Envelope
        envelope = np.exp(-3 * t / duration)
        audio *= envelope

        return audio.astype(np.float32), "Triangle Wave (hollow)"

    def method_7_chirp(self, pitch: float = 400, duration: float = 0.8) -> Tuple[np.ndarray, str]:
        """Method 7: Chirp/sweep (rapid pitch change)"""
        n_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, n_samples)

        # Rapid pitch sweep from low to high to low
        f0 = pitch * 0.5
        f1 = pitch * 1.5

        # Create sweep
        from scipy.signal import chirp
        audio = chirp(t, f0, duration, f1, method='quadratic', phi=-90)

        # Add harmonics
        audio += 0.3 * chirp(t, f0*2, duration, f1*2, method='quadratic', phi=-90)

        # Envelope
        envelope = np.exp(-4 * t / duration)
        audio *= envelope * 0.3

        return audio.astype(np.float32), "Chirp/Sweep (sliding pitch)"

    def method_8_growly(self, pitch: float = 400, duration: float = 0.8) -> Tuple[np.ndarray, str]:
        """Method 8: Growly/rough texture"""
        n_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, n_samples)

        # Base pitch with vibrato
        vibrato = 5  # Hz
        pitch_contour = pitch * (0.7 + 0.6 * np.sin(np.linspace(0, np.pi, n_samples)))
        pitch_contour *= (1 + 0.08 * np.sin(2 * np.pi * vibrato * t))

        # Generate with harmonics
        phase = 2 * np.pi * np.cumsum(pitch_contour / self.sample_rate)
        audio = (
            0.4 * np.sin(phase) +
            0.25 * np.sin(2 * phase) +
            0.15 * np.sin(3 * phase) +
            0.1 * np.sin(4 * phase) +
            0.05 * np.sin(6 * phase)
        )

        # Add amplitude modulation (roughness)
        am_freq = 30  # Hz (creates growl)
        am = 1 + 0.3 * np.sin(2 * np.pi * am_freq * t)
        audio *= am

        # Envelope
        envelope = np.exp(-2.5 * t / duration)
        audio *= envelope

        return audio.astype(np.float32), "Growly/Rough (angry cat?)"

    def generate_all_methods(self, pitch: float = 400, duration: float = 0.8) -> dict:
        """Generate meows using all methods for comparison"""
        methods = {
            'method_1': self.method_1_simple_sine,
            'method_2': self.method_2_harmonics,
            'method_3': self.method_3_formants,
            'method_4': self.method_4_noisy,
            'method_5': self.method_5_fm_synthesis,
            'method_6': self.method_6_triangle_wave,
            'method_7': self.method_7_chirp,
            'method_8': self.method_8_growly,
        }

        results = {}
        for method_name, method_func in methods.items():
            try:
                audio, description = method_func(pitch, duration)
                results[method_name] = {
                    'audio': audio,
                    'description': description,
                    'success': True
                }
            except Exception as e:
                logger.error(f"Error generating {method_name}: {e}")
                results[method_name] = {
                    'audio': None,
                    'description': f"Error: {e}",
                    'success': False
                }

        return results
