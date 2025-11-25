import subprocess, os

def play_wav(filename: str) -> None:
    base_dir = os.path.dirname(__file__)
    sound_path = os.path.join(base_dir, "sounds", filename)
    subprocess.run(["aplay", sound_path])