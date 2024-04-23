import asyncio
import random

import aiohttp
from PIL import Image, ImageTk
import customtkinter
from concurrent.futures import ThreadPoolExecutor
from spotify_api import sp, get_token, search_for_artist, get_albums_by_artist
from utilities import download_image_async, download_image
from io import BytesIO
executor = ThreadPoolExecutor(max_workers=5)


async def download_album_image(album_url):
    loop = asyncio.get_event_loop()
    imgdata = await loop.run_in_executor(executor, download_image_async, album_url)
    return imgdata
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
    # imgdatas = [await future for albumname, future in futures]

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
async def download_images(album_images):
    async with aiohttp.ClientSession() as session:
        tasks = [download_image_async(url, session) for url in album_images]
        return await asyncio.gather(*tasks)

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
    async def getAlbums():
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
        # futures = []
        for album in output:
            if album["album_type"] == "album":
                albumnames.append(album["name"])
                albumimages.append(album["images"][0]["url"])
        imgdata_list = await download_images(albumimages)
        albumframe = customtkinter.CTkFrame(master=frameea)
        albumframe.pack(pady=20,padx=60)
        stringoutput = ""
        # for i in range(len(albumnames)):
        #     future = executor.submit(download_image, albumimages[i])
        #     futures.append(future)
        for i, imgdata in enumerate(imgdata_list):
            if imgdata is not None:
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
            else:
                print(f"Failed to download {albumnames[i]}")

        font = customtkinter.CTkFont(family="Arial", size=16)
        LabelArtists = customtkinter.CTkLabel(master=frameea, text=stringoutput, font=font)
        LabelArtists.pack()

    button = customtkinter.CTkButton(master=frameea, text="Submit")
    button.configure(command=lambda: asyncio.run(getAlbums()))
    button.pack(pady=10, padx=60)
    back_button = customtkinter.CTkButton(master=frameea, text="Back", command=topea.destroy)
    back_button.pack(pady=5, padx=60)
