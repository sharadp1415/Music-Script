from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from youtubesearchpython import VideosSearch
import yt_dlp as youtube_dl
from mutagen.easyid3 import EasyID3

# Set up your Spotify app credentials
client_id = ''
client_secret = ''
redirect_uri = 'https://localhost:8888/callback'  # This should be the same as the one you set in your Spotify app settings

def fetch_tracks_from_playlist(selected_playlist_name):

    # Create an instance of the Spotipy client
    sp = Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope='playlist-read-private'))

    # Get the user's playlists
    playlists = sp.current_user_playlists()

    # Grab user's selected playlist object
    for playlist in playlists['items']:
        if playlist['name'] == selected_playlist_name:
            selected_playlist = playlist

    # Fetch track names from selected playlist
    results = sp.playlist_tracks(selected_playlist['id'])

    # print(results['items'][0]['track'].keys())

    tracks = [track['track'] for track in results['items']]

    while results['next']:
        results = sp.next(results)
        temp = [track['track'] for track in results['items']]
        tracks.extend(temp)

    return tracks

def search_and_download_audio(track):

    track['name'] = track['name'].replace('"', '')

    search_term = track['name'] + " " + track['artists'][0]['name'] + " audio"

    # print(search_term)

    # Search for videos
    search = VideosSearch(search_term, limit=1)
    results = search.result()['result']
    # print(results)

    # return
    
    if len(results) > 0:
        # Get the first video from the search results
        video_id = results[0]['id']
        video_title = results[0]['title']
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"

        # print(youtube_url)
        
        # Download and convert the video to MP3~
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': f"{track['name']}.%(ext)s",
        }
        
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        
        return f"{track['name']}.mp3"
    
    return None

def download_tracks(tracks):

    for track in tracks:
        try:
            if not search_and_download_audio(track):
                print("Error downloading", track['name'])
            
            path = track['name'] + ".mp3"
            meta = EasyID3(path)
            
            meta['title'] = track['name']
            meta['artist'] = ', '.join(t['name'] for t in track['artists'])
            meta['album'] = track['album']['name']
            meta.save()
        except:
            print("\nError downloading", track['name'], "\n")


if __name__ == "__main__":
    tracks = fetch_tracks_from_playlist("Straight Outta Bihar")

    download_tracks(tracks[:])
