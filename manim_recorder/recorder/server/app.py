from bottle import Bottle, run, request, static_file, template
import os
import datetime
import threading
import signal


class WebRecorder:
    def __init__(self, package_dir):
        self.app = Bottle()
        self.package_dir = package_dir
        self.root_dir = os.path.join(
            package_dir, "manim_recorder", "recorder", "server")
        self.upload_dir = "uploads"
        print(self.root_dir)
        self.audio_file_path = None
        self.shutdown_event = threading.Event()
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)

        self.setup_routes()

    def setup_routes(self):
        self.app.route('/', callback=self.index)
        self.app.route("/static/<filepath:path>", callback=self.server_statics)
        self.app.route('/upload', method='POST', callback=self.upload)
        self.app.route('/uploads/<filename>', callback=self.serve_file)

    def index(self):
        return static_file("index.html", root=self.root_dir)

    def server_statics(self, filepath):
        return static_file(filepath, root="{}/static".format(self.root_dir))

    def get_filename_basename(self):
        now = datetime.datetime.now()
        return "Voice_{}".format(now.strftime('%d%m%Y_%H%M%S'))

    def upload(self):
        upload = request.files.get("audio")
        if upload:
            # Save the file
            if self.audio_file_path is None:
                filename = self.get_filename_basename() + ".wav"
                upload.save(os.path.join(self.upload_dir, filename))
            else:
                filename = self.audio_file_path
                if os.path.exists(filename):
                    os.remove(filename)
                upload.save(filename)
            self.shutdown_event.set()  # Signal to shut down the server
            return "Audio uploaded successfully!"
        return "Failed to upload audio."

    def serve_file(self, filename):
        return static_file(filename, root=str(os.path.join(self.root_dir, self.upload_dir)))

    def run(self, host='localhost', port=8080, debug=True):
        run(self.app, host=host, port=port, debug=debug)
        

    def record(self, audio_file_path: str, msg: str = None):
        self.audio_file_path = audio_file_path
        server_thread = threading.Thread(target=self.run, daemon=True)
        server_thread.start()

        # Wait for the shutdown event to be set
        self.shutdown_event.wait()
        print("Yes")
        server_thread.join()
        print("Yes")
        return self.audio_file_path


if __name__ == '__main__':
    app = WebRecorder("/home/mrlinux/Documents/manim-recorder")
    path_audio = app.record("/home/mrlinux/Documents/manim-recorder/media/recordings/VoiceRecorder/Voice_02092024_143652.wav")
    print(f"Saved, {path_audio}")
    path_audio = app.record("/home/mrlinux/Documents/manim-recorder/media/recordings/VoiceRecorder/Voice_02092024_143654.wav")
    print(f"Saved, {path_audio}")
    path_audio = app.record("/home/mrlinux/Documents/manim-recorder/media/recordings/VoiceRecorder/Voice_02092024_143658.wav")
    print(f"Saved, {path_audio}")
    path_audio = app.record("/home/mrlinux/Documents/manim-recorder/media/recordings/VoiceRecorder/Voice_02092024_143656.wav")
    print(f"Saved, {path_audio}")
