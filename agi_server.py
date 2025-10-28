"""
AGI (Asterisk Gateway Interface) Server
Handles incoming calls from Asterisk and routes them through the IVR system
"""
import socket
import threading
import logging
from typing import Optional, Dict
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import settings
from services.ivr import IVRHandler

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AGISession:
    """Handles a single AGI session with Asterisk"""

    def __init__(self, socket_conn: socket.socket):
        self.socket = socket_conn
        self.env: Dict[str, str] = {}
        self.logger = logging.getLogger(f"{__name__}.AGISession")

    def read_env(self):
        """Read AGI environment variables from Asterisk"""
        while True:
            line = self.socket.recv(1024).decode('utf-8').strip()
            if not line:
                break
            if ':' in line:
                key, value = line.split(':', 1)
                self.env[key.strip()] = value.strip()
            self.logger.debug(f"ENV: {line}")

        self.logger.info(f"Call from: {self.env.get('agi_callerid', 'Unknown')}")

    def send_command(self, command: str) -> str:
        """Send AGI command to Asterisk and get response"""
        self.logger.debug(f"Sending: {command}")
        self.socket.send(f"{command}\n".encode('utf-8'))

        response = self.socket.recv(1024).decode('utf-8').strip()
        self.logger.debug(f"Response: {response}")
        return response

    def answer(self):
        """Answer the call"""
        return self.send_command("ANSWER")

    def stream_file(self, filename: str, escape_digits: str = "") -> str:
        """Play an audio file"""
        # Remove file extension if present
        filename = filename.replace('.wav', '').replace('.gsm', '')
        return self.send_command(f'STREAM FILE "{filename}" "{escape_digits}"')

    def get_data(self, filename: str, timeout: int = 5000, max_digits: int = 1) -> str:
        """Play a file and get DTMF input"""
        filename = filename.replace('.wav', '').replace('.gsm', '')
        response = self.send_command(f'GET DATA "{filename}" {timeout} {max_digits}')

        # Parse response: "200 result=<digits>"
        if 'result=' in response:
            digits = response.split('result=')[1].split()[0]
            return digits
        return ""

    def record_file(self, filename: str, format: str = "wav", escape_digits: str = "#",
                   timeout: int = -1, offset: int = 0, beep: bool = True,
                   silence: int = 3) -> str:
        """Record audio from caller"""
        beep_flag = "beep" if beep else ""
        cmd = f'RECORD FILE "{filename}" {format} "{escape_digits}" {timeout} {offset} {beep_flag} s={silence}'
        return self.send_command(cmd)

    def say_number(self, number: int, escape_digits: str = "") -> str:
        """Speak a number"""
        return self.send_command(f'SAY NUMBER {number} "{escape_digits}"')

    def hangup(self):
        """Hang up the call"""
        return self.send_command("HANGUP")

    def set_variable(self, name: str, value: str):
        """Set a channel variable"""
        return self.send_command(f'SET VARIABLE {name} "{value}"')

    def get_variable(self, name: str) -> str:
        """Get a channel variable"""
        response = self.send_command(f'GET VARIABLE {name}')
        if 'result=' in response:
            return response.split('result=')[1].strip('()')
        return ""

    def verbose(self, message: str, level: int = 1):
        """Log a verbose message in Asterisk"""
        return self.send_command(f'VERBOSE "{message}" {level}')


class AGIServer:
    """AGI server that listens for connections from Asterisk"""

    def __init__(self, host: str = settings.AGI_HOST, port: int = settings.AGI_PORT):
        self.host = host
        self.port = port
        self.server_socket: Optional[socket.socket] = None
        self.logger = logging.getLogger(__name__)
        self.running = False

    def handle_call(self, client_socket: socket.socket, address: tuple):
        """Handle an incoming call"""
        self.logger.info(f"New connection from {address}")

        try:
            session = AGISession(client_socket)
            session.read_env()

            # Create IVR handler and process the call
            ivr = IVRHandler(session)
            ivr.run()

        except Exception as e:
            self.logger.error(f"Error handling call: {e}", exc_info=True)
        finally:
            try:
                client_socket.close()
            except:
                pass
            self.logger.info(f"Connection closed from {address}")

    def start(self):
        """Start the AGI server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True

            self.logger.info(f"AGI Server listening on {self.host}:{self.port}")

            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()

                    # Handle each call in a separate thread
                    thread = threading.Thread(
                        target=self.handle_call,
                        args=(client_socket, address)
                    )
                    thread.daemon = True
                    thread.start()

                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        self.logger.error(f"Error accepting connection: {e}")

        except KeyboardInterrupt:
            self.logger.info("Shutting down AGI server...")
        finally:
            self.stop()

    def stop(self):
        """Stop the AGI server"""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        self.logger.info("AGI Server stopped")


if __name__ == "__main__":
    server = AGIServer()
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
