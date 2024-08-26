from manim import *
# from manim_recorder import VoiceoverScene
from manim_recorder import RecorderScene
# from manim_recorder.services.recorder import RecorderService
from manim_recorder.recorder.pynput import RecorderService
from pathlib import Path


class Recordering(RecorderScene):
    def construct(self):
        self.set_speech_service(
            RecorderService(
                device_index=0,
            )
        )

        circle = Circle()
        square = Square().shift(2 * RIGHT)
        with self.voiceover(text="This circle is drawn as I speak.") as tracker:
            print(tracker.duration, tracker.cache_dir)
            self.play(Create(circle), run_time=tracker.duration)

        with self.voiceover(text="Let's shift it to the left 2 units.") as tracker:
            print(tracker.duration)
            self.play(circle.animate.shift(2 * LEFT),
                      run_time=tracker.duration)

        with self.voiceover(text="Thank you for watching.") as tracker:
            print(tracker.duration)
            self.play(Uncreate(circle), run_time=tracker.duration)

        self.wait()
