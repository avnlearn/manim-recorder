from bottle import Bottle, run, request, static_file, template
import os
import datetime




class WebRecorder:
    def __init__(self):
        self.app = Bottle()
        

# Serve static files
@app.route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./static')

# Serve the main page


@app.route('/')
def index():
    return static_file('index.html', root='.')

# Handle audio upload


def get_filename_basename():
    now = datetime.datetime.now()
    return "Voice_{}".format(now.strftime('%d%m%Y_%H%M%S'))


@app.route('/upload', method='POST')
def upload():
    upload = request.files.get('audio')
    if upload:
        filename = get_filename_basename() + ".wav"
        upload.save(os.path.join('uploads', filename))  # Save the file
        return "Audio uploaded successfully!"
    return "Failed to upload audio."


@app.route('/uploads/<filename>')
def serve_file(filename):
    return static_file(filename, root=UPLOAD_DIR)


if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    run(app, host='localhost', port=8080)
    print("Yes")
