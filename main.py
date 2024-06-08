import os
import subprocess
import whisper
from flask import Flask, request, redirect, url_for, render_template, send_from_directory

app = Flask(__name__, template_folder='frontend/templates')
UPLOAD_FOLDER = 'input'
PROCESSED_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

def extract_audio_from_video(video_file_path, audio_file_path):
    cmd = [
        'ffmpeg', '-i', video_file_path, '-q:a', '0', '-map', 'a',
        '-y', audio_file_path
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"Audio extracted to {audio_file_path}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Ensure that ffmpeg is installed and added to your PATH.")
    except subprocess.CalledProcessError as e:
        print(f"Error during audio extraction: {e}")

def transcribe_speech_whisper(audio_file_path, model_name='base', language='en'):
    model = whisper.load_model(model_name)
    result = model.transcribe(audio_file_path, language=language)
    segments = result['segments']
    print("Transcription completed.")
    return segments

def create_srt(segments, output_srt_file):
    if not segments:
        print("No content to write to SRT.")
        return
    
    with open(output_srt_file, 'w', encoding='utf-8') as file:
        for i, segment in enumerate(segments):
            start_time = segment['start']
            end_time = segment['end']
            text = segment['text'].strip()

            start_time_formatted = format_time(start_time)
            end_time_formatted = format_time(end_time)

            file.write(f"{i+1}\n")
            file.write(f"{start_time_formatted} --> {end_time_formatted}\n")
            file.write(f"{text}\n\n")
    print(f"SRT file created at {output_srt_file}")

def format_time(seconds):
    milliseconds = int((seconds % 1) * 1000)
    seconds = int(seconds)
    minutes = seconds // 60
    seconds = seconds % 60
    hours = minutes // 60
    minutes = minutes % 60
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def add_subtitles_with_ffmpeg(video_path, srt_path, output_path):
    if not os.path.exists(srt_path):
        print(f"Subtitle file {srt_path} does not exist.")
        return

    if os.path.exists(output_path):
        srt_path = srt_path.replace("\\", "\\\\")
        video_path = video_path.replace("\\", "\\\\")
        output_path = output_path.replace("\\", "\\\\")

    cmd = [
        'ffmpeg', '-i', video_path,
        '-vf', f"subtitles='{srt_path}'",
        '-c:v', 'libx264', '-crf', '23', '-preset', 'fast',
        '-c:a', 'aac', '-b:a', '128k',
        '-y', output_path
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"Subtitles added to {output_path}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Ensure that ffmpeg is installed and added to your PATH.")
    except subprocess.CalledProcessError as e:
        print(f"Error during subtitle addition: {e}")

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            language = request.form.get('language')
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], 'extracted_audio.wav')

            extract_audio_from_video(file_path, audio_path)
            segments = transcribe_speech_whisper(audio_path, model_name='base', language=language)
            srt_output = os.path.join(app.config['PROCESSED_FOLDER'], 'output.srt')
            create_srt(segments, srt_output)

            video_output_path = os.path.join(app.config['PROCESSED_FOLDER'], 'output_with_subtitles.mp4')
            add_subtitles_with_ffmpeg(file_path, srt_output, video_output_path)

            return redirect(url_for('download_file', filename='output_with_subtitles.mp4'))

    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
