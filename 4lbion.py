#!/usr/bin/env python3
# 4lbion - Open Source launcher for Albion Online
# Jus de Patate_ | ign: jusdepatate | jusdepatate@protonmail.com - 2020

version = "1.0"

try:
    # Native libs
    import os
    import sys
    import json
    import re
    import platform
    import threading
    from hashlib import md5
    from zipfile import ZipFile

    # PyPi libs
    from moviepy.editor import *
    import requests
    import xmltodict
except ImportError:
    print(
        "Unable to import at least one package, did you install all required Pip packages ?"
    )
    sys.exit(1)

try:
    from tkinter import *
    from tkinter import messagebox
    from tkinter import filedialog
    import tkinter.ttk

    # We import tkinter to create GUI
except ImportError:
    print("Unable to import Tkinter, is it installed ? Are you running Py3.x ?")
    sys.exit(1)

screenRes = [
    "3620x2036",
    "3440x1440",
    "2560x1440",
    "1920x1440",
    "1920x1080",
    "1680x1050",
    "1768x992",
    "1600x1024",
    "1400x1050",
    "1600x900",
    "1440x960",
    "1440x900",
    "1280x960",
    "1280x864",
    "1366x768",
    "1280x768",
    "1280x720",
    "1152x768",
    "1152x720",
    "1024x768",
]

languages = {
    "English": "EN-US",
    "Espanol": "ES-ES",
    "Deutsche": "DE-DE",
    "Francais": "FR-FR",
    "русский": "RU-RU",
    "Polskie": "PL-PL",
    "Português (Brasil)": "PT-BR",
}

languagesArray = [
    "English",
    "Espanol",
    "Deutsche",
    "Français",
    "русский",
    "Polskie",
    "Português (Brasil)",
]

curlHeaders = {
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en,*",
    "User-Agent": "Mozilla/5.0",
}


# Exact same headers as the official launcher has


def getScreenSize():
    tempWindow = Tk()
    tempWindow.update_idletasks()
    tempWindow.attributes("-fullscreen", True)
    tempWindow.state("iconic")
    screenSize = tempWindow.winfo_geometry()
    tempWindow.destroy()
    # we create a fullscreen window that we instantly kill to get the user's screen size
    # works with multiple screens

    width = screenSize.split("x")[0]
    height = screenSize.split("x")[1].split("+")[0]
    return width + "x" + height


def initJsonDataFile():
    if not os.path.exists("4lbion.json"):
        try:
            with open("4lbion.json", "w") as f:
                if getScreenSize() in screenRes:
                    resolution = getScreenSize()
                else:
                    resolution = "1920x1080"

                defaultSettings = {
                    "basePath": os.getcwd(),
                    "resolution": resolution,
                    "language": "English",
                    "steam": False,
                    "fullscreen": True,
                }
                json.dump(defaultSettings, f)
        except IOError:
            messagebox.showerror("4lbion - Error", "Unable to create 4lbion.json")


def getJsonData(name):
    if os.path.exists("4lbion.json"):
        with open("4lbion.json") as f:
            settings = json.load(f)

            if name in settings:
                return settings[name]
            else:
                messagebox.showwarning("4lbion - Internal Error", "Internal error")
    else:
        initJsonDataFile()
        return getJsonData(name)
        # if 4lbion.json doesn't exist we init it and re run the function


def editJsonData(basePath, resolution, language, steam, fullscreen):
    if os.path.exists("4lbion.json"):
        try:
            if not resolution == getJsonData("resolution"):
                messagebox.showwarning("4lbion - Warning", "Please restart 4lbion")
            elif not basePath == getJsonData("basePath"):
                messagebox.showwarning("4lbion - Warning", "Please restart 4lbion")

            with open("4lbion.json", "w") as settingsFile:
                settings = {
                    "basePath": basePath,
                    "resolution": resolution,
                    "language": language,
                    "steam": steam,
                    "fullscreen": fullscreen,
                }

                json.dump(settings, settingsFile)
        except IOError:
            messagebox.showerror("4lbion - Error", "Unable to edit 4lbion.json")


def getOS():
    if platform.system() == "Windows":
        return "win32"
    if platform.system() == "Linux":
        return "linux"
    if platform.system() == "Darwin":
        return "macosx"
    else:
        return "win32"
    # this function returns the OS as SBI's servers names them


def getGameVersion():
    try:
        versionFile = open(path + "/version.txt").read()
        prefixSize = len("albiononline-" + getOS() + "-full-")

        return versionFile[prefixSize:].strip("\n")
    except FileNotFoundError:
        return "0.0.0.0"


def checkStatus():
    statusAdresses = [
        "http://serverstatus.albiononline.com/",  # default used by official launcher
        "https://status.albiononline.com/status_live.txt",
        "https://live.albiononline.com/status.txt",
    ]
    # this array is totally useless but well it's there lmao

    r = requests.get("https://" + server + "/status.txt", headers=curlHeaders)
    content = json.loads(r.text)

    status = content[0]
    message = content[1]

    return status, message


def getLauncherBackground():
    global url
    if not os.path.exists("background.gif"):
        regexp = r"background-image: url(.*)"
        try:
            r = requests.get(
                "https://assets.albiononline.com/launcher/EN", headers=curlHeaders
            )
        except requests.exceptions:
            messagebox.showerror(
                "4lbion - Error",
                "Unable to access https://assets.albiononline.com/launcher/EN",
            )
            sys.exit(1)

        html = r.text

        if re.search(regexp, html):
            matches = re.finditer(regexp, r.text, re.MULTILINE)

            for matchNum, match in enumerate(matches, start=1):
                url = (
                    "htt"
                    + match.group().strip(
                        '<div class="launcher" style="background-image: url("'
                    )[:-3]
                )
                # ok do not ask me anything about this line lmfao
                break
                # strange way but we get the content of style tag to scrap the image url
            with open("background.jpeg", "wb") as f:
                try:
                    r = requests.get(url, headers=curlHeaders)
                except requests.exceptions:
                    messagebox.showerror("4lbion - Error", "Unable to download " + url)
                    sys.exit(1)
                f.write(r.content)

            clip = ImageSequenceClip(["background.jpeg"], fps=1).resize(width=700)
            clip.write_gif("background.gif")
            # we resize the background image and transform it in gif so that Tkinter can read it

            os.remove("background.jpeg")
            # we delete the old file because it's useless now


def connectedPlayers():
    # we will get this data from Steam so it doesn't reflect the real number of connected players

    if server == "live.albiononline.com":
        onlinePlayersJsonUrl = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid=761890"

        try:
            r = requests.get(onlinePlayersJsonUrl, headers=curlHeaders)
            onlinePlayers = json.loads(r.text)["response"]["player_count"]
            return f"{onlinePlayers:,}"
            # format it so it has thousands separators
        except:
            return "Unknown"
    else:
        return "Unknown"


if (
    not platform.system() == "Windows"
    and not platform.system() == "Linux"
    and not platform.system() == "Darwin"
):
    warn = messagebox.askokcancel(
        "4lbion - Error",
        "Your OS ("
        + platform.system()
        + ") is not officialy supported by Albion Online nor 4lbion",
    )
    if not warn:
        # if user pushes "cancel"
        sys.exit(1)

if not sys.maxsize > 2 ** 32:
    messagebox.showerror(
        "4lbion - Error", "You need a 64bits processor to run Albion Online"
    )
    sys.exit(1)
# in the last 2 if statements we test the user's system to know if the computer is supported by Albion

basePath = getJsonData("basePath")

server = "live.albiononline.com"
loginServer = "loginserver.live.albion.zone:5055"
path = basePath + "/game_x64"

servers = {
    "Live": [
        "live.albiononline.com",
        "loginserver.live.albion.zone:5055",
        basePath + "/game_x64",
    ],
    "Test": [
        "staging.albiononline.com",
        "stagingserver.albiononline.com:5055",
        basePath + "/staging_x64",
    ],
    "Playground": [
        "playground.albiononline.com",
        "playgroundserver.albiononline.com:5055",
        basePath + "/playground_x64",
    ]
    # 0: server, 1: loginServer, 2: path
}
serversArray = ["Live", "Test", "Playground"]


# Non-exhaustive list of officials servers/login servers
# live.albiononline.com         | loginserver.live.albion.zone:5055         | Main server
# staging.albiononline.com      | stagingserver.albiononline.com:5055       | Test server
# playground.albiononline.com   | playgroundserver.albiononline.com:5055    | Playground server (apparently for Wiki editors)
# clients.nightly.albion.zone   | clients.nightly.albion.zone:5055          | Internal server, DNS doesn't resolve


class fourlbion:
    def __init__(self, master):
        self.master = master
        self.master.title("4lbion " + version)
        self.master.minsize(700, 415)
        self.master.resizable(False, False)
        # creation of a 700x420 window not resizable

        getLauncherBackground()

        try:
            bg = PhotoImage(file="background.gif")  # Tkinter forces us to use GIF
            bgLabel = Label(self.master, image=bg)
            bgLabel.photo = bg
            backgroundSet = True
            # here we scrap the background of the official launcher and we use it for our background
        except TclError:
            backgroundSet = False
            messagebox.showwarning("4lbion - Warning", "Unable to load background.gif")

        self.connectedVar = StringVar()
        self.connectedVar.set(connectedPlayers() + " players online")
        self.connectedLabel = Label(master, textvariable=self.connectedVar)

        self.gameVersionVar = StringVar()
        self.gameVersionVar.set(
            "Game version: " + getGameVersion() + " (" + getOS() + ")"
        )
        self.gameVersionLabel = Label(master, textvariable=self.gameVersionVar)

        self.downloadProgress = tkinter.ttk.Progressbar(
            root, orient=HORIZONTAL, length=500
        )
        # to update it: self.downloadProgress['value'] = x (in percentage)

        self.downloadVar = StringVar()
        self.downloadLabel = Label(master, textvariable=self.downloadVar)

        self.serverVar = StringVar()
        self.serverVar.set("Live")
        self.serverMenu = OptionMenu(
            root, self.serverVar, *serversArray, command=self.changeServerVars
        )
        self.serverMenu.config(height=1, width=12)
        # entry for server's address

        self.playButton = Button(
            master,
            text="Play",
            command=lambda: threading.Thread(target=self.startGame).start(),
            height=2,
            width=14,
        )
        # play btn
        # put game in another thread so that we can close the launcher while albion is running

        self.settingsButton = Button(
            master, text="⚙", command=self.settingsWindow, height=2, width=2
        )
        # btn to start the settings window

        if backgroundSet:
            bgLabel.place(x=0, y=0, relwidth=1, relheight=1)

        self.connectedLabel.place(relx=0, rely=0, anchor="nw")
        self.gameVersionLabel.pack(anchor="ne")

        self.downloadProgress.place(x=5, y=390)
        self.downloadLabel.place(x=5, y=370)

        self.serverMenu.place(x=560, y=345)
        self.playButton.place(x=560, y=375)
        self.settingsButton.place(x=510, y=375)
        # pack everything on the window

        threading.Thread(target=self.updater, args=(False,)).start()
        # now update the game

    def settingsWindow(self):
        self.settings = Toplevel(self.master)
        self.settings.title("4lbion - Settings")
        self.settings.minsize(280, 230)
        self.settings.resizable(False, False)
        # creation of a 280x230 window not resizable

        self.pathVar = StringVar()
        self.pathVar.set(getJsonData("basePath"))
        self.pathButton = Button(
            self.settings,
            command=lambda: self.pathVar.set(
                filedialog.askdirectory(initialdir=getJsonData("basePath"))
            ),
            text="Choose Game Path",
        )
        self.pathButton.config(height=1, width=30)
        # path entry and label

        self.resLabel = Label(self.settings, text="Game Resolution")

        self.resVar = StringVar()
        self.resVar.set(getJsonData("resolution"))
        self.resMenu = OptionMenu(self.settings, self.resVar, *screenRes)
        self.resMenu.config(height=1, width=12)
        # resolution menu and label

        self.langLabel = Label(self.settings, text="Game Language")

        self.langVar = StringVar()
        self.langVar.set(getJsonData("language"))
        self.langMenu = OptionMenu(self.settings, self.langVar, *languagesArray)
        self.langMenu.config(height=1, width=12)
        # language menu and label

        self.steamLabel = Label(self.settings, text="use SteamAPI ?")

        self.steamVar = BooleanVar()
        self.steamVar.set(getJsonData("steam"))
        self.steamCheck = Checkbutton(self.settings, variable=self.steamVar)
        # SteamAPI checkbutton and label

        self.fullscreenLabel = Label(self.settings, text="Fullscreen")

        self.fullscreenVar = BooleanVar()
        self.fullscreenVar.set(getJsonData("fullscreen"))
        self.fullscreenCheck = Checkbutton(self.settings, variable=self.fullscreenVar)
        # fullscreen checkbutton and label

        self.updateButton = Button(
            self.settings,
            text="Force checking for update",
            command=lambda: threading.Thread(target=self.updater, args=(True,)).start(),
        )
        self.updateButton.config(height=1, width=30)

        self.applyButton = Button(
            self.settings,
            text="Apply",
            command=lambda: editJsonData(
                self.pathVar.get(),
                self.resVar.get(),
                self.langVar.get(),
                self.steamVar.get(),
                self.fullscreenVar.get(),
            ),
            height=1,
            width=8,
        )

        self.pathButton.place(x=5, y=5)

        self.resLabel.place(x=5, y=47)
        self.resMenu.place(x=125, y=40)

        self.langLabel.place(x=5, y=82)
        self.langMenu.place(x=125, y=75)

        self.steamLabel.place(x=5, y=110)
        self.steamCheck.place(x=125, y=110)

        self.fullscreenLabel.place(x=5, y=130)
        self.fullscreenCheck.place(x=125, y=130)

        self.updateButton.place(x=5, y=160)

        self.applyButton.place(x=100, y=200)

    def updater(self, force):
        self.serverMenu.config(state="disabled")
        self.connectedVar.set(connectedPlayers() + " players online")
        self.playButton.config(state="disabled", text="Checking...")
        # here we update and disable everything that could lead to a bug
        self.downloadProgress["value"] = 0

        manifestUrl = "https://" + server + "/autoupdate/manifest.xml"

        self.downloadProgress["value"] = 0

        r = requests.get(manifestUrl, headers=curlHeaders)
        manifestXml = r.text
        manifestXml = xmltodict.parse(manifestXml)

        # fmt:off
        lastVersion = manifestXml["patchsitemanifest"]["albiononline"][getOS()]["fullinstall"]["@version"]
        # fmt:on

        localVersion = getGameVersion()

        if force or not lastVersion == localVersion:
            self.playButton.config(state="disabled", text="Update Required !")
            self.downloadProgress["value"] = 0

            tocURL = (
                "https://"
                + server
                + "/autoupdate/perfileupdate/"
                + getOS()
                + "_"
                + lastVersion
                + "/toc_"
                + getOS()
                + ".xml"
            )
            # example url: https://live.albiononline.com/autoupdate/perfileupdate/linux_1.16.396.166022/toc_linux.xml

            r = requests.get(tocURL, headers=curlHeaders)
            tocXml = r.text
            tocXml = xmltodict.parse(tocXml)

            oldPath = os.getcwd()
            os.chdir(path)

            i = 0
            for file in tocXml["toc"]["file"]:
                filePath = file["@path"][:-4]  # -4 because we remove the ".zip"
                fileMd5 = file["@md5"]

                self.downloadVar.set("Checking " + filePath + "...")
                percentage = (i / len(tocXml["toc"]["file"])) * 100
                self.downloadProgress["value"] = percentage

                if (
                    not os.path.exists(filePath)
                    or not md5(open(filePath, "rb").read()).hexdigest() == fileMd5
                ):
                    self.downloadVar.set("Downloading " + filePath + "...")
                    fileToDownloadURL = (
                        "https://"
                        + server
                        + "/autoupdate/perfileupdate/"
                        + getOS()
                        + "_"
                        + lastVersion
                        + "/"
                        + filePath
                        + ".zip"
                    )

                    fileToDownloadZip = requests.get(fileToDownloadURL)
                    open("temp.zip", "wb").write(fileToDownloadZip.content)

                    with ZipFile("temp.zip", "r") as tempZip:
                        self.downloadVar.set("Extracting " + filePath + "...")
                        tempZip.extractall()
                        try:
                            os.replace(tempZip.namelist()[0], filePath)
                        except FileNotFoundError:
                            pathToCreate = "."
                            for folder in filePath.split("/")[-1]:
                                pathToCreate += folder
                            os.makedirs(pathToCreate)

                    os.remove("temp.zip")
                i += 1

            self.downloadVar.set("")
            os.chdir(oldPath)

        self.gameVersionVar.set(
            "Game version: " + getGameVersion() + " (" + getOS() + ")"
        )
        self.downloadProgress["value"] = 100
        self.playButton.config(state="normal", text="Play")
        self.serverMenu.config(state="normal")

    def changeServerVars(self, event):
        global server, loginServer, path

        threading.Thread(target=self.updater, args=(False,)).start()

        server = servers[self.serverVar.get()][0]
        loginServer = servers[self.serverVar.get()][1]
        path = servers[self.serverVar.get()][2]

        self.gameVersionVar.set(
            "Game version: " + getGameVersion() + " (" + getOS() + ")"
        )

    def startGame(self):
        width = getJsonData("resolution").split("x")[0]
        height = getJsonData("resolution").split("x")[1]
        # extract width and height from resolution

        if getJsonData("fullscreen"):
            windowMode = '"-screen-fullscreen 1" +fullscreen'
        else:
            windowMode = "+windowed"

        if os.path.exists(path + "/Albion-Online"):
            oldWorkingDir = os.getcwd()
            os.chdir(path)
            os.system(
                '"'
                + path
                + '/Albion-Online" '
                + windowMode
                + " -screen-width "
                + width
                + " -screen-height "
                + height
                + " +lang "
                + languages[getJsonData("language")]
                + " +server "
                + loginServer
            )
            os.chdir(oldWorkingDir)
            # command is very strange but it's very close to what the official launcher is doing
        else:
            messagebox.showwarning(
                "4lbion - Error",
                "Game path is invalid\n(Unable to find "
                + path
                + "/Albion-Online on your disk)",
            )


try:
    root = Tk()
    window = fourlbion(root)
    root.mainloop()
except KeyboardInterrupt:
    sys.exit(0)
