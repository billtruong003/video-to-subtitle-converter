import os
import subprocess
import whisper
import torch
import psutil
from flask import Flask, request, redirect, url_for, render_template, send_from_directory
import platform  # Nhập module để kiểm tra hệ điều hành

app = Flask(__name__, template_folder='frontend/templates')
UPLOAD_FOLDER = 'input'
PROCESSED_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# Đặt mức sử dụng CPU tối đa cho quá trình hiện tại
p = psutil.Process(os.getpid())
p.cpu_percent()  # Khởi tạo tính toán sử dụng CPU
p.cpu_affinity([0, 1, 2, 3])  # Giới hạn sử dụng CPU cho 4 lõi đầu tiên

# Chỉ đặt mức độ ưu tiên thấp nhất nếu hệ điều hành là Windows
if platform.system() == 'Windows':
    p.nice(psutil.IDLE_PRIORITY_CLASS)  # Đặt mức độ ưu tiên thấp nhất cho Windows

def extract_audio_from_video(video_file_path, audio_file_path):
    cmd = [
        'ffmpeg', '-threads', '2', '-i', video_file_path, '-q:a', '0', '-map', 'a',
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
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = whisper.load_model(model_name, device=device)
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

def add_subtitles_with_ffmpeg(video_path, srt_path, output_path, quality):
    if not os.path.exists(srt_path):
        print(f"Subtitle file {srt_path} does not exist.")
        return

    srt_path = srt_path.replace("\\", "\\\\")
    video_path = video_path.replace("\\", "\\\\")
    output_path = output_path.replace("\\", "\\\\")

    if quality == 'high':
        resolution = '1920x1080'
        crf = '18'  # Giữ CRF ở mức thấp để đảm bảo chất lượng cao
        preset = 'slow'  # Giữ preset chậm để đảm bảo chất lượng cao
        codec = 'h264_nvenc'
    elif quality == 'medium':
        resolution = '1280x720'
        crf = '23'  # CRF trung bình
        preset = 'medium'
        codec = 'h264_nvenc'
    elif quality == 'low':
        resolution = '640x360'
        crf = '30'  # CRF cao hơn để giảm kích thước file và yêu cầu tài nguyên thấp
        preset = 'ultrafast'
        codec = 'h264_nvenc'
    else:
        resolution = '1280x720'
        crf = '23'
        preset = 'medium'
        codec = 'h264_nvenc'

    cmd = [
        'ffmpeg', '-threads', '2', '-i', video_path,
        '-vf', f"scale={resolution},subtitles='{srt_path}'",
        '-c:v', codec, '-crf', crf, '-preset', preset,
        '-c:a', 'aac', '-b:a', '128k',
        '-y', output_path
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"Subtitles added to {output_path} with resolution {resolution}")
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
            quality = request.form.get('quality')
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], 'extracted_audio.wav')

            extract_audio_from_video(file_path, audio_path)
            segments = transcribe_speech_whisper(audio_path, model_name='base', language=language)
            srt_output = os.path.join(app.config['PROCESSED_FOLDER'], 'output.srt')
            create_srt(segments, srt_output)

            video_output_path = os.path.join(app.config['PROCESSED_FOLDER'], 'output_with_subtitles.mp4')
            add_subtitles_with_ffmpeg(file_path, srt_output, video_output_path, quality)

            return redirect(url_for('download_file', filename='output_with_subtitles.mp4'))

    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

