import subprocess


def Run_Audacity(audio_path):
    try:
        # Run the dpkg command to check if the package is installed
        subprocess.run(['audacity', str(audio_path)],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False
