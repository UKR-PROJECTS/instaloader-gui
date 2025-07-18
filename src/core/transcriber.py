import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

from src.utils.lazy_imports import lazy_import_moviepy, lazy_import_whisper
from src.utils.resource_loader import get_resource_path


class AudioTranscriber:
    """
    Handles audio transcription using OpenAI's Whisper model.

    This class manages the loading of the Whisper model and the transcription
    of audio from video files, including temporary audio extraction if needed.
    """

    def __init__(self):
        """
        Initializes the AudioTranscriber.

        The Whisper model is not loaded until `load_whisper_model` is called.
        """
        self.whisper_model: Optional[Any] = None

    def load_whisper_model(self, progress_callback=None):
        """
        Loads the OpenAI Whisper model.

        The model is loaded only once. If a `progress_callback` is provided,
        it will be used to report the loading status.

        Args:
            progress_callback (callable, optional): A function to report progress.
                                                    Expected signature: (url, progress, status_message).
        """
        if self.whisper_model:
            return

        if progress_callback:
            progress_callback("", 5, "Loading Whisper model...")
        try:
            # Set path to our ffmpeg executable using absolute path
            ffmpeg_path = get_resource_path("bin/ffmpeg.exe")
            if ffmpeg_path.exists():
                # Use absolute path in environment variable
                os.environ["WHISPER_FFMPEG_PATH"] = str(ffmpeg_path.absolute())

            whisper_module = lazy_import_whisper()
            model_dir = get_resource_path("whisper")

            # Verify model file and assets exist
            model_file = model_dir / "base.pt"
            assets_dir = model_dir / "assets"

            if not model_file.exists():
                raise FileNotFoundError(f"Model file not found: {model_file}")
            if not assets_dir.exists() or not any(assets_dir.iterdir()):
                raise FileNotFoundError(
                    f"Assets directory missing or empty: {assets_dir}"
                )

            # Load the model
            self.whisper_model = whisper_module(str(model_file), device="cpu")
        except Exception as e:
            self.whisper_model = None
            error_msg = f"Whisper model load failed: {str(e)}"
            print(error_msg)  # Log to console for debugging
            if progress_callback:
                progress_callback("", 0, error_msg)

    def transcribe_audio_from_reel(
        self, reel_folder: Path, reel_number: int, result: Dict, progress_callback=None
    ):
        """
        Transcribes audio from a reel using the loaded Whisper model.

        If an audio path is not already available in `result`, it attempts to
        extract audio temporarily from the video file. The transcription text
        and path to the transcript file are added to the `result` dictionary.

        Args:
            reel_folder (Path): The folder where the reel's files are located.
            reel_number (int): The sequential number of the reel.
            result (Dict): A dictionary containing download results, which will be
                           updated with transcription information.
            progress_callback (callable, optional): A function to report progress.
                                                    Expected signature: (url, progress, status_message).
        """
        if not self.whisper_model:
            result["transcript"] = "Transcription skipped: Whisper model not loaded."
            return

        if progress_callback:
            progress_callback("", 90, "Transcribing audio...")

        audio_source = result.get("audio_path")
        temp_audio_path = None

        if not audio_source:
            audio_source, temp_audio_path = self._extract_temp_audio(
                reel_folder, reel_number, result
            )

        try:
            if not (audio_source and os.path.exists(audio_source)):
                error_msg = "Transcription failed: No audio source found."
                result["transcript"] = error_msg
                print(error_msg)
                return

            # Handle ffmpeg path for both development and frozen states
            try:
                # First try bundled ffmpeg
                ffmpeg_path = get_resource_path("bin/ffmpeg.exe")
                if not ffmpeg_path.exists():
                    # Try looking for it in the executable directory for frozen state
                    exe_dir = Path(sys.executable).parent
                    ffmpeg_path = exe_dir / "bin" / "ffmpeg.exe"
                    if not ffmpeg_path.exists():
                        raise FileNotFoundError(f"FFmpeg not found at: {ffmpeg_path}")

                # Add to PATH temporarily
                os.environ["PATH"] = f"{ffmpeg_path.parent};{os.environ['PATH']}"

                # Verify ffmpeg works
                ffmpeg_result = subprocess.run(
                    [str(ffmpeg_path), "-version"],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                if ffmpeg_result.returncode != 0:
                    raise RuntimeError(
                        f"FFmpeg failed version check: {ffmpeg_result.stderr}"
                    )

            except Exception as e:
                error_msg = f"FFmpeg setup failed: {str(e)}"
                result["transcript"] = error_msg
                print(error_msg)
                return

            # Now transcribe audio
            transcript_result = self.whisper_model.transcribe(audio_source)
            transcript_text = transcript_result["text"]
            result["transcript"] = transcript_text

            transcript_path = reel_folder / f"transcript{reel_number}.txt"
            with open(transcript_path, "w", encoding="utf-8") as f:
                f.write(transcript_text)
            result["transcript_path"] = str(transcript_path)

        except Exception as e:
            error_msg = f"Transcription failed: {str(e)}"
            result["transcript"] = error_msg
            print(error_msg)  # Log to console for debugging
            import traceback

            traceback.print_exc()  # Print full traceback

        finally:
            if temp_audio_path and os.path.exists(temp_audio_path):
                self._safe_file_removal(temp_audio_path)

    def _extract_temp_audio(self, reel_folder: Path, reel_number: int, result: Dict):
        """
        Extracts audio from a video file temporarily for transcription.

        Args:
            reel_folder (Path): The folder where the reel's files are located.
            reel_number (int): The sequential number of the reel.
            result (Dict): A dictionary containing download results.

        Returns:
            Tuple[Optional[str], Optional[str]]: A tuple containing the path to the
            extracted audio file and the path to the temporary audio file (if created).
            Returns (None, None) if extraction fails or video path is not found.
        """
        video_path = result.get("video_path") or str(
            reel_folder / f"video{reel_number}.mp4"
        )
        temp_audio_path = str(reel_folder / f"temp_audio{reel_number}.mp3")

        if not os.path.exists(video_path):
            return None, None

        video_clip = None
        audio_clip = None

        try:
            VideoFileClip = lazy_import_moviepy()
            video_clip = VideoFileClip(video_path)
            if video_clip.audio is not None:
                audio_clip = video_clip.audio
                audio_clip.write_audiofile(temp_audio_path, verbose=False, logger=None)
                return temp_audio_path, temp_audio_path

        except Exception:
            # Log the error if a proper logging mechanism is in place
            pass

        finally:
            self._cleanup_video_resources(audio_clip, video_clip)

        return None, None

    def _cleanup_video_resources(self, audio_clip, video_clip):
        """
        Safely closes and cleans up moviepy video and audio clip resources.

        Args:
            audio_clip: The audio clip object to close.
            video_clip: The video clip object to close.
        """
        if audio_clip:
            try:
                audio_clip.close()
            except Exception:
                pass

        if video_clip:
            try:
                video_clip.close()
            except Exception:
                pass

    def _safe_file_removal(self, file_path: str):
        """
        Safely removes a file from the filesystem.

        Args:
            file_path (str): The path to the file to be removed.
        """
        try:
            os.remove(file_path)
        except OSError:
            # Log the error if a proper logging mechanism is in place
            pass
