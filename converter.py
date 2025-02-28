import subprocess

def convert_avi_to_mp4(input_file="saved_video.avi", output_file="saved_video.mp4"):
    """Convert AVI to MP4 using FFmpeg."""
    try:
        command = [
            "ffmpeg",
            "-i", input_file,   # Input file
            "-vcodec", "libx264",  # Video codec
            "-crf", "23",  # Quality (Lower is better)
            "-preset", "fast",  # Encoding speed
            output_file
        ]
        subprocess.run(command, check=True)
        print(f"Conversion successful: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting video: {e}")

# Run conversion after saving the video
convert_avi_to_mp4()
