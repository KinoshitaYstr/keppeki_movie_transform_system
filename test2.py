import pydub
from pydub import AudioSegment

base_sound = AudioSegment.from_file("a.mp4", format="mp4")
print(base_sound)
print("sound length : ", base_sound.duration_seconds)
base_sound.export("aa.mp3")