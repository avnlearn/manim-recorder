from manim import *

from manim_recorder.voiceover_scene import RecorderScene
from manim_recorder.recorder.gui import RecorderService
from pathlib import Path


class VoiceRecorder(RecorderScene):
    def construct(self):
        self.set_audio_service(
            RecorderService(), cache_dir_delete=True
        )

        circle = Circle()
        square = Square().shift(2 * RIGHT)
        math = MathTex(r"x = \dfrac{-b \pm \sqrt{b^2 - 4ac}}{2a}")
        with self.voiceover(text="Say", mobject_path=math.get_file_path()) as tracker:
            self.play(Write(math), run_time=tracker.duration)

        self.play(Unwrite(math))

        with self.voiceover(text="This circle is drawn as I speak.") as tracker:
            self.play(Create(circle), run_time=tracker.duration)
        self.say_to_wait()
        with self.voiceover(text="Let's shift it to the left 2 units.") as tracker:
            self.play(circle.animate.shift(2 * LEFT),
                      run_time=tracker.duration)

        with self.voiceover(text="Thank you for watching.") as tracker:
            self.play(Uncreate(circle))

        self.wait()
