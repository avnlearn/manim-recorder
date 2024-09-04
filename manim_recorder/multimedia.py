"""
multimedia for manim-recorder
"""
import uuid
import platform
import os
import sys
import threading
import wave
import subprocess
import time
from pathlib import Path
import sox
import pyaudio
from pydub.utils import mediainfo
from mutagen.mp3 import MP3
from pydub import AudioSegment
from pydub.playback import play
from manim import logger


def Check_os():
    os_name = platform.system()
    match os_name:
        case "Linux":
            # Check for Termux by looking for the presence of the 'termux' directory
            if os.path.exists("/data/data/com.termux"):
                # if 'TERMUX_VERSION' in os.environ:
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
        """
        Cross Media Player
        """
        match Check_os():
            case "Termux (Android)":
                self.Termux_Media_Play()
                input("[ Stop ]: Press any key to listen to the recording....")
                self.Termux_Media_Stop()
            case "Linux" | "macOS" | "Windows":
                audio = AudioSegment.from_file(self.path)
                play(audio)

    def Termux_Media_Play(self):
        """
        Termux-media-player access is play
        """
        subprocess.run(["termux-media-player", "play", str(self.path)])

    def Termux_Media_Stop(self):
        """
        Termux-media-player access is stop
        """
        subprocess.run(["termux-media-player", "stop"])


class Pyaudio_Recorder:
    """
    Using pyaudio controlling class
    """

    def __init__(
        self,
        format: int = pyaudio.paInt16,
        channels: int = 1 if sys.platform == "darwin" else 2,
        rate: int = 44100,
        chunk: int = 1024,
        device_index: int = None,
        # callback_delay: float = 0.05,
        file_path: str = "output.wav",
        **kwargs,
    ):
        """
        """
        self.format = format
        self.channels = channels
        self.rate = rate
        self.chunk = chunk
        self.device_index = device_index
        self.frames = []
        self.is_recording = False
        self.is_paused = False
        self.lock = threading.Lock()
        self.p = pyaudio.PyAudio()
        self.file_path = file_path
        self.playback_thread = None
        self.stop_playback_event = threading.Event()
        self.is_playing = False

    def set_device_index(self, device_index) -> None:
        """
        """
        try:
            self.p.get_device_info_by_host_api_device_index(0, device_index)
            return True
        except Exception as e:
            print("Invalid device index. Please try again. ", e)
            return False

    def set_channels(self, channels: int = None) -> None:
        """
        """
        if channels is None:
            channels = self.device_index
        try:
            print("Channels : ", channels)
            self.channels = self.p.get_device_info_by_host_api_device_index(
                0, channels
            ).get("maxInputChannels")
            return True
        except Exception as e:
            print("Invalid device index. Please try again.", e)
            return False

    def get_device_count(self) -> None:
        """
        """
        return self.p.get_host_api_info_by_index(0).get("deviceCount")

    def get_devices_name(self) -> None:
        """
        """
        return [
            self.p.get_device_info_by_host_api_device_index(0, i).get("name")
            for i in range(0, self.get_device_count())
            if self.p.get_device_info_by_host_api_device_index(0, i).get(
                "maxInputChannels"
            )
            > 0
        ]

    def start_recording(self) -> None:
        """
        """
        self.frames = []
        self.is_recording = True
        self.is_paused = False
        self.thread = threading.Thread(target=self._record)
        self.thread.start()

    def _record(self) -> None:
        """
        """
        stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk,
            input_device_index=self.device_index,
        )

        while self.is_recording:
            if not self.is_paused:
                data = stream.read(self.chunk)
                with self.lock:
                    print(data)
                    self.frames.append(data)

        stream.stop_stream()
        stream.close()

    def pause_recording(self) -> None:
        """
        """
        self.is_paused = True

    def resume_recording(self) -> None:
        """
        """
        self.is_paused = False

    def stop_recording(self) -> None:
        """
        """
        self.is_recording = False
        self.thread.join()

    def save_recording(self) -> None:
        """
        """
        with wave.open(self.file_path, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.rate)
            wf.writeframes(b"".join(self.frames))

    def play_playback(self) -> None:
        """
        """
        if not self.frames:
            return False
        self.is_playing = True
        self.stop_playback_event.clear()  # Clear the stop event

        self.playback_thread = threading.Thread(target=self._playback)
        self.playback_thread.start()

    def _playback(self) -> None:
        """
        """
        stream = self.p.open(
            format=self.format, channels=self.channels, rate=self.rate, output=True
        )

        for data in self.frames:
            if self.stop_playback_event.is_set():
                break
            stream.write(data)

        stream.stop_stream()
        stream.close()

    def stop_playback(self) -> None:
        """
        """
        self.is_playing = False
        self.stop_playback_event.set()  # Signal to stop playback
        if self.playback_thread is not None:
            self.playback_thread.join()  # Wait for the playback thread to finish

    def close(self) -> None:
        """
        """
        self.p.terminate()

    def get_duration(self) -> int:
        """
        """
        if not self.frames:
            return 0
        return len(self.frames) * self.chunk / self.rate

    def format_duration(self) -> str:
        """
        """
        struct_time = time.gmtime(self.get_duration())
        return time.strftime("%H:%M:%S", struct_time)

    def set_filepath(self, path: str):
        """
        """
        self.file_path = str(path)

    def __str__(self) -> str:
        """
        """
        if isinstance(self.file_path):
            if os.path.exists(str(self.file_path)):
                return str(self.file_path)
        return ""


def adjust_speed(input_path: str, output_path: str, tempo: float) -> None:
    """
    """
    same_destination = False
    if input_path == output_path:
        same_destination = True
        path_, ext = os.path.splitext(input_path)
        output_path = path_ + str(uuid.uuid1()) + ext

    tfm = sox.Transformer()
    tfm.tempo(tempo)
    tfm.build(input_filepath=input_path, output_filepath=output_path)
    if same_destination:
        os.rename(output_path, input_path)


def get_duration(path: str) -> float:
    """
    """
    # Create a Path object
    file_path = Path(path)

    # Use match-case to check the file extension
    match file_path.suffix.lower():
        case ".mp3":
            audio = MP3(path)
            return audio.info.length
        case ".m4a":
            audio = mediainfo(path)
            return float(audio["duration"])
        case ".wav":
            with wave.open(str(path), "rb") as wav_file:
                return wav_file.getnframes() / wav_file.getframerate()
        case _:
            return False


def chunks(lst: list, n: int):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i: i + n]


def wav2mp3(wav_path, mp3_path=None, remove_wav=True, bitrate="312k"):
    """Convert wav file to mp3 file"""

    if mp3_path is None:
        mp3_path = Path(wav_path).with_suffix(".mp3")

    # Convert to mp3
    AudioSegment.from_wav(wav_path).export(
        mp3_path, format="mp3", bitrate=bitrate)

    if remove_wav:
        # Remove the .wav file
        os.remove(wav_path)
    logger.info(f"Saved {mp3_path}")
    return


def detect_leading_silence(sound, silence_threshold=-20.0, chunk_size=10):
    """
    sound is a pydub.AudioSegment
    silence_threshold in dB
    chunk_size in ms

    iterate over chunks until you find the first one with sound
    """
    trim_ms = 0  # ms

    assert chunk_size > 0  # to avoid infinite loop
    while sound[
        trim_ms: trim_ms + chunk_size
    ].dBFS < silence_threshold and trim_ms < len(sound):
        trim_ms += chunk_size

    return trim_ms


def trim_silence(
    sound: AudioSegment,
    silence_threshold=-40.0,
    chunk_size=5,
    buffer_start=200,
    buffer_end=200,
) -> AudioSegment:
    """
    """
    start_trim = detect_leading_silence(sound, silence_threshold, chunk_size)
    end_trim = detect_leading_silence(
        sound.reverse(), silence_threshold, chunk_size)

    # Remove buffer_len milliseconds from start_trim and end_trim
    start_trim = max(0, start_trim - buffer_start)
    end_trim = max(0, end_trim - buffer_end)

    duration = len(sound)
    trimmed_sound = sound[start_trim: duration - end_trim]
    return trimmed_sound
