from mutagen.mp3 import MP3
from pydub import AudioSegment
from pathlib import Path

in_file = "media/recordings/Recordering/Voice_26082024_045423.wav"
in_file = Path(in_file)
out_file = in_file.with_suffix(".mp3")
AudioSegment.from_wav(in_file).export(out_file, bitrate="312k")
audio = MP3(out_file)
print(audio.info.length)
