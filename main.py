#!./.venv/bin/python3
# Simple program that is run on startup to show weather, NHL news, and other
# stuff. Made for personal use.
#
# Initial revision: September 3rd, 2025
# Author: Alex Trumier
# Email: adtrumier@protonmail.com

import os
import subprocess
import json
import tkinter as tk
import requests_cache
from retry_requests import retry
import openmeteo_requests
import tkinter.font as tkFont
import datetime
import webbrowser
import time as t

# Get location based on IP Address, then store the latitutude and longitude
# in a file so that we don't look it up every time.
def get_location() -> (str, str):
    home_dir = os.path.expanduser('~')

    # if the file already exists, just load it
    if os.path.exists(f"{home_dir}/.loc"):
        with open(f"{home_dir}/.loc", "r") as f:
            loc = f.readline().strip()
            splitted = loc.split(", ")
            return (splitted[0], splitted[1])
    else:
        # otherwise, use curl to get IP then lookup the location via ip-api
        ip = subprocess.run("curl ifconfig.me", shell=True, capture_output=True)
        loc = json.loads(subprocess.run(f"curl ip-api.com/json/{str(ip.stdout)[1:]}", \
                                        shell=True, capture_output=True).stdout)
        max_len = max(len(str(loc["lat"])), len(str(loc["lon"])))
        with open(f"{home_dir}/.loc", "a") as f:
            f.write(f"{"{:.2f}".format(loc["lat"])}, {"{:.2f}".format(loc["lon"])}")
        return (str(loc["lat"]), str(loc["lon"]))

# Get the weather based on the given location.
def get_weather(loc: (str, str)) -> (float, float, float):
    url = "https://api.open-meteo.com/v1/forecast"

    # tons of bootstrap code here to simply get the hourly stuff.
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    params = {
        "latitude": float(loc[0]),
        "longitude": float(loc[1]),
        "hourly": ["temperature_2m", "precipitation_probability", "apparent_temperature"],
        "forecast_days": 1,
    }
    weather = openmeteo.weather_api(url, params=params)
    hourly = weather[0].Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_precipitation_probability = hourly.Variables(1).ValuesAsNumpy()
    hourly_apparent_temperature = hourly.Variables(2).ValuesAsNumpy()

    # now we can just iterate through the arrays to find the max.
    # FIXME: this sucks because there is probably a one liner to do this
    max_temp = -9999999
    max_feels_like = -999999
    max_precip = -99999

    for i in hourly_temperature_2m:
        if i > max_temp:
            max_temp = i

    for i in hourly_precipitation_probability:
        if i > max_precip:
            max_precip = i

    for i in hourly_apparent_temperature:
        if i > max_feels_like:
            max_feels_like = i

    return (max_temp, max_feels_like, max_precip)

# opens a link in firefox.
def open_link(link: str):
    firefox = webbrowser.Mozilla("/usr/bin/firefox")
    firefox.open(link)

def update_time():
    current_time = t.strftime('%H:%M:%S')
    time.config(text="--- Current date and time ---\n" + \
                str(datetime.date.today()) + " " + current_time)
    time.after(1000, update_time)


# FIXME: TBH should be in a frame

root = tk.Tk()
root.geometry("1280x960")

# set 3x3 grid
for i in range(0, 3):
    root.columnconfigure(i, weight=1)
    root.rowconfigure(i, weight=1)

font = tkFont.Font(size=25)
middlefont = tkFont.Font(size=16)


name = tk.Label(root, text=f"Welcome back {os.getenv("USER")}.", font=font)
name.grid(row=0, column=1, sticky="N")

weatherframe = tk.Frame(root)
weatherframe.rowconfigure(0, weight=1)
weatherframe.rowconfigure(1, weight=1)

weatherlabel = tk.Label(weatherframe, text=f"{str(datetime.date.today())} Weather", font=middlefont)
weatherlabel.grid(row=0, column=0)

weathercontent = tk.Label(weatherframe, text="")
weathercontent.grid(row=1, column=0)

weatherframe.grid(row=1, column=0)

linkframe = tk.Frame(root)
linkframe.rowconfigure(0, weight=1)
linkframe.rowconfigure(1, weight=1)
linkframe.rowconfigure(2, weight=1)

linklabel = tk.Label(linkframe, text="Links")
linklabel.grid(row=0, column=0)

slashdot = tk.Button(linkframe, text="Open Slashdot in Firefox", \
                     command=lambda:open_link("www.slashdot.org"))
slashdot.grid(row=1, column=0)

email = tk.Button(linkframe, text="Open email", \
                  command=lambda:open_link("https://mail.proton.me/u/0/inbox"))
email.grid(row=2, column=0)

linkframe.grid(row=1, column=2)

time = tk.Label(root, text="")
time.grid(row=0, column=1)
update_time()



if __name__ == "__main__":
    weather = get_weather(get_location())
    weather_str = f"High: {int(weather[0])}°C\nFeels like: {int(weather[1])}°C\nPOP: {int(weather[2])}%"
    weathercontent.config(text=weather_str)
    root.mainloop()
