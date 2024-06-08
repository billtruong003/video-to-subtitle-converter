import os
import subprocess
import whisper

# Hàm trích xuất âm thanh từ video
def extract_audio_from_video(video_file_path, audio_file_path):
    cmd = [
        'ffmpeg', '-i', video_file_path, '-q:a', '0', '-map', 'a',
        '-y', audio_file_path  # Ghi đè file hiện tại
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"Audio extracted to {audio_file_path}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Ensure that ffmpeg is installed and added to your PATH.")
    except subprocess.CalledProcessError as e:
        print(f"Error during audio extraction: {e}")

# Hàm sử dụng Whisper để nhận diện giọng nói từ file âm thanh
def transcribe_speech_whisper(audio_file_path, model_name='base', language='en'):
    model = whisper.load_model(model_name)
    result = model.transcribe(audio_file_path, language=language)
    segments = result['segments']
    print("Transcription completed.")
    return segments

# Hàm tạo file phụ đề SRT
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

# Hàm định dạng thời gian
def format_time(seconds):
    milliseconds = int((seconds % 1) * 1000)
    seconds = int(seconds)
    minutes = seconds // 60
    seconds = seconds % 60
    hours = minutes // 60
    minutes = minutes % 60
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

# Hàm thêm phụ đề vào video
def add_subtitles_with_ffmpeg(video_path, srt_path, output_path):
    if not os.path.exists(srt_path):
        print(f"Subtitle file {srt_path} does not exist.")
        return

    if os.path.exists(output_path):
        print(f"Output file {output_path} already exists. Overwrite? [y/N]")
        response = input().strip().lower()
        if response != 'y':
            print("Not overwriting - exiting.")
            return

    cmd = [
        'ffmpeg', '-i', video_path,
        '-vf', f"subtitles={srt_path}",
        '-s', '1280x720',  # Rescale video to 720p
        '-c:v', 'libx264', '-crf', '23', '-preset', 'fast',
        '-c:a', 'aac', '-b:a', '128k',
        output_path
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"Subtitles added to {output_path}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Ensure that ffmpeg is installed and added to your PATH.")
    except subprocess.CalledProcessError as e:
        print(f"Error during subtitle addition: {e}")

# Sử dụng ví dụ
video_path = 'video.mp4'  # Đường dẫn đến file video
audio_path = 'extracted_audio.wav'  # Đường dẫn đến file âm thanh trích xuất
srt_output = 'output.srt'
video_output = 'output_with_subtitles.mp4'

# Bước 1: Trích xuất âm thanh từ file video
extract_audio_from_video(video_path, audio_path)

# Bước 2: Nhận diện giọng nói từ file âm thanh bằng Whisper
segments = transcribe_speech_whisper(audio_path, model_name='base', language='vi')
print("Segments:", segments)

# Bước 3: Tạo file phụ đề SRT từ các đoạn nhận diện
if segments:
    create_srt(segments, srt_output)
    # Bước 4: Thêm phụ đề vào video
    add_subtitles_with_ffmpeg(video_path, srt_output, video_output)
else:
    print("No transcription available for creating subtitles.")
