let isRecording = false;
let mediaRecorder;
let audioChunks = [];
let upload_audioChunks = [];
const progressBar = document.getElementById('progress-bar');
const toggleButton = document.getElementById('toggle-recording');
const uploadButton = document.getElementById('upload-audio');
const audioElement = document.getElementById('audio');
const waveformCanvas = document.getElementById('waveform');
const timerDisplay = document.getElementById('timer');
const waveformContext = waveformCanvas.getContext('2d');

let timerInterval;
let elapsedTime = 0;
let audioContext;
let analyser;
let dataArray;


toggleButton.addEventListener('click', async () => {
    if (isRecording) {
        mediaRecorder.stop();
        toggleButton.innerHTML = 'Start Recording';
        uploadButton.disabled = false; // Enable upload button
        clearInterval(timerInterval);
        cancelAnimationFrame(animationId); // Stop the animation
    } else {
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: true
        });

        // Create audio context and analyser
        audioContext = new(window.AudioContext || window.webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        const source = audioContext.createMediaStreamSource(stream);
        source.connect(analyser);
        analyser.fftSize = 2048; // Set FFT size
        const bufferLength = analyser.frequencyBinCount;
        dataArray = new Uint8Array(bufferLength);

        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.start();
        toggleButton.innerHTML = 'Stop Recording';
        uploadButton.disabled = true; // Disable upload button

        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, {
                type: 'audio/wav'
            });
            const audioUrl = URL.createObjectURL(audioBlob);
            audioElement.src = audioUrl;
            upload_audioChunks = audioChunks;
            // Reset audio chunks for the next recording
            audioChunks = [];
        };

        // Start drawing the waveform
        drawWaveform();

        // Update progress bar and start timer
        let progressWidth = 0;
        const interval = setInterval(() => {
            if (isRecording) {
                progressWidth += 1;
                progressBar.style.width = progressWidth + '%';
            } else {
                clearInterval(interval);
            }
        }, 1000);

        // Start timer
        elapsedTime = 0;
        timerInterval = setInterval(() => {
            elapsedTime++;
            const minutes = String(Math.floor(elapsedTime / 60)).padStart(2, '0');
            const seconds = String(elapsedTime % 60).padStart(2, '0');
            timerDisplay.textContent = `${minutes}:${seconds}`;
        }, 1000);
    }
    isRecording = !isRecording;
});

// Handle audio upload
uploadButton.addEventListener('click', async () => {

    if (upload_audioChunks.length > 0) {
        const audioBlob = new Blob(upload_audioChunks, {
            type: 'audio/wav'
        });
        const formData = new FormData();
        formData.append('audio', audioBlob, {
            type: 'audio/wav',
            name: 'recording.wav'
        });
        
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        console.log(response)
        const result = await response.text();
        alert(result); // Show upload result
        upload_audioChunks = []
    }
});

// Draw waveform in real-time
let animationId;

function drawWaveform() {
    waveformContext.clearRect(0, 0, waveformCanvas.width, waveformCanvas.height); // Clear previous drawing
    analyser.getByteTimeDomainData(dataArray); // Get the current waveform data

    waveformContext.beginPath();
    const sliceWidth = waveformCanvas.width / dataArray.length;
    let x = 0;

    // Center the waveform vertically
    const centerY = waveformCanvas.height / 2;

    for (let i = 0; i < dataArray.length; i++) {
        const v = dataArray[i] / 128.0; // Normalize to [0, 1]
        const y = centerY + (v - 1) * (waveformCanvas.height / 2); // Center the waveform
        if (i === 0) {
            waveformContext.moveTo(x, y);
        } else {
            waveformContext.lineTo(x, y);
        }
        x += sliceWidth;
    }
    waveformContext.lineTo(waveformCanvas.width, centerY);
    waveformContext.strokeStyle = '#4caf50';
    waveformContext.lineWidth = 1; // Set line width
    waveformContext.stroke();

    // Request the next animation frame
    animationId = requestAnimationFrame(drawWaveform);
}