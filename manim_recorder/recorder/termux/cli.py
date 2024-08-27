import os
import time
import wave
import sys
import sched
import subprocess
from pathlib import Path
from manim import logger

from manim_recorder.helper import trim_silence

from pydub import AudioSegment
from manim_recorder.multimedia import Multimedia


class Recorder:
    def __init__(
        self,
        encoder: int = "acc",
        channel_count: int = None,
        sampling_rate: int = 44100,
        trim_silence_threshold: float = -40.0,
        trim_buffer_start: int = 200,
        trim_buffer_end: int = 200,
    ):
        self.encoder = encoder
        self.channel_count = channel_count
        self.sampling_rate = sampling_rate
        self.first_call = True
        self.trim_silence_threshold = trim_silence_threshold
        self.trim_buffer_start = trim_buffer_start
        self.trim_buffer_end = trim_buffer_end

    def termux_mic_rec(
        self,
        path: str,
        channel_count: str,
        sampling_rate: str,
        limit: int = 0,
        encoder: str = "acc",
    ):
        subprocess.run(
            [
                "termux-microphone-record",
                "-d",
                "-f",
                str(path),
                "-l",
                str(limit),
                "-e",
                str(encoder),
                "-r",
                str(sampling_rate),
                "-c",
                str(channel_count),
            ]
        )

    def termux_mic_stop(self):
        subprocess.run(["termux-microphone-record", "-q"])

    def termux_media_play(self, path):
        subprocess.run(["termux-media-player", "play", str(path)])
        input("[ Stop ]: Press any key to listen to the recording....")
        subprocess.run(["termux-media-player", "stop"])

    def _record(self, path):
        self.frames = []
        print("Press and hold the 'r' key to begin recording")
        if self.first_call:
            print("Wait for 1 second, then start speaking.")
            print("Wait for at least 1 second after you finish speaking.")
            print("This is to eliminate any sounds that may come from your keyboard.")
            print("The silence at the beginning and end will be trimmed automatically.")
            print(
                "You can adjust this setting using the `trim_silence_threshold` argument."
            )
            print("These instructions are only shown once.")

        print("Release the 'r' key to end recording")
        try:
            key = input("Stream active: ")[-1].lower()
            if key == "r":
                self.termux_mic_rec(
                    str(path),
                    channel_count=self.channel_count,
                    sampling_rate=self.sampling_rate,
                    encoder=self.encoder,
                )
                print("start Stream")
                input("Press any key to end recording....")
                self.termux_mic_stop()
                print("Finished recording, saving to", path)
                self.first_call = False
                logger.info(f"Saved {path}")
        except KeyboardInterrupt:
            print("KeyboardInterrupt")
            exit()
        except:
            raise

        return

    def record(self, path: str, message: str = None):

        if message is not None:
            print(message)
        self._record(path)

        while True:
            print(
                """Press...
 l to [l]isten to the recording
 r to [r]e-record
 a to [a]ccept the recording
"""
            )
            try:
                key = input()[-1].lower()
                if key == "l":
                    audio = Multimedia(path)
                    audio.Play()
                elif key == "r":
                    if message is not None:
                        print(message)
                    self._record(path)
                elif key == "a":
                    break
                else:
                    print("Invalid input")
            except KeyboardInterrupt:
                print("KeyboardInterrupt")
                exit()
