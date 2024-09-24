from flask import Flask, render_template, request, send_file
from gtts import gTTS
import os
import speech_recognition as sr
from googletrans import Translator
from moviepy.editor import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dub', methods=['POST'])
def dub():
    #wav_File = request.form.get('wavFile')
    target_language = request.form.get('language')
    video_File=request.form.get('videoFile')

    video_clip = VideoFileClip(video_File)
    audio_clip = video_clip.audio

    # Save the audio as WAV file
    audio_clip.write_audiofile('harvard.wav', codec='pcm_s16le', ffmpeg_params=["-ac", "1"])

    # Close the clips
    video_clip.close()
    audio_clip.close()
    recognizer = sr.Recognizer()

    # Load the audio file
    audio_clip = sr.AudioFile('harvard.wav')

    # Use Google Web Speech API to recognize the audio
    with audio_clip as source:
        print("Transcribing audio...")
        audio = recognizer.record(source)

    # Recognize the speech using Google Web Speech API
    text = recognizer.recognize_google(audio, language="en-US")
    print("Transcription:")
    print(text)
    translator = Translator()
    # Translate the text to the specified target language
    translation = translator.translate(text, dest=target_language)
    textinfo=translation.text
    tts = gTTS(text=textinfo, lang=target_language, slow=False)
    # Save the speech as an audio file
    tts.save("output_audio.mp3")
    video_clip = VideoFileClip(video_File)

    # Load the new audio clip
    new_audio_clip = AudioFileClip("output_audio.mp3")

    # Set the audio of the video clip to the new audio
    video_clip = video_clip.set_audio(new_audio_clip)
    # Write the video with the new audio to the output file
    video_clip.write_videofile('videofile.mp4', codec="libx264", audio_codec="aac")

    # Close the clips
    video_clip.close()
    new_audio_clip.close()
    return send_file("videofile.mp4", as_attachment=True)

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=5000, workers=4)
