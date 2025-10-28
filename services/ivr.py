"""
IVR (Interactive Voice Response) Handler
Manages the call tree and routes callers to different experiences
"""
import logging
import random
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agi_server import AGISession

from config import settings
from services.meow_generator import MeowMockeryHandler
from services.cat_personalities import TalkativeCatHandler

logger = logging.getLogger(__name__)


class IVRHandler:
    """Handles the IVR call flow and menu system"""

    def __init__(self, session: 'AGISession'):
        self.session = session
        self.logger = logging.getLogger(f"{__name__}.IVRHandler")

    def run(self):
        """Main IVR flow"""
        try:
            # Answer the call
            self.session.answer()
            self.session.verbose("Meow-Now IVR Started", 2)

            # Play welcome message and get menu choice
            choice = self.main_menu()

            if choice == "1":
                self.logger.info("Caller selected: Meow Mockery")
                self.handle_meow_mockery()
            elif choice == "2":
                self.logger.info("Caller selected: Talkative Cats")
                self.handle_talkative_cats()
            else:
                self.logger.info("No valid selection, playing default message")
                self.play_audio("goodbye")
                self.session.hangup()

        except Exception as e:
            self.logger.error(f"Error in IVR flow: {e}", exc_info=True)
            try:
                self.play_audio("error")
                self.session.hangup()
            except:
                pass

    def main_menu(self) -> str:
        """Present main menu and get caller's choice"""
        self.logger.info("Playing main menu")

        # Play welcome message and prompt for choice
        # "Welcome to Meow-Now! Press 1 for the meow mockery experience,
        #  or press 2 to hear from our talkative cats."
        prompt = self.get_audio_path("main_menu")

        if not prompt.exists():
            # Fallback: use individual prompts
            self.play_audio("welcome")
            choice = self.session.get_data("menu_prompt", timeout=5000, max_digits=1)
        else:
            choice = self.session.get_data("main_menu", timeout=5000, max_digits=1)

        self.logger.info(f"Caller pressed: {choice}")
        return choice

    def handle_meow_mockery(self):
        """Handle the meow mockery experience (Option 1)"""
        self.logger.info("Starting meow mockery handler")

        # Play instructions
        self.play_audio("meow_instructions")
        # "Get ready to be mocked by a cat! Start talking after the beep.
        #  You have 60 seconds. Press pound when finished."

        # Initialize meow mockery handler
        handler = MeowMockeryHandler(self.session)
        handler.run()

        # Say goodbye and hang up
        self.play_audio("meow_goodbye")
        self.session.hangup()

    def handle_talkative_cats(self):
        """Handle the talkative cats experience (Option 2)"""
        self.logger.info("Starting talkative cats handler")

        # Play intro
        self.play_audio("cats_intro")
        # "Connecting you to one of our talkative felines..."

        # Get a random cat personality
        handler = TalkativeCatHandler(self.session)
        handler.run()

        # Hang up (cats hang up themselves)
        self.session.hangup()

    def play_audio(self, name: str) -> bool:
        """Play an audio file by name"""
        audio_path = self.get_audio_path(name)

        if audio_path.exists():
            # Remove extension for Asterisk
            file_without_ext = str(audio_path).replace('.wav', '').replace('.gsm', '')
            self.session.stream_file(file_without_ext)
            return True
        else:
            self.logger.warning(f"Audio file not found: {audio_path}")
            return False

    def get_audio_path(self, name: str) -> Path:
        """Get full path to audio file"""
        # Try different formats
        for ext in ['.wav', '.gsm', '.ulaw']:
            path = settings.PROMPTS_DIR / f"{name}{ext}"
            if path.exists():
                return path

        # Return default wav path even if doesn't exist
        return settings.PROMPTS_DIR / f"{name}.wav"
