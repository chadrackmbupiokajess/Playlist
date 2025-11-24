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
        for file in sorted(files):
            if file.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')):
                full_path = os.path.join(root, file)
                category = os.path.basename(root)
                if root == start_path:
                    category = "General"
                categorized_videos[category].append(full_path)
    return categorized_videos

def play_video_playlist(video_paths, vlc_path):
    """
    Plays a list of videos sequentially.
    If VLC is found, it's given the entire playlist at once.
    Otherwise, it falls back to playing one by one with the default player.
    """
    if not video_paths:
        print("No videos to play in this category.")
        return

    try:
        if vlc_path:
            print("Launching VLC with the full category playlist...")
            # Convert all file paths to URIs for VLC
            file_uris = [Path(p).as_uri() for p in video_paths]
            
            # Command: vlc.exe [options] video1 video2 video3... vlc://quit
            # vlc://quit ensures VLC closes after the last video in the playlist.
            command = [vlc_path, '--one-instance'] + file_uris + ['vlc://quit']
            
            # We use .run() so the script waits for VLC to be closed.
            subprocess.run(command, check=True)
        else:
            # Fallback for when VLC is not found
            print("VLC not found. Playing with default player one by one.")
            for i, video_path in enumerate(video_paths):
                print(f"  Now playing ({i+1}/{len(video_paths)}): {os.path.basename(video_path)}")
                if sys.platform == "win32":
                    # 'start /WAIT' is a blocking call on Windows
                    subprocess.run(['start', '/WAIT', '', os.path.normpath(video_path)], shell=True, check=True)
                else:
                    opener = "open" if sys.platform == "darwin" else "xdg-open"
                    subprocess.run([opener, video_path], check=True)
    except Exception as e:
        print(f"An error occurred during playback: {e}")

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
            categories = sorted(playlist_data.keys())
            
            while True:
                print("\n--- Video Categories ---")
                for i, category in enumerate(categories):
                    video_count = len(playlist_data[category])
                    print(f"  {i+1}. {category} ({video_count} videos)")
                print("------------------------")

                choice_str = input("Enter a category number to play (or 'q' to quit): ")
                if choice_str.lower() == 'q':
                    break
                
                try:
                    choice_num = int(choice_str)
                    if 1 <= choice_num <= len(categories):
                        selected_category = categories[choice_num - 1]
                        videos_to_play = playlist_data[selected_category]
                        
                        print(f"\nQueueing all videos in category: [{selected_category}]")
                        play_video_playlist(videos_to_play, vlc_executable_path)
                        print(f"\nFinished category [{selected_category}]. Returning to menu.")
                    else:
                        print("Invalid number. Please try again.")
                except ValueError:
                    print("That's not a valid number. Please enter a number or 'q'.")
