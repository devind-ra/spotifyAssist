import asyncio

from spotify_api import get_token
from relatedartists import relatedartists
from utilities import exitprogram
from newreleases import randomg, albumgenerator, exploreartists
import customtkinter
import tracemalloc

tracemalloc.start()

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")

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
    button = customtkinter.CTkButton(master=frame, text="New Albums", font=fontbutton)
    button.configure(command=lambda: asyncio.run(albumgenerator(root)))
    button.pack(pady=5)
    button2 = customtkinter.CTkButton(master=frame, text="Find New Artists", font=fontbutton, command=lambda:relatedartists(root))
    button2.pack(pady=5)
    button3 = customtkinter.CTkButton(master=frame, text="Explore Artist", font=fontbutton, command=lambda: exploreartists(root))
    button3.pack(pady=5)
    button4 = customtkinter.CTkButton(master=frame, text="Exit", font=fontbutton, command=exitprogram)
    button4.pack(pady=50)
    token = get_token()
    root.mainloop()







