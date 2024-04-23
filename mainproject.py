from dotenv import load_dotenv
import os
import base64
import random
from requests import post, get
import json
import customtkinter
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageTk
from io import BytesIO
import sys
import tracemalloc
tracemalloc.start()
executor = ThreadPoolExecutor(max_workers=5)

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")

load_dotenv() 
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

def main():
    root = customtkinter.CTk()
    windowwidth = root.winfo_screenwidth()
    windowheight = root.winfo_screenheight()
    w = 500
    h = 900
    x_coordinate = windowwidth - 500
    root.geometry(f'{w}x{h}+{x_coordinate}+{0}')
    frame = customtkinter.CTkFrame(master=root)
    frame.pack(pady=20, padx=60, fill="both", expand=True)
    fonttitle = customtkinter.CTkFont(family="Raleway", size=25, weight="bold")
    label = customtkinter.CTkLabel(master=frame, text="Spotify Assist", font=fonttitle)
    label.pack(pady=30, padx=10)
    fontbutton = customtkinter.CTkFont(family="Raleway", size=15)
    button = customtkinter.CTkButton(master=frame, text="New Albums", font=fontbutton, command=lambda:albumgenerator(root))
    button.pack(pady=5)
    button2 = customtkinter.CTkButton(master=frame, text="Find New Artists", font=fontbutton, command=lambda:relatedartists(root))
    button2.pack(pady=5)
    button3 = customtkinter.CTkButton(master=frame, text="Explore Artist", font=fontbutton, command=lambda: exploreartists(root))
    button3.pack(pady=5)
    button4 = customtkinter.CTkButton(master=frame, text="Exit", font=fontbutton, command=exitprogram)
    button4.pack(pady=50)
    token = get_token()
    root.mainloop()

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"q={artist_name}&type=artist&limit=1"
    query_url = url + "?" + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No artist found")
        return None
    
    return json_result[0]

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=GB"
    headers = get_auth_header(token)
    result = requests.get(url, headers=headers)
    if result.status_code == 200:
        json_result = result.json()
        tracks = json_result.get("tracks", [])
        songs = [track["name"] for track in tracks]
        return songs
    else:
        print(f"Status code: {result.status_code}")
        return []

def get_albums_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    headers = get_auth_header(token)
    result = requests.get(url, headers=headers)
    if result.status_code == 200:
        json_result = result.json()
        albums = json_result.get("items", [])
        return albums

    else:
        print(f"Status code: {result.status_code}")
        return []

def get_related_artists(token, artist_id):
     # async with aiohttp.ClientSession() as session:
     #    return await fetch_related_artists(artist_id, token, session)
    url= f"https://api.spotify.com/v1/artists/{artist_id}/related-artists"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    return json_result

def generaterandom():
    limit = 3
    categories = sp.categories(limit=limit)
    categoryids = [category['id'] for category in categories['categories']['items']]
    albums = []

    for categoryid in categoryids:
        results = sp.category_playlists(category_id=categoryid, limit=limit)
        playlists = results['playlists']['items']
        random.shuffle(playlists)
        for playlist in playlists: 
            playlists_tracks = sp.playlist_items(playlist['id'])
            for track in playlists_tracks['items']:
                album = track['track']['album']
                if album not in albums and album['album_type'] == 'album':
                    albums.append(album)
    return albums

def randomg(frameag, topag):
    for widget in frameag.winfo_children():
        if isinstance(widget, customtkinter.CTkLabel):
            widget.destroy()
    albums = sp.new_releases(country='GB', limit=50)
    album_items = albums['albums']['items']
    random.shuffle(album_items)
    minimumnumber = min(6, len(album_items))
    futures = []
    fontalbum = customtkinter.CTkFont(family="Raleway", size=10)

    for i in range(minimumnumber):
        albumname = album_items[i]['name']
        albumimage = album_items[i]['images']
        albumurl = albumimage[0]['url']
        future = executor.submit(download_image, albumurl)
        futures.append((albumname, future))

    for i, (albumname, future) in enumerate(futures):
        imgdata = future.result()
        img = Image.open(BytesIO(imgdata))
        newsize = (40, 40)
        resized = img.resize(newsize, Image.ANTIALIAS)
        img = ImageTk.PhotoImage(resized)
        artistnames = ', '.join(artist['name'] for artist in album_items[i]['artists'])
        label = customtkinter.CTkLabel(master=frameag, text=f"Album Name: {albumname}", font=fontalbum)
        label.pack()
        labelimage = customtkinter.CTkLabel(master=frameag, image=img, text="")
        labelimage.pack()
        labelimage.image = img
        label2 = customtkinter.CTkLabel(master=frameag, text=(f"Artist(s): {artistnames}"), font=fontalbum)
        label2.pack()

def exploreartists(root):
    topea = customtkinter.CTkToplevel()
    windowheight = root.winfo_screenheight()
    w = 900
    h = windowheight // 1.5
    y_position = h - topea.winfo_reqheight()
    topea.geometry(f'{w}x{h}+{0}+{y_position}')
    topea.title("Related Artists")
    topea.focus_set()
    frameea = customtkinter.CTkScrollableFrame(master=topea)
    frameea.pack(pady=20, padx=60, fill="both", expand=True)
    fontinput = customtkinter.CTkFont(family="Raleway", size=12)
    artistentry = customtkinter.CTkEntry(master=frameea, font=fontinput, placeholder_text="Enter Artist Name")
    artistentry.pack(pady=20, padx=60)
    def getAlbums():
        for widget in frameea.winfo_children():
            if isinstance(widget, customtkinter.CTkFrame):
                widget.destroy()
        token = get_token()
        text = artistentry.get()
        result = search_for_artist(token, text)
        artist_id = result['id']
        output = get_albums_by_artist(token, artist_id)
        albumnames = []
        albumimages = []
        futures = []
        for album in output:
            if album["album_type"] == "album":
                albumnames.append(album["name"])
                albumimages.append(album["images"][0]["url"])
        albumframe = customtkinter.CTkFrame(master=frameea)
        albumframe.pack(pady=20,padx=60)
        stringoutput = ""
        for i in range(len(albumnames)):
            future = executor.submit(download_image, albumimages[i])
            futures.append(future)
        for i, future in enumerate(futures):
            imgdata = future.result()
            img = Image.open(BytesIO(imgdata))
            newsize = (40, 40)
            resized = img.resize(newsize, Image.ANTIALIAS)
            img = ImageTk.PhotoImage(resized)
            fontalbum = customtkinter.CTkFont(family="Raleway", size=16)
            label = customtkinter.CTkLabel(master=albumframe, font=fontalbum, text=f"{albumnames[i]}")
            label.grid(row=i, column=0, padx=10, pady=10)
            imageoutput = customtkinter.CTkLabel(master=albumframe, image=img, text=" ")
            imageoutput.image = img
            imageoutput.grid(row=i, column=1, padx=10, pady=10)

        font = customtkinter.CTkFont(family="Arial", size=16)
        LabelArtists = customtkinter.CTkLabel(master=frameea, text=stringoutput, font=font)
        LabelArtists.pack()

    button = customtkinter.CTkButton(master=frameea, text="Submit", command=getAlbums)
    button.pack(pady=10, padx=60)
    back_button = customtkinter.CTkButton(master=frameea, text="Back", command=topea.destroy)
    back_button.pack(pady=5, padx=60)

def download_image(url):
    response = requests.get(url)
    return response.content

def albumgenerator(root):
    topag = customtkinter.CTkToplevel()
    windowheight = root.winfo_screenheight()
    w = 900
    h = windowheight//1.5
    y_position = h - topag.winfo_reqheight()
    topag.geometry(f'{w}x{h}+{0}+{y_position}')
    topag.title("New Albums")
    topag.focus_set()
    frameag = customtkinter.CTkFrame(master=topag)
    frameag.pack(pady=20, padx=60, fill="both", expand=True)
    fontbutton = customtkinter.CTkFont(family="Raleway", size=15)
    random_button = customtkinter.CTkButton(master=frameag, text="Randomise Again", font=fontbutton, command=lambda: randomg(frameag, topag))
    random_button.pack(pady=5, padx=60)
    back_button = customtkinter.CTkButton(master=frameag, text="Back", font=fontbutton, command=topag.destroy)
    back_button.pack(pady=5, padx=60)
    randomg(frameag, topag)



def relatedartists(root):
    topra = customtkinter.CTkToplevel()
    windowheight = root.winfo_screenheight()
    w = 900
    h = windowheight//1.5
    y_position = h - topra.winfo_reqheight()
    topra.geometry(f'{w}x{h}+{0}+{y_position}')
    topra.title("Related Artists")
    topra.focus_set()
    framera = customtkinter.CTkFrame(master=topra)
    framera.pack(pady=20, padx=60, fill="both", expand=True)
    fontinput = customtkinter.CTkFont(family="Raleway", size=12)
    artistentry = customtkinter.CTkEntry(master=framera, font=fontinput, placeholder_text="Enter Artist Name")
    artistentry.pack(pady=20, padx=60)
    def getArtistName():
        global LabelArtists
        if 'LabelArtists' in globals():
            LabelArtists.destroy()
        token = get_token()
        text = artistentry.get()
        result = search_for_artist(token, text)
        artist_id = result['id']
        artists = get_related_artists(token, artist_id)
        stringoutput = "" 
        for i, artist in enumerate(artists["artists"]):
            stringoutput += f"{i+1}. {artist['name']}\n"
        font = customtkinter.CTkFont(family="Raleway", size=16)
        LabelArtists = customtkinter.CTkLabel(master=framera, text=stringoutput, font=font)
        LabelArtists.pack()

    fontbutton = customtkinter.CTkFont(family="Raleway", size=15)
    button = customtkinter.CTkButton(master=framera, text="Submit", font=fontbutton, command=getArtistName)
    button.pack(pady=10, padx=60)

    backbutton = customtkinter.CTkButton(master=framera, text="Back", font=fontbutton, command=topra.destroy)
    backbutton.pack(pady=20, padx=60)

def exitprogram():
    sys.exit()
        
