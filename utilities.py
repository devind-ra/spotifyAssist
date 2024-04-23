import sys
import asyncio
import aiohttp
import requests
from requests import session

def download_image(url):
    response = requests.get(url)
    return response.content
async def download_image_async(url, session):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.read()
            else:
                print(f"Failed to download image {response.status.code}")
                return None
    except aiohttp.ClientError as e:
        print(f"Error downloading: {e}")
        return None

# def download_image(url):
#     response = requests.get(url)
#     return response.content
def exitprogram():
    sys.exit()
