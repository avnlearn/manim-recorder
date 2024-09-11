from manim import *

from manim_recorder.voiceover_scene import RecorderScene
from manim_recorder.recorder.gui import RecorderService
from pathlib import Path


class VoiceRecorder(RecorderScene):
    def construct(self):
        self.set_audio_service(RecorderService(), cache_dir_delete=True)
        # self.set_audio_service(RecorderService())

        circle = Circle()
        square = Square().shift(2 * RIGHT)
        math = MathTex(r"x = \dfrac{-b \pm \sqrt{b^2 - 4ac}}{2a}")

        with self.voiceover(
            "भारत के दस सबसे अधिक प्रतिभाशाली लेखक यह हमलोग नहीं जानना सकते है कि भुत्तकल(Past) में बहुत सारे लिखका हुए जो प्रतिभाशाली थे और आने वाले भाभिष्य कल (Future) में प्रतिभाशाली लेखक होगे। यह हम कुछ लेखको को देखेगे।, इसलिए लिखेगे"
        ) as tracker:
            self.play(Write(math), run_time=tracker.duration)

        self.play(Unwrite(math))

        with self.voiceover(math) as tracker:
            self.play(Write(math), run_time=tracker.duration)

        self.play(Unwrite(math))

        with self.voiceover(text="This circle is drawn as I speak.") as tracker:
            self.play(Create(circle), run_time=tracker.duration)
        self.say_to_wait()
        with self.voiceover(text="Let's shift it to the left 2 units.") as tracker:
            self.play(circle.animate.shift(2 * LEFT), run_time=tracker.duration)

        with self.voiceover(text="Thank you for watching.") as tracker:
            self.play(Uncreate(circle))

        self.wait()
