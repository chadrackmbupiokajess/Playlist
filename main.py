import os
import sys
import subprocess
from collections import defaultdict

def find_vlc_path():
    """Tries to find the VLC executable on Windows."""
    if sys.platform != "win32":
        return "vlc" # On Linux/macOS, we assume 'vlc' is in the PATH

    possible_paths = [
        r"C:\Program Files\VideoLAN\VLC\vlc.exe",
        r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def find_and_categorize_videos(start_path):
    """
    Scans for video files and categorizes them by their parent folder's name.
    """
    categorized_videos = defaultdict(list)
    for root, dirs, files in os.walk(start_path):
        for file in files:
            if file.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')):
                full_path = os.path.join(root, file)
                category = os.path.basename(root)
                if root == start_path:
                    category = "General"
                categorized_videos[category].append(full_path)
    return categorized_videos

def play_video(filepath, vlc_path):
    """Plays a video file, trying to use VLC first."""
    try:
        # Ensure the path is in a format that the command line can handle
        formatted_path = os.path.normpath(filepath)

        if vlc_path:
            print("Attempting to launch with VLC...")
            command = [vlc_path, '--play-and-exit', '--one-instance', formatted_path]
            subprocess.Popen(command)
        elif sys.platform == "win32":
            print("VLC not found. Falling back to default player.")
            os.startfile(formatted_path)
        else:
            print("VLC not found. Falling back to default player.")
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.Popen([opener, formatted_path])
    except Exception as e:
        print(f"Error playing video: {e}")

if __name__ == "__main__":
    video_directory = "C:/Users/chadr/Videos"
    
    if not os.path.isdir(video_directory):
        print(f"The directory '{video_directory}' does not exist.")
    else:
        vlc_executable_path = find_vlc_path()
        if not vlc_executable_path and sys.platform == "win32":
             print("Warning: VLC executable not found in standard locations.")
             print(r"(C:\Program Files\VideoLAN\VLC or C:\Program Files (x86)\VideoLAN\VLC)")

        playlist = find_and_categorize_videos(video_directory)
        
        if not playlist:
            print("No video files found.")
        else:
            video_map = []
            print("--- Your Video Playlist ---")
            for category, videos in sorted(playlist.items()):
                print(f"\n[{category}]")
                for video_path in videos:
                    video_map.append(video_path)
                    video_number = len(video_map)
                    print(f"  {video_number}. {os.path.basename(video_path)}")
            print("\n-------------------------")

            while True:
                choice_str = input("Enter the number of the video to play (or 'q' to quit): ")
                if choice_str.lower() == 'q':
                    break
                
                try:
                    choice_num = int(choice_str)
                    if 1 <= choice_num <= len(video_map):
                        selected_video = video_map[choice_num - 1]
                        print(f"Playing '{os.path.basename(selected_video)}'...")
                        play_video(selected_video, vlc_executable_path)
                    else:
                        print("Invalid number. Please try again.")
                except ValueError:
                    print("That's not a valid number. Please enter a number from the list or 'q'.")
