"""
Voice Analysis Service
Detects pitch, rhythm, and timing from caller's speech
"""
import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import soundfile as sf

try:
    import parselmouth
    from parselmouth.praat import call
    PRAAT_AVAILABLE = True
except ImportError:
    PRAAT_AVAILABLE = False
    logging.warning("Parselmouth not available, pitch detection will be limited")

try:
    import aubio
    AUBIO_AVAILABLE = True
except ImportError:
    AUBIO_AVAILABLE = False
    logging.warning("Aubio not available, using fallback pitch detection")

from config import settings

logger = logging.getLogger(__name__)


class VoiceAnalyzer:
    """Analyzes voice recordings for pitch and rhythm characteristics"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sample_rate = settings.SAMPLE_RATE

    def analyze_audio_file(self, file_path: Path) -> Dict:
        """
        Analyze an audio file and extract pitch/rhythm features

        Returns:
            Dict with keys:
                - mean_pitch: Average pitch in Hz
                - pitch_range: (min, max) pitch in Hz
                - pitch_variance: Standard deviation of pitch
                - speech_segments: List of (start_time, end_time, mean_pitch) tuples
                - rhythm_pattern: List of segment durations
                - speaking_rate: Syllables or segments per second
        """
        self.logger.info(f"Analyzing audio file: {file_path}")

        try:
            # Load audio file
            audio, sr = sf.read(file_path)

            # Convert stereo to mono if needed
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)

            # Resample if needed (usually telephony is 8kHz)
            if sr != self.sample_rate:
                audio = self._resample(audio, sr, self.sample_rate)
                sr = self.sample_rate

            # Detect pitch using available method
            if PRAAT_AVAILABLE:
                pitch_data = self._detect_pitch_praat(audio, sr)
            elif AUBIO_AVAILABLE:
                pitch_data = self._detect_pitch_aubio(audio, sr)
            else:
                pitch_data = self._detect_pitch_basic(audio, sr)

            # Detect speech segments and rhythm
            segments = self._detect_speech_segments(audio, sr, pitch_data)

            # Calculate rhythm pattern
            rhythm = self._analyze_rhythm(segments)

            # Compile results
            valid_pitches = [p for p in pitch_data['pitches'] if p > 0]

            if valid_pitches:
                result = {
                    'mean_pitch': np.mean(valid_pitches),
                    'pitch_range': (np.min(valid_pitches), np.max(valid_pitches)),
                    'pitch_variance': np.std(valid_pitches),
                    'speech_segments': segments,
                    'rhythm_pattern': rhythm,
                    'speaking_rate': len(segments) / (len(audio) / sr) if len(audio) > 0 else 0,
                    'duration': len(audio) / sr
                }
            else:
                # No valid pitch detected
                result = {
                    'mean_pitch': settings.MEOW_BASE_PITCH,
                    'pitch_range': (settings.MEOW_BASE_PITCH - 50, settings.MEOW_BASE_PITCH + 50),
                    'pitch_variance': 20,
                    'speech_segments': [],
                    'rhythm_pattern': [],
                    'speaking_rate': 0,
                    'duration': len(audio) / sr
                }

            self.logger.info(f"Analysis complete: mean_pitch={result['mean_pitch']:.1f}Hz, "
                           f"segments={len(result['speech_segments'])}")
            return result

        except Exception as e:
            self.logger.error(f"Error analyzing audio: {e}", exc_info=True)
            # Return default values
            return {
                'mean_pitch': settings.MEOW_BASE_PITCH,
                'pitch_range': (200, 400),
                'pitch_variance': 50,
                'speech_segments': [],
                'rhythm_pattern': [],
                'speaking_rate': 0,
                'duration': 0
            }

    def _detect_pitch_praat(self, audio: np.ndarray, sr: int) -> Dict:
        """Detect pitch using Praat (most accurate)"""
        self.logger.debug("Using Praat for pitch detection")

        # Create Praat sound object
        sound = parselmouth.Sound(audio, sampling_frequency=sr)

        # Extract pitch
        pitch = call(sound, "To Pitch", 0.0, settings.MIN_PITCH, settings.MAX_PITCH)

        # Get pitch values at regular intervals
        pitch_times = []
        pitches = []

        for t in np.arange(0, sound.duration, 0.01):  # Every 10ms
            pitch_value = call(pitch, "Get value at time", t, "Hertz", "Linear")
            if pitch_value is not None and not np.isnan(pitch_value):
                pitch_times.append(t)
                pitches.append(pitch_value)

        return {
            'times': np.array(pitch_times),
            'pitches': np.array(pitches)
        }

    def _detect_pitch_aubio(self, audio: np.ndarray, sr: int) -> Dict:
        """Detect pitch using Aubio"""
        self.logger.debug("Using Aubio for pitch detection")

        # Aubio pitch detection
        win_s = 4096  # window size
        hop_s = 512   # hop size

        pitch_o = aubio.pitch("yinfft", win_s, hop_s, sr)
        pitch_o.set_unit("Hz")
        pitch_o.set_silence(-40)

        pitches = []
        times = []

        # Convert to float32 for aubio
        audio_float = audio.astype(np.float32)

        # Process in chunks
        for i in range(0, len(audio_float), hop_s):
            chunk = audio_float[i:i+win_s]
            if len(chunk) < win_s:
                chunk = np.pad(chunk, (0, win_s - len(chunk)))

            pitch = pitch_o(chunk)[0]
            confidence = pitch_o.get_confidence()

            if confidence > 0.5 and settings.MIN_PITCH < pitch < settings.MAX_PITCH:
                pitches.append(pitch)
                times.append(i / sr)

        return {
            'times': np.array(times),
            'pitches': np.array(pitches)
        }

    def _detect_pitch_basic(self, audio: np.ndarray, sr: int) -> Dict:
        """Basic pitch detection using autocorrelation"""
        self.logger.debug("Using basic autocorrelation for pitch detection")

        # Simple autocorrelation-based pitch detection
        frame_size = int(0.03 * sr)  # 30ms frames
        hop_size = int(0.01 * sr)     # 10ms hop

        pitches = []
        times = []

        for i in range(0, len(audio) - frame_size, hop_size):
            frame = audio[i:i+frame_size]

            # Autocorrelation
            corr = np.correlate(frame, frame, mode='full')
            corr = corr[len(corr)//2:]

            # Find first peak after zero lag
            min_lag = int(sr / settings.MAX_PITCH)
            max_lag = int(sr / settings.MIN_PITCH)

            if max_lag < len(corr):
                peak = np.argmax(corr[min_lag:max_lag]) + min_lag
                pitch = sr / peak

                if settings.MIN_PITCH < pitch < settings.MAX_PITCH:
                    pitches.append(pitch)
                    times.append(i / sr)

        return {
            'times': np.array(times),
            'pitches': np.array(pitches)
        }

    def _detect_speech_segments(self, audio: np.ndarray, sr: int, pitch_data: Dict) -> List[Tuple]:
        """Detect continuous speech segments"""
        segments = []

        if len(pitch_data['pitches']) == 0:
            return segments

        # Group consecutive pitch detections into segments
        current_segment_start = pitch_data['times'][0]
        current_pitches = [pitch_data['pitches'][0]]

        for i in range(1, len(pitch_data['times'])):
            time_gap = pitch_data['times'][i] - pitch_data['times'][i-1]

            # If gap is more than 200ms, start new segment
            if time_gap > 0.2:
                # Save previous segment
                mean_pitch = np.mean(current_pitches)
                segments.append((current_segment_start, pitch_data['times'][i-1], mean_pitch))

                # Start new segment
                current_segment_start = pitch_data['times'][i]
                current_pitches = [pitch_data['pitches'][i]]
            else:
                current_pitches.append(pitch_data['pitches'][i])

        # Add final segment
        if current_pitches:
            mean_pitch = np.mean(current_pitches)
            segments.append((current_segment_start, pitch_data['times'][-1], mean_pitch))

        return segments

    def _analyze_rhythm(self, segments: List[Tuple]) -> List[float]:
        """Analyze rhythm pattern from segments"""
        if not segments:
            return []

        # Calculate duration of each segment and gaps between them
        rhythm = []

        for i, (start, end, pitch) in enumerate(segments):
            duration = end - start
            rhythm.append(duration)

            # Add gap to next segment
            if i < len(segments) - 1:
                gap = segments[i+1][0] - end
                rhythm.append(-gap)  # Negative indicates silence

        return rhythm

    def _resample(self, audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """Simple resampling (can be improved with scipy.signal.resample)"""
        if orig_sr == target_sr:
            return audio

        # Basic linear interpolation
        duration = len(audio) / orig_sr
        target_length = int(duration * target_sr)

        indices = np.linspace(0, len(audio) - 1, target_length)
        resampled = np.interp(indices, np.arange(len(audio)), audio)

        return resampled
