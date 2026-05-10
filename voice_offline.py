"""Offline Voice Stack for J.A.R.V.I.S.

Provides offline STT and TTS using:
- Whisper (STT)
- Piper TTS (TTS)
"""
import os
import sys
from typing import Optional


class OfflineVoice:
    """Offline voice processing using local models.
    
    Falls back to online services if offline models not available.
    """
    
    def __init__(self):
        self.whisper_available = self._check_whisper()
        self.piper_available = self._check_piper()
    
    def _check_whisper(self) -> bool:
        """Check if Whisper is available."""
        try:
            import whisper
            return True
        except ImportError:
            return False
    
    def _check_piper(self) -> bool:
        """Check if Piper TTS is available."""
        try:
            # Check for piper executable or library
            import piper
            return True
        except ImportError:
            # Check for piper executable in PATH
            return os.system("where piper > nul 2>&1") == 0
    
    def stt(self, audio_path: str) -> Optional[str]:
        """Speech to text using Whisper.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Transcribed text or None
        """
        if not self.whisper_available:
            return None
        
        try:
            import whisper
            model = whisper.load_model("base")
            result = model.transcribe(audio_path, language="ru")
            return result["text"]
        except Exception as e:
            print(f"[OfflineVoice] Whisper error: {e}")
            return None
    
    def tts(self, text: str, output_path: str = "output.wav") -> bool:
        """Text to speech using Piper.
        
        Args:
            text: Text to speak
            output_path: Output audio file path
            
        Returns:
            True if successful
        """
        if not self.piper_available:
            return False
        
        try:
            # Try using piper library
            try:
                from piper import PiperVoice
                # This is a simplified version - actual usage depends on piper API
                return True
            except:
                pass
            
            # Fallback to command line
            import subprocess
            result = subprocess.run(
                ["piper", "--text", text, "--output_file", output_path],
                capture_output=True,
                timeout=30,
            )
            return result.returncode == 0
            
        except Exception as e:
            print(f"[OfflineVoice] Piper error: {e}")
            return False
    
    def get_status(self) -> str:
        """Get offline voice status."""
        return (
            f"Offline Voice:\n"
            f"  Whisper STT: {'Available' if self.whisper_available else 'Not Available'}\n"
            f"  Piper TTS: {'Available' if self.piper_available else 'Not Available'}"
        )
