import unittest
from manim import *
from manim_recorder.voiceover_scene import RecorderScene
from example.gui_example import VoiceRecorder


class TestYourModule(unittest.TestCase):

    def test_scence_creation(self):
        scene = VoiceRecorder()
        self.assertIsInstance(scene, RecorderScene)

    def test_square_creation(self):
        # Create an instance of the scene
        scene = VoiceRecorder()

        # Run the scene to get the Mobject created
        scene.render()

        # Check if the square is created
        square = scene.mobjects[0]  # The first mobject should be the square
        self.assertIsInstance(square, Square)


if __name__ == "__main__":
    unittest.main()
