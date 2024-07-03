import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import glob
import mutagen
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4
from mutagen.asf import ASF

def parse_m3u8(file_path):
    playlist = []
    current_track = {}
    
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.startswith('#EXTINF:'):
                # Parse metadata line
                duration, title = line.split(',', 1)
                current_track['duration'] = float(duration.replace('#EXTINF:', '').strip())
                current_track['title'] = title.strip()
            elif line and not line.startswith('#'):
                # Parse file path line
                current_track['file_path'] = line.strip()
                playlist.append(current_track)
                current_track = {}
    
    return playlist

def get_audio_metadata(file_path):
    audio = mutagen.File(file_path)
    metadata = {}
    
    if isinstance(audio, MP3):
        metadata['bit_rate'] = audio.info.bitrate // 1000  # kbps
        metadata['sample_rate'] = audio.info.sample_rate
        metadata['file_size'] = os.path.getsize(file_path)
        metadata['play_time_secs'] = int(audio.info.length)
        metadata['format'] = 'MP3'
    elif isinstance(audio, FLAC):
        metadata['bit_rate'] = 0  # FLAC does not have a bit rate in the same way MP3 does
        metadata['sample_rate'] = audio.info.sample_rate
        metadata['file_size'] = os.path.getsize(file_path)
        metadata['play_time_secs'] = int(audio.info.length)
        metadata['format'] = 'FLAC'
    elif isinstance(audio, MP4):
        metadata['bit_rate'] = 0  # MP4 bit rate is not provided by mutagen
        metadata['sample_rate'] = audio.info.sample_rate
        metadata['file_size'] = os.path.getsize(file_path)
        metadata['play_time_secs'] = int(audio.info.length)
        metadata['format'] = 'MP4'
    elif isinstance(audio, ASF):
        metadata['bit_rate'] = 0  # ASF bit rate is not provided by mutagen
        metadata['sample_rate'] = audio.info.sample_rate
        metadata['file_size'] = os.path.getsize(file_path)
        metadata['play_time_secs'] = int(audio.info.length)
        metadata['format'] = 'ASF'
    else:
        raise ValueError(f"Unsupported file format: {file_path}")

    metadata['title'] = str(audio.tags.get('TIT2', [''])[0])
    metadata['artist'] = str(audio.tags.get('TPE1', [''])[0])
    metadata['album'] = str(audio.tags.get('TALB', [''])[0])
    metadata['year'] = str(audio.tags.get('TDRC', [''])[0])
    metadata['genre'] = str(audio.tags.get('TCON', [''])[0])
    metadata['composer'] = str(audio.tags.get('TCOM', [''])[0])
    metadata['track_number'] = str(audio.tags.get('TRCK', [''])[0])
    metadata['album_artist'] = str(audio.tags.get('TPE2', [''])[0])
    metadata['bpm'] = str(audio.tags.get('TBPM', [''])[0])
    metadata['comments'] = str(audio.tags.get('COMM', [''])[0])
    metadata['label'] = str(audio.tags.get('TPUB', [''])[0])
    metadata['producer'] = str(audio.tags.get('TPE3', [''])[0])
    metadata['remixer'] = str(audio.tags.get('TPE4', [''])[0])
    metadata['key'] = str(audio.tags.get('TKEY', [''])[0])
    metadata['number_of_tracks'] = str(audio.tags.get('TRCK', [''])[0])
    metadata['disc_number'] = str(audio.tags.get('TPOS', [''])[0])
    metadata['number_of_discs'] = str(audio.tags.get('TPOS', [''])[0])
    metadata['rating'] = str(audio.tags.get('POPM', [''])[0])

    # Extract numeric part for track number, disc number, and number of discs
    if metadata['track_number']:
        metadata['track_number'] = metadata['track_number'].split('/')[0]
    if metadata['number_of_tracks']:
        metadata['number_of_tracks'] = metadata['number_of_tracks'].split('/')[0]
    if metadata['disc_number']:
        metadata['disc_number'] = metadata['disc_number'].split('/')[0]
    if metadata['number_of_discs']:
        metadata['number_of_discs'] = metadata['number_of_discs'].split('/')[0]

    return metadata

def inject_playlist_to_db(m3u8_path, db_path, case_name):
    # Parse the M3U8 file
    parsed_playlist = parse_m3u8(m3u8_path)
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Start a transaction
        cursor.execute('BEGIN')
        
        # Insert new case
        cursor.execute("""
            INSERT INTO cases (name, date_created, genre, year, creator_id, times_played, image_id)
            VALUES (?, strftime('%s', 'now'), 'Various', 2024, 'Tonium;Editor;2.0.2.14170;1117277940118978560', 0, 0);
        """, (case_name,))
        conn.commit()

        # Get the new case_id
        cursor.execute("SELECT last_insert_rowid()")
        new_case_id = cursor.fetchone()[0]
        
        # Insert tracks and map them to the new case
        for track in parsed_playlist:
            title = track['title']
            file_path = track['file_path']
            
            try:
                metadata = get_audio_metadata(file_path)
                print(f"Metadata for {file_path}: {metadata}")
            except Exception as e:
                print(f"Error reading metadata from {file_path}: {e}")
                continue
            
            # Ensure no None values are inserted and convert numerical fields
            for key in metadata:
                if metadata[key] is None:
                    metadata[key] = 0 if isinstance(metadata[key], (int, float)) else ""
                if key in ['bit_rate', 'sample_rate', 'file_size', 'play_time_secs', 'track_number', 'bpm', 'number_of_tracks', 'disc_number', 'number_of_discs', 'rating']:
                    try:
                        metadata[key] = int(metadata[key])
                    except ValueError:
                        metadata[key] = 0
                elif key == 'play_time_secs':
                    try:
                        metadata[key] = float(metadata[key])
                    except ValueError:
                        metadata[key] = 0.0

            # Check if track exists
            cursor.execute("SELECT track_id FROM tracks WHERE location = ?", (file_path,))
            result = cursor.fetchone()
            
            if result:
                track_id = result[0]
            else:
                # Prepare values for insertion
                values = (
                    metadata.get('title', ''), file_path, metadata.get('bit_rate', 0), metadata.get('sample_rate', 0), 
                    metadata.get('file_size', 0), metadata.get('play_time_secs', 0.0), metadata.get('format', ''), metadata.get('artist', ''), 
                    metadata.get('album_artist', ''), metadata.get('composer', ''), metadata.get('album', ''), int(metadata.get('track_number', 0)), 
                    metadata.get('year', ''), metadata.get('genre', ''), 0, int(os.path.getmtime(file_path)), -1, 0, -1, 0, 
                    metadata.get('bpm', 0), metadata.get('label', ''), 2, None, -1, -1, None, metadata.get('title', ''), 
                    metadata.get('artist', ''), metadata.get('album', ''), metadata.get('genre', ''), metadata.get('bpm', 0), 
                    None, metadata.get('producer', ''), metadata.get('remixer', ''), metadata.get('key', ''), metadata.get('number_of_tracks', 0), 
                    metadata.get('disc_number', 0), metadata.get('number_of_discs', 0), int(os.path.getmtime(file_path)), 
                    '2.0.2.14170', '2.0.2.14170', 1, metadata.get('rating', 0), metadata.get('comments', '')
                )

                # Print debug information
                columns = (
                    "title, location, bit_rate, sample_rate, file_size, play_time_secs, format, artist, album_artist, "
                    "composer, album, track_number, year, genre, is_part_of_c, date_added, last_played, times_played, "
                    "cue_point, rc_mixes, bpm, label, track_flags, global_id, loop_in, loop_out, structured_ct, "
                    "ind_title, ind_artist, ind_album, ind_genre, ind_bpm, discid, producer, remixer, key, number_of_tracks, "
                    "disc_number, number_of_discs, date_modified, modified_by_ed, analyzed_by_ed, analysis_ver, rating, comments"
                )

                print(f"Inserting into tracks: \nColumns: {columns}\nValues: {values}")

                # Insert new track with metadata
                cursor.execute(f"""
                    INSERT INTO tracks ({columns})
                    VALUES ({','.join(['?' for _ in values])});
                """, values)
                conn.commit()
                
                # Get the new track_id
                cursor.execute("SELECT last_insert_rowid()")
                track_id = cursor.fetchone()[0]
                
                # Map track to case
                cursor.execute("""
                    INSERT INTO casetracks (case_id, track_id)
                    VALUES (?, ?);
                """, (new_case_id, track_id))
            
            # Commit the transaction
            conn.commit()
            print("Playlist successfully injected into the database.")
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        # Close the database connection
        conn.close()
        print("Database connection closed.")

# Function to process multiple playlists
def process_multiple_playlists(folder_path, db_path):
    m3u8_files = glob.glob(os.path.join(folder_path, "*.m3u8"))
    for m3u8_file in m3u8_files:
        file_name = os.path.splitext(os.path.basename(m3u8_file))[0]
        inject_playlist_to_db(m3u8_file, db_path, file_name)

# Function to process a single playlist
def process_single_playlist(playlist_path, db_path):
    file_name = os.path.splitext(os.path.basename(playlist_path))[0]
    inject_playlist_to_db(playlist_path, db_path, file_name)

# GUI functions
def select_db_file():
    db_file = filedialog.askopenfilename(title="Select the database file", filetypes=(("SQLite files", "*.db"), ("All files", "*.*")))
    db_path_entry.delete(0, tk.END)
    db_path_entry.insert(0, db_file)

def select_playlist_file():
    playlist_file = filedialog.askopenfilename(title="Select the playlist file", filetypes=(("M3U8 files", "*.m3u8"), ("All files", "*.*")))
    playlist_path_entry.delete(0, tk.END)
    playlist_path_entry.insert(0, playlist_file)

def select_folder():
    folder = filedialog.askdirectory(title="Select the folder containing playlists")
    folder_path_entry.delete(0, tk.END)
    folder_path_entry.insert(0, folder)

def process_playlists():
    db_path = db_path_entry.get()
    playlist_path = playlist_path_entry.get()
    folder_path = folder_path_entry.get()

    if not db_path:
        messagebox.showerror("Error", "Please select a database file.")
        return

    if playlist_path and folder_path:
        messagebox.showerror("Error", "Please select either a single playlist file or a folder containing playlists, not both.")
        return

    if not playlist_path and not folder_path:
        messagebox.showerror("Error", "Please select either a single playlist file or a folder containing playlists.")
        return

    if playlist_path:
        process_single_playlist(playlist_path, db_path)
    else:
        process_multiple_playlists(folder_path, db_path)
    
    messagebox.showinfo("Success", "Playlists successfully injected into the database.")

# Create the main application window
root = tk.Tk()
root.title("Playlist Injector")

# Database file selection
tk.Label(root, text="Database File:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
db_path_entry = tk.Entry(root, width=50)
db_path_entry.grid(row=0, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=select_db_file).grid(row=0, column=2, padx=10, pady=5)

# Single playlist file selection
tk.Label(root, text="Single Playlist File:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
playlist_path_entry = tk.Entry(root, width=50)
playlist_path_entry.grid(row=1, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=select_playlist_file).grid(row=1, column=2, padx=10, pady=5)

# Folder selection for multiple playlists
tk.Label(root, text="Folder Containing Playlists:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
folder_path_entry = tk.Entry(root, width=50)
folder_path_entry.grid(row=2, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=select_folder).grid(row=2, column=2, padx=10, pady=5)

# Process button
tk.Button(root, text="Inject Playlists", command=process_playlists).grid(row=3, column=0, columnspan=3, pady=10)

# Start the GUI event loop
root.mainloop()