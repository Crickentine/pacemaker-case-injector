# Playlist to Database Injector User Guide

## Overview
This application allows you to inject playlists from `.m3u8` files into a Pacemaker database. You can either select a folder containing multiple playlist files or a single playlist file for injection.

## Requirements
- Windows operating system
- SQLite database file for Pacemaker
- Playlist files in `.m3u8` format

## Instructions

### Launch the Application
1. Double-click the executable file to open the application.

### Select Database File
1. Click on the **Select Database** button.
2. A file dialog will open. Navigate to your Pacemaker database file (`C:\Users\USER\AppData\Roaming\Tonium\Pacemaker\music.db`) and select it.
3. The selected database file path will be displayed in the application.

### Select Playlists
You have two options to select playlists:

#### Select Playlist Folder
1. Click on the **Select Playlist Folder** button.
2. A folder dialog will open. Navigate to the folder containing your `.m3u8` playlist files and select it.
3. All `.m3u8` files in the folder will be processed.

#### Select Single Playlist File
1. Click on the **Select Single Playlist File** button.
2. A file dialog will open. Navigate to your `.m3u8` playlist file and select it.
3. Only the selected file will be processed.

### Start Injection
1. After selecting the database and playlist(s), the injection process will start automatically.
2. Wait for the process to complete. A message will appear indicating the success or failure of the injection.

### Close the Application
1. Once the process is complete, you can close the application.

## Notes
- Ensure that the database file and playlist files are accessible and not being used by other applications during the injection process.
- The application will handle multiple playlists in a folder and inject each one separately.
- If you encounter any issues, please check the file paths and ensure they are correct.
