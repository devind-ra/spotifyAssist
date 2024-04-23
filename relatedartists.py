import customtkinter

from spotifyAssist.spotify_api import get_token, search_for_artist, get_related_artists


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