# Video to Subtitle Converter

This project provides a tool to extract audio from a video, transcribe the speech to text using Whisper, and add subtitles to the video. The tool is built using Flask for the web interface and ffmpeg for audio extraction and video processing.

## Features

- Extract audio from a video file
- Transcribe speech to text using Whisper
- Generate SRT files from transcribed text
- Add subtitles to the video

## Installation

### Prerequisites

- Python 3.7 or higher
- ffmpeg installed and added to your PATH (instructions below)

### Steps

1. Clone the repository:

    ```bash
    git clone https://github.com/billtruong003/video-to-subtitle-converter.git
    cd video-to-subtitle-converter
    ```

2. Install the required Python libraries:

    ```bash
    pip install -r requirements.txt
    ```

3. Install ffmpeg and ensure it is added to your PATH:

    #### Windows:

    1. Download the latest ffmpeg release from the [official website](https://ffmpeg.org/download.html).
    2. Extract the downloaded zip file to a directory of your choice, e.g., `C:\ffmpeg`.
    3. Add the `bin` folder to your system's PATH:
       - Search for "Environment Variables" in the Windows search bar.
       - Click "Edit the system environment variables."
       - In the "System Properties" window, click the "Environment Variables" button.
       - In the "Environment Variables" window, find the `Path` variable in the "System variables" section, and click "Edit."
       - Click "New" and add the path to the `bin` folder inside your ffmpeg directory (e.g., `C:\ffmpeg\bin`).
       - Click "OK" to close all windows.
    4. Open a new command prompt and type `ffmpeg -version` to verify the installation.

    #### macOS:

    1. Install Homebrew if it is not already installed:
        ```bash
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        ```

    2. Use Homebrew to install ffmpeg:
        ```bash
        brew install ffmpeg
        ```

    3. Verify the installation by typing `ffmpeg -version` in your terminal.

    #### Linux (Ubuntu):

    1. Open a terminal and update your package list:
        ```bash
        sudo apt update
        ```

    2. Install ffmpeg:
        ```bash
        sudo apt install ffmpeg
        ```

    3. Verify the installation by typing `ffmpeg -version` in your terminal.

4. Verify `ffmpeg` is installed and accessible from the command line by running:

    ```bash
    ffmpeg -version
    ```

## Usage

1. Run the Flask app:

    ```bash
    python app.py
    ```

2. Open your web browser and navigate to `http://localhost:5000`.

3. Upload a video file and select the language for transcription.

4. The application will extract audio, transcribe it, and generate subtitles. You can download the video with subtitles after processing.

## File Structure

- `main.py`: The main application file that contains the Flask routes and functions for processing video and audio.
- `frontend/templates/index.html`: The HTML template for the file upload interface.
- `requirements.txt`: List of Python dependencies.
- `LICENSE`: License file for the project.
- `README.md`: This readme file.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add some feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Open a pull request.

## Acknowledgements

- [Whisper](https://github.com/openai/whisper): Speech-to-text transcription library.
- [FFmpeg](https://ffmpeg.org/): Audio and video processing tool.
