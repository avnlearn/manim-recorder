from bottle import Bottle, run, request, static_file, template
import os
import datetime


class WebRecorder:
    def __init__(self):
        self.app = Bottle()
        self.upload_dir = "uploads"
        self.audio_file_path = None
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)

        self.setup_routes()

    def setup_routes(self):
        self.app.route('/', callback=self.index)
        self.app.route("/static/<filepath:path>", callback=self.server_statics)
        self.app.route('/upload', method='POST', callback=self.upload)
        self.app.route('/uploads/<filename>', callback=self.serve_file)

    def index(self):
        return static_file("index.html", root=".")

    def server_statics(self, filepath):
        return static_file(filepath, root="./static")

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
                upload.save(filename)
            
            return "Audio uploaded successfully!"
        return "Failed to upload audio."

    def serve_file(self, filename):
        return static_file(filename, root=self.upload_dir)

    def run(self, host='localhost', port=8080, debug=True):
        run(self.app, host=host, port=port, debug=debug)

    


if __name__ == '__main__':
    app = WebRecorder()
    app.run()
