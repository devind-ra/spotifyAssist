import base64
import json
import os
import random

import requests
import spotipy
from dotenv import load_dotenv
from spotipy import SpotifyClientCredentials
from requests import post, get

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

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
    url = f"https://api.spotify.com/v1/artists/{artist_id}/related-artists"
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