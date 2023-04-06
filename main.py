import requests
import pprint
import subprocess
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController
from secrets import refreshToken, base64
import time

#Uses constant refresh token to generate a new token
def newToken():
    query = "https://accounts.spotify.com/api/token"
    response = requests.post(query,
                             data={"grant_type": "refresh_token",
                                   "refresh_token": refreshToken},
                             headers={"Authorization": "Basic " + base64})
    return response.json()['access_token']

keyboard = KeyboardController()
mouse = MouseController()
query = "https://api.spotify.com/v1/me/player/currently-playing"
p = None
spotify_token = newToken()
lastRefresh = time.time()


#Functions for common keypress actions and Spotify startup sequence
def spacebar():
    keyboard.press(Key.space)
    keyboard.release(Key.space)

def altTab():
    keyboard.press(Key.alt)
    keyboard.press(Key.tab)
    keyboard.release(Key.alt)
    keyboard.release(Key.tab)

def nextSong():
    keyboard.press(Key.ctrl)
    keyboard.press(Key.right)
    time.sleep(0.01)
    keyboard.release(Key.ctrl)
    keyboard.release(Key.right)

def clickPlaylist():
    #Make Spotify fullscreen, take a screenshot, put into photopea.com and click info. Hover over playlist you want in order to get its screen coords.
    mouse.position = (40, 300)
    mouse.press(Button.left)
    mouse.release(Button.left)

def start():
    global p
    p = subprocess.Popen(r"C:\Users\toady\AppData\Roaming\Spotify\Spotify.exe", shell=True)
    time.sleep(2.5)
    spacebar()
    response = requests.get(query, headers={"Content-Type": "application/json",
                                            "Authorization": "Bearer {}".format(spotify_token)})
    #clickPlaylist()
    #API request will for some reason not work properly with just one spacebar play (idk why) so loop will spam play and unplay until it works
    while response.status_code != 200:
        print("failed")
        spacebar()
        spacebar()
        time.sleep(0.1)
        response = requests.get(query, headers={"Content-Type": "application/json",
                                                "Authorization": "Bearer {}".format(spotify_token)})
    nextSong()
    altTab()


start()

while True:
    #Token expires after 1 hour (3600 seconds), needs to be refreshed
    if (time.time() - lastRefresh > 3000):
        spotify_token = newToken()
        lastRefresh = time.time()
        print("successfully refreshed token")
    #Sometimes random stuff throws errors so I just stuck it all in a try catch block and the while loop will just try again
    try:
        response = requests.get(query, headers={"Content-Type": "application/json",
                                                "Authorization": "Bearer {}".format(spotify_token)})
        response_json = response.json()
        if "skipping_next" in response_json['actions']['disallows']:
            print("ad is playing rn")

            subprocess.Popen("taskkill /F /T /PID %i" % p.pid, shell=True)
            time.sleep(2)
            start()
            time.sleep(300)  #Pauses while loop for 5 min so it doesn't run pointlessly, as there obviously won't be another ad for a little while

        else:
            print("song is playing rn")
    except:
        print(response)
    time.sleep(1.3) #1.3 seconds is a good balance between catching the ads ASAP and not spamming too much
