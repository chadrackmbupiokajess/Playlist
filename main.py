import os
import sys
import subprocess
from collections import defaultdict
from pathlib import Path

def find_vlc_path():
    """Tries to find the VLC executable on Windows."""
    if sys.platform != "win32":
        return "vlc"
    possible_paths = [
        r"C:\Program Files\VideoLAN\VLC\vlc.exe",
        r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def find_and_categorize_videos(start_path):
    """Scans for video files and categorizes them."""
    categorized_videos = defaultdict(list)
    for root, dirs, files in os.walk(start_path):
        # Sort files to ensure a consistent playback order
        for file in sorted(files):
            if file.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')):
                full_path = os.path.join(root, file)
                category = os.path.basename(root)
                if root == start_path:
                    category = "General"
                categorized_videos[category].append(full_path)
    return categorized_videos

def play_video_and_wait(filepath, vlc_path):
    """
    Plays a single video file and waits for the player to close.
    This is a 'blocking' call.
    """
    try:
        file_uri = Path(filepath).as_uri()
        if vlc_path:
            # 'vlc://quit' tells VLC to close after the playlist (of one item) is done.
            command = [vlc_path, '--one-instance', file_uri, 'vlc://quit']
            # Use subprocess.run to wait for the command to complete.
            subprocess.run(command, check=True)
        else:
            # Fallback for default players (might not always wait)
            print("VLC not found. Waiting for default player is not guaranteed.")
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            if sys.platform == "win32":
                proc = subprocess.Popen(['start', '/WAIT', os.path.normpath(filepath)], shell=True)
                proc.wait()
            else:
                subprocess.run([opener, file_uri])
    except Exception as e:
        print(f"Error playing video: {e}")

if __name__ == "__main__":
    video_directory = "C:/Users/chadr/Videos"
    
    if not os.path.isdir(video_directory):
        print(f"The directory '{video_directory}' does not exist.")
    else:
        vlc_executable_path = find_vlc_path()
        playlist_data = find_and_categorize_videos(video_directory)
        
        if not playlist_data:
            print("No video files found.")
        else:
            # Create a numbered list of categories
            categories = sorted(playlist_data.keys())
            
            print("--- Video Categories ---")
            for i, category in enumerate(categories):
                video_count = len(playlist_data[category])
                print(f"  {i+1}. {category} ({video_count} videos)")
            print("------------------------")

            while True:
                choice_str = input("Enter a category number to play (or 'q' to quit): ")
                if choice_str.lower() == 'q':
                    break
                
                try:
                    choice_num = int(choice_str)
                    if 1 <= choice_num <= len(categories):
                        selected_category = categories[choice_num - 1]
                        videos_to_play = playlist_data[selected_category]
                        
                        print(f"\nPlaying all videos in category: [{selected_category}]")
                        for i, video_path in enumerate(videos_to_play):
                            print(f"  Now playing ({i+1}/{len(videos_to_play)}): {os.path.basename(video_path)}")
                            play_video_and_wait(video_path, vlc_executable_path)
                        
                        print(f"\nFinished category [{selected_category}].")
                        print("\n--- Video Categories ---")
                        for i, category in enumerate(categories):
                            video_count = len(playlist_data[category])
                            print(f"  {i+1}. {category} ({video_count} videos)")
                        print("------------------------")

                    else:
                        print("Invalid number. Please try again.")
                except ValueError:
                    print("That's not a valid number. Please enter a number or 'q'.")
