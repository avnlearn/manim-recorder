from pprint import pp
from manim import *
from manim_recorder.voiceover_scene import RecorderScene
from manim_recorder.recorder.gui import RecorderService
from pathlib import Path


class VoiceRecorder(RecorderScene):
    def construct(self):
        # self.set_audio_service(RecorderService(), cache_dir_delete=True, skip=True)
        self.set_audio_service(RecorderService(), cache_dir_delete=True)
        # self.set_audio_service(RecorderService())

        circle = Circle()
        square = Square().shift(2 * RIGHT)
        math = MathTex(r"x = \dfrac{-b \pm \sqrt{b^2 - 4ac}}{2a}")
        m = VGroup(circle, square, math)
        # self.say_to_image_play(Create(circle))
        # self.say_to_image_play(Uncreate(circle))
        # self.say_to_image_play(Write(math))
        # self.say_to_image_play(Unwrite(math))
        self.say_to_image_play(Write(m))
        # print(Write(m).get_all_mobjects())
        # self.say_to_play_image(Create(circle))
        # self.say_to_image_play(Create(circle))

        self.wait()


if __name__ == "__main__":
    scene = VoiceRecorder()
    scene.render()
