from pydub import AudioSegment
from pydub.playback import play
import platform
import os


def Check_OS():
    os_name = platform.system()
    match os_name:
        case "Linux":
            if "termux" in os.environ.get("TERM", ''):
                return "Termux (Android)"
            else:
                return "Linux"
        case "Darwin":
            return "macOS"
        case "Windows":
            return "Windows"
        case _:
            return "Unknown OS"


class Multimedia:
    def __init__(self, path):
        self.path = path

    def Play(self):
        match Check_OS():
            case "Termux (Android)":
                self.Termux_Media_Play()
                input("[ Stop ]: Press any key to listen to the recording....")
                self.Termux_Media_Stop()
            case "Linux" | "macOS" | "Windows":
                audio = AudioSegment.from_file(self.path)
                play(audio)

    
    def Termux_Media_Play(self):
        subprocess.run(["termux-media-player", "play", str(self.path)])

    def Termux_Media_Stop(self):
        subprocess.run(["termux-media-player", "stop"])
