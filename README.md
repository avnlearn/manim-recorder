# Manim Recorder

If you want to structure your Bottle application in a way that separates the application logic from the main execution flow, you can create a separate class to handle the application and call it from another script. This is a good practice for organizing your code, especially as your application grows.

### Step 1: Create the Bottle Application Class

You can create a new file named `audio_recorder.py` that contains the Bottle application class. Here’s how you can structure it:

```python
# audio_recorder.py
from bottle import Bottle, run, request, static_file
import os
from datetime import datetime

class AudioRecorderApp:
    def __init__(self):
        self.app = Bottle()
        self.upload_dir = 'uploads'
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)

        self.setup_routes()

    def setup_routes(self):
        self.app.route('/', callback=self.index)
        self.app.route('/upload', method='POST', callback=self.upload)
        self.app.route('/uploads/<filename>', callback=self.serve_file)

    def index(self):
        return '''
            <html>
                <body>
                    <h1>Audio Recorder</h1>
                    <button onclick="startRecording()">Start Recording</button>
                    <button onclick="stopRecording()">Stop Recording</button>
                    <script>
                        let mediaRecorder;
                        let audioChunks = [];

                        async function startRecording() {
                            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                            mediaRecorder = new MediaRecorder(stream);
                            mediaRecorder.start();

                            mediaRecorder.ondataavailable = event => {
                                audioChunks.push(event.data);
                            };
                        }

                        function stopRecording() {
                            mediaRecorder.stop();
                            mediaRecorder.onstop = async () => {
                                const audioBlob = new Blob(audioChunks);
                                const formData = new FormData();
                                formData.append('audio', audioBlob, 'recording.wav');

                                await fetch('/upload', {
                                    method: 'POST',
                                    body: formData
                                });
                                audioChunks = [];
                            };
                        }
                    </script>
                </body>
            </html>
        '''

    def upload(self):
        audio_file = request.files.get('audio')
        if audio_file:
            now = datetime.now()
            date_str = now.strftime("%Y%m%d")
            time_str = now.strftime("%H%M%S")
            filename = f"REC_{date_str}_{time_str}.wav"
            
            file_path = os.path.join(self.upload_dir, filename)
            audio_file.save(file_path)
            return {'status': 'success', 'message': 'File uploaded successfully!', 'filename': filename}
        return {'status': 'error', 'message': 'No file uploaded.'}

    def serve_file(self, filename):
        return static_file(filename, root=self.upload_dir)

    def run(self, host='localhost', port=8080, debug=True):
        run(self.app, host=host, port=port, debug=debug)
```

### Step 2: Create the Main Script to Run the Application

Now, create another file named `main.py` that will import and run the `AudioRecorderApp` class:

```python
# main.py
from audio_recorder import AudioRecorderApp

if __name__ == '__main__':
    app = AudioRecorderApp()
    app.run()
```

### Step 3: Run the Application

To run your application, execute the `main.py` script:

```bash
python main.py
```

### Explanation

1. **AudioRecorderApp Class:** This class encapsulates the Bottle application. It initializes the app, sets up routes, and defines the methods for handling requests.
2. **Separation of Concerns:** The `main.py` script is responsible for running the application, while the `audio_recorder.py` file contains the application logic.
3. **Modularity:** This structure makes it easier to maintain and extend your application in the future.

### Testing

Open your web browser and go to `http://localhost:8080`. You should see the same audio recording interface as before, but now the application is organized into classes and separate files. This makes it easier to manage and scale your application.