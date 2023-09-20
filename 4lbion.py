#!/usr/bin/env python3
# 4lbion - Open Source launcher for Albion Online
# Jus de Patate_ | ign: jusdepatate | jusdepatate@protonmail.com - 2020 - 2022

try:
    # Native libs
    import os
    import sys
    import json
    import re
    import platform
    import threading
    import subprocess
    import stat
    import datetime
    import hashlib
    import zipfile

    # PyPi libs
    import PIL.Image
    import requests
    import xmltodict
except ImportError:
    print(
        "Unable to import at least one package, did you install all required Pip packages ?"
    )
    sys.exit(1)

try:
    import tkinter
    import tkinter.ttk
    import tkinter.messagebox
    import tkinter.filedialog

    # We import tkinter to create GUI
except ImportError:
    print("Unable to import Tkinter, is it installed ? Are you running Py3.x ?")
    sys.exit(1)

try:
    if platform.system() == "Darwin":
        import PyTouchBar

        touch_bar = True
        # Nice useless feature :)
    else:
        touch_bar = False
except ImportError:
    touch_bar = False
    pass

screen_res = [
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

languages_array = [
    "English",
    "Espanol",
    "Deutsche",
    "Francais",
    "Russian",
    "Polskie",
    "Portugues (Brasil)",
]

curl_headers = {
    # Exact same headers as the official launcher has
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en,*",
    "User-Agent": "Mozilla/5.0",
}

launcher_path = os.getcwd()


def get_screen_size():
    temp_window = tkinter.Tk()
    temp_window.update_idletasks()
    temp_window.attributes("-fullscreen", True)
    temp_window.state("iconic")
    screen_size = temp_window.winfo_geometry()
    temp_window.destroy()
    # we create a fullscreen window that we instantly kill to get the user's screen size
    # works with multiple screens

    width = screen_size.split("x")[0]
    height = screen_size.split("x")[1].split("+")[0]
    return width + "x" + height


def init_json_data_file():
    if not os.path.exists(launcher_path + "/4lbion.json"):
        try:
            with open(launcher_path + "/4lbion.json", "w") as f:
                if get_screen_size() in screen_res:
                    resolution = get_screen_size()
                else:
                    resolution = "1920x1080"

                default_settings = {
                    "basePath": os.getcwd(),
                    "resolution": resolution,
                    "language": "English",
                    "steam": False,
                    "fullscreen": True,
                }
                json.dump(default_settings, f)
        except IOError:
            tkinter.messagebox.showerror(
                "4lbion - Error", "Unable to create 4lbion.json"
            )


def get_json_data(name):
    if os.path.exists(launcher_path + "/4lbion.json"):
        with open(launcher_path + "/4lbion.json") as f:
            settings = json.load(f)

            if name in settings:
                return settings[name]
            else:
                tkinter.messagebox.showwarning(
                    "4lbion - Internal Error", "Internal error"
                )
    else:
        init_json_data_file()
        return get_json_data(name)
        # if 4lbion.json doesn't exist we init it and re run the function


def edit_json_data(resolution, language, steam, fullscreen):
    if os.path.exists(launcher_path + "/4lbion.json"):
        try:
            if not resolution == get_json_data("resolution"):
                tkinter.messagebox.showwarning(
                    "4lbion - Warning", "Please restart 4lbion"
                )
            elif not base_path == get_json_data("basePath"):
                tkinter.messagebox.showwarning(
                    "4lbion - Warning", "Please restart 4lbion"
                )

            with open(launcher_path + "/4lbion.json", "w") as settingsFile:
                settings = {
                    "basePath": base_path,
                    "resolution": resolution,
                    "language": language,
                    "steam": steam,
                    "fullscreen": fullscreen,
                }

                json.dump(settings, settingsFile)
        except IOError:
            tkinter.messagebox.showerror("4lbion - Error", "Unable to edit 4lbion.json")


def get_os():
    # this function returns the OS as SBI's servers names them
    if platform.system() == "Windows":
        return "win32"
    if platform.system() == "Linux":
        return "linux"
    if platform.system() == "Darwin":
        return "macosx"
    else:
        tkinter.messagebox.showwarning(
            "4lbion - Error",
            "Your OS ("
            + platform.system()
            + ") is not officialy supported by Albion Online nor 4lbion",
        )
        return "win32"
        # lets assume that unsupported OSes are gonna be using Wine or equivalent


def get_game_version():
    try:
        if get_os() == "macosx":
            game_version = open(
                path + "/Albion-Online.app/Contents/Resources" + "/version.txt"
            ).read()
        else:
            game_version = open(path + "/version.txt").read()

        prefix_size = len("albiononline-" + get_os() + "-full-")

        return game_version[prefix_size:].strip("\n")
    except FileNotFoundError:
        return "0.0.0.0"


def check_status():
    status_addresses = [
        "https://serverstatus.albiononline.com/",  # default used by official launcher for server Live
        "https://status.albiononline.com/status_live.txt",  # timestamp says last update was in 2020
    ]
    # this array is totally useless but well it's there lmao

    if server != "live.albiononline.com":
        return True
    # Apparently we have no way to check if other servers are up

    r = requests.get(
        status_addresses[0],
        headers=curl_headers,
    )
    content = json.loads(r.text)

    status = content["status"]

    if status == "online":
        return True
    else:
        return False


def get_launcher_background():
    if not os.path.exists("background.gif"):
        regexp = r"background-image: url(.*)"
        try:
            r = requests.get(
                "https://assets.albiononline.com/launcher/EN", headers=curl_headers
            )
        except requests.exceptions:
            tkinter.messagebox.showerror(
                "4lbion - Error",
                "Unable to access https://assets.albiononline.com/launcher/EN",
            )
            return False

        html = r.text

        if re.search(regexp, html):
            url = ""
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
                    r = requests.get(url, headers=curl_headers)
                except requests.exceptions:
                    tkinter.messagebox.showerror(
                        "4lbion - Error", "Unable to download " + url
                    )
                    sys.exit(1)
                f.write(r.content)

            img = PIL.Image.open("background.jpeg")

            img.thumbnail((700, 415), 0)  # 0 = BEST QUALITY
            img.save("background.gif")
            # we resize the background image and transform it in gif so that Tkinter can read it

            os.remove("background.jpeg")
            # we delete the old file because it's useless now
    else:
        today = datetime.datetime.today()
        background_dl_date = datetime.datetime.fromtimestamp(
            os.path.getmtime("background.gif")
        )
        duration = today - background_dl_date
        if duration.days >= 30:
            os.unlink("background.gif")
            get_launcher_background()
        # If background is older than a month, remove it and rerun function


def connected_players():
    # Scrap connected player count from Steam

    if server == "live.albiononline.com":
        online_players_json_url = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid=761890"

        try:
            r = requests.get(online_players_json_url, headers=curl_headers)
            r.raise_for_status()
            online_players = json.loads(r.text)["response"]["player_count"]
            return f"{online_players:,}"
            # format it so it has thousands separators
        except:
            return "Unknown"
    else:
        return "Unknown"


base_path = get_json_data("basePath")

server = "live.albiononline.com"
loginServer = "loginserver.live.albion.zone:5055"
path = base_path + "/game_x64"

if get_os() == "win32":
    exe = "Albion-Online.exe"
elif get_os() == "linux":
    exe = "Albion-Online"
elif get_os() == "macosx":
    exe = "Albion-Online.app"


servers = {
    "Live": [
        "live.albiononline.com",
        "loginserver.live.albion.zone:5055",
        base_path + "/game_x64",
    ],
    "Test": [
        "staging.albiononline.com",
        "stagingserver.albiononline.com:5055",
        base_path + "/staging_x64",
    ],
    "Playground": [
        "playground.albiononline.com",
        "playgroundserver.albiononline.com:5055",
        base_path + "/playground_x64",
    ]
    # 0: server, 1: loginServer, 2: path
}
servers_array = ["Live", "Test", "Playground"]


# Non-exhaustive list of officials servers/login servers
# live.albiononline.com         | loginserver.live.albion.zone:5055         | Main server
# staging.albiononline.com      | stagingserver.albiononline.com:5055       | Test server
# playground.albiononline.com   | playgroundserver.albiononline.com:5055    | Playground server (apparently for Wiki editors)
# clients.nightly.albion.zone   | clients.nightly.albion.zone:5055          | Internal server, DNS doesn't resolve


def start_game():
    width = get_json_data("resolution").split("x")[0]
    height = get_json_data("resolution").split("x")[1]
    # extract width and height from resolution

    if get_json_data("fullscreen"):
        window_mode = "+borderlessfullscreenwindow"
    else:
        window_mode = "+windowed"

    if os.path.exists(path + "/" + exe):
        old_working_dir = os.getcwd()
        os.chdir(path)
        prefix = ""
        arg = " "
        if get_os() == "macosx":
            prefix = "open "
            arg = " --args "
        subprocess.call(
            prefix
            + '"'
            + path
            + "/"
            + exe
            + '"'
            + arg
            + window_mode
            + " -screen-width "
            + width
            + " -screen-height "
            + height
            + " +lang "
            + languages[get_json_data("language")]
            + " +server "
            + loginServer,
            shell=True,
        )
        os.chdir(old_working_dir)
        # command is very strange but it's very close to what the official launcher is doing
    else:
        tkinter.messagebox.showwarning(
            "4lbion - Error",
            "Game path is invalid\n(Unable to find "
            + path
            + "/"
            + exe
            + " on your disk)",
        )


class fourAlbion:
    def __init__(self, master):
        self.master = master
        self.master.title("4lbion Game Launcher")
        self.master.minsize(640, 415)
        self.master.lift()
        # creation of a window and put in on the top

        get_launcher_background()

        bg_label = tkinter.Label(self.master)
        try:
            bg = tkinter.PhotoImage(
                file="background.gif"
            )  # Tkinter forces us to use GIF
            bg_label = tkinter.Label(self.master, image=bg)
            bg_label.photo = bg
            background_set = True
            # here we scrap the background of the official launcher and use it for our background
        except tkinter.TclError:
            background_set = False
            tkinter.messagebox.showwarning(
                "4lbion - Warning", "Unable to load background.gif"
            )

        self.top_bar = tkinter.Frame(self.master)

        self.connected_var = tkinter.StringVar()
        self.connected_var.set(connected_players() + " players online (Steam)")
        self.connected_label = tkinter.Label(
            self.top_bar, textvariable=self.connected_var
        )

        self.game_version_var = tkinter.StringVar()
        self.game_version_var.set(
            "Game version: " + get_game_version() + " (" + get_os() + ")"
        )
        self.game_version_label = tkinter.Label(
            self.top_bar, textvariable=self.game_version_var
        )

        self.bot_frame = tkinter.Frame(self.master)

        self.dw_frame = tkinter.Frame(self.bot_frame)
        self.dw_frame_l1 = tkinter.Frame(self.dw_frame)
        self.download_var = tkinter.StringVar()
        self.download_label = tkinter.Label(
            self.dw_frame_l1, textvariable=self.download_var, width=50
        )

        self.dw_frame_line2 = tkinter.Frame(self.dw_frame)
        self.download_progress = tkinter.ttk.Progressbar(
            self.dw_frame_line2,
            orient=tkinter.HORIZONTAL,
            length=500,
            mode="determinate",
        )
        # to update it: self.downloadProgress['value'] = x (in percentage)

        self.server_frame = tkinter.Frame(self.bot_frame)

        self.server_frame_line1 = tkinter.Frame(self.server_frame)
        self.server_var = tkinter.StringVar()
        self.server_var.set("Live")
        self.server_menu = tkinter.OptionMenu(
            self.server_frame_line1,
            self.server_var,
            *servers_array,
            command=self.change_server_vars,
        )
        self.server_menu.config(height=1, width=15)
        # entry for server's address

        self.server_frame_line2 = tkinter.Frame(self.server_frame)
        self.play_button = tkinter.Button(
            self.server_frame_line2,
            text="Play",
            command=threading.Thread(target=start_game).start,
            height=2,
            width=14,
        )
        # play btn
        # put game in a none daemon thread so that we can close the launcher while albion is running

        self.settings_button = tkinter.Button(
            self.server_frame_line2,
            text="⚙",
            command=self.settings_window,
            height=2,
            width=2,
        )
        # btn to start the settings window

        if background_set:
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.top_bar.pack(side=tkinter.TOP, fill=tkinter.X)
        self.connected_label.pack(side=tkinter.LEFT)
        self.game_version_label.pack(side=tkinter.RIGHT)
        # pack top_bar and children

        self.bot_frame.pack(side=tkinter.BOTTOM, fill=tkinter.X)

        self.dw_frame.pack(side=tkinter.LEFT)
        self.dw_frame_l1.pack(side=tkinter.TOP, fill=tkinter.X)
        self.download_label.pack(side=tkinter.TOP, fill=tkinter.X)
        self.dw_frame_line2.pack(side=tkinter.BOTTOM, fill=tkinter.X)
        self.download_progress.pack(side=tkinter.BOTTOM, ipady=13)
        # pack dwFrame and children

        self.server_frame.pack(side=tkinter.RIGHT)
        self.server_frame_line1.pack(side=tkinter.TOP)
        self.server_menu.pack(side=tkinter.RIGHT)
        self.server_frame_line2.pack(side=tkinter.BOTTOM)
        self.settings_button.pack(side=tkinter.LEFT)
        self.play_button.pack(side=tkinter.RIGHT, fill=tkinter.X)
        # pack serverFrame and children

        self.update_thread = threading.Thread(target=self.updater, args=(False,))
        self.update_thread.daemon = True
        # Doing this so the thread will stop when the launcher stops
        self.update_thread.start()
        # now update the game

        if touch_bar:
            play_button = PyTouchBar.TouchBarItems.Button(
                title="Play !", action=self.tb_play
            )
            settings_button = PyTouchBar.TouchBarItems.Button(
                title="⚙️", action=self.settings_window
            )

            PyTouchBar.set_touchbar([play_button, settings_button])

    def tb_play(self, event):
        # this function only exists to make sure that we are supposed to start the game when pressing on Mac Touch Bar
        if self.play_button["state"] == tkinter.NORMAL:
            start_game()

    def settings_window(self, tb=False):
        settings = tkinter.Toplevel(self.master)
        settings.title("4lbion - Settings")
        settings.minsize(170, 160)
        settings.resizable(False, False)
        settings.lift()
        # creation of secondary window for settings

        line1 = tkinter.Frame(settings)
        path_var = tkinter.StringVar()
        path_var.set(get_json_data("basePath"))
        path_button = tkinter.Button(
            line1,
            command=lambda: path_var.set(
                tkinter.filedialog.askdirectory(initialdir=get_json_data("basePath"))
            ),
            text="Choose Game Path",
        )
        path_button.config(height=1, width=30)
        # path entry and label

        line2 = tkinter.Frame(settings)
        res_label = tkinter.Label(line2, text="Game Resolution")

        res_var = tkinter.StringVar()
        res_var.set(get_json_data("resolution"))
        res_menu = tkinter.OptionMenu(line2, res_var, *screen_res)
        res_menu.config(height=1, width=12)
        # resolution menu and label

        line3 = tkinter.Frame(settings)
        lang_label = tkinter.Label(line3, text="Game Language")

        lang_var = tkinter.StringVar()
        lang_var.set(get_json_data("language"))
        lang_menu = tkinter.OptionMenu(line3, lang_var, *languages_array)
        lang_menu.config(height=1, width=12)
        # language menu and label

        line4 = tkinter.Frame(settings)
        steam_label = tkinter.Label(line4, text="use SteamAPI ?")

        steam_var = tkinter.BooleanVar()
        steam_var.set(get_json_data("steam"))
        steam_check = tkinter.Checkbutton(line4, variable=steam_var)
        # SteamAPI checkbutton and label

        line5 = tkinter.Frame(settings)
        fullscreen_label = tkinter.Label(line5, text="Fullscreen")

        fullscreen_var = tkinter.BooleanVar()
        fullscreen_var.set(get_json_data("fullscreen"))
        fullscreen_check = tkinter.Checkbutton(line5, variable=fullscreen_var)
        # fullscreen checkbutton and label

        line6 = tkinter.Frame(settings)
        update_thread = threading.Thread(target=self.updater, args=(True,))
        update_thread.daemon = True
        update_button = tkinter.Button(
            line6,
            text="Force checking for update",
            command=self.update_thread.start,
        )
        update_button.config(height=1, width=30)

        line7 = tkinter.Frame(settings)
        apply_button = tkinter.Button(
            line7,
            text="Apply",
            command=lambda: edit_json_data(
                res_var.get(), lang_var.get(), steam_var.get(), fullscreen_var.get()
            ),
            height=1,
            width=8,
        )

        line1.pack(side=tkinter.TOP, fill=tkinter.X)
        path_button.pack(side=tkinter.TOP, fill=tkinter.X)

        line2.pack(side=tkinter.TOP, fill=tkinter.X)
        res_label.pack(side=tkinter.LEFT)
        res_menu.pack(side=tkinter.RIGHT)

        line3.pack(side=tkinter.TOP, fill=tkinter.X)
        lang_label.pack(side=tkinter.LEFT)
        lang_menu.pack(side=tkinter.RIGHT)

        line4.pack(side=tkinter.TOP, fill=tkinter.X)
        steam_label.pack(side=tkinter.LEFT)
        steam_check.pack(side=tkinter.RIGHT)

        line5.pack(side=tkinter.TOP, fill=tkinter.X)
        fullscreen_label.pack(side=tkinter.LEFT)
        fullscreen_check.pack(side=tkinter.RIGHT)

        line6.pack(side=tkinter.TOP, fill=tkinter.X)
        update_button.pack(side=tkinter.TOP, fill=tkinter.X)

        line7.pack(side=tkinter.TOP, fill=tkinter.X)
        apply_button.pack(side=tkinter.TOP, fill=tkinter.X)

    def updater(self, force):
        self.server_menu.config(state="disabled")
        self.connected_var.set(connected_players() + " players online")
        self.play_button.config(state="disabled", text="Checking...")
        # here we update and disable everything that could lead to a bug
        self.download_progress["value"] = 0

        manifest_url = "https://" + server + "/autoupdate/manifest.xml"

        self.download_progress["value"] = 0

        r = requests.get(manifest_url, headers=curl_headers)
        manifest_xml = r.text
        manifest_xml = xmltodict.parse(manifest_xml)

        # fmt:off
        last_version = manifest_xml["patchsitemanifest"]["albiononline"][get_os()]["fullinstall"]["@version"]
        # fmt:on

        local_version = get_game_version()

        if force or not last_version == local_version:
            self.play_button.config(state="disabled", text="Update Required !")
            self.download_progress["value"] = 0

            toc_url = (
                "https://"
                + server
                + "/autoupdate/perfileupdate/"
                + get_os()
                + "_"
                + last_version
                + "/toc_"
                + get_os()
                + ".xml"
            )
            # example url: https://live.albiononline.com/autoupdate/perfileupdate/linux_1.16.396.166022/toc_linux.xml

            r = requests.get(toc_url, headers=curl_headers)
            toc_xml = r.text
            toc_xml = xmltodict.parse(toc_xml)

            old_path = os.getcwd()

            try:
                os.chdir(path)
            except FileNotFoundError:
                os.makedirs(path)
                os.chdir(path)

            i = 0
            for file in toc_xml["toc"]["file"]:
                file_path = file["@path"][:-4]  # -4 because we remove the ".zip"
                file_md5 = file["@md5"]

                self.download_var.set("Checking " + file_path + "...")
                percentage = (i / len(toc_xml["toc"]["file"])) * 100
                self.download_progress["value"] = percentage

                if (
                    not os.path.exists(file_path)
                    or not hashlib.md5(open(file_path, "rb").read()).hexdigest()
                    == file_md5
                ):
                    self.download_var.set("Downloading " + file_path + "...")
                    file_to_download_url = (
                        "https://"
                        + server
                        + "/autoupdate/perfileupdate/"
                        + get_os()
                        + "_"
                        + last_version
                        + "/"
                        + file_path
                        + ".zip"
                    )

                    file_to_download_zip = requests.get(file_to_download_url)
                    open("temp.zip", "wb").write(file_to_download_zip.content)

                    with zipfile.ZipFile("temp.zip", "r") as tempZip:
                        self.download_var.set("Extracting " + file_path + "...")
                        tempZip.extractall()
                        try:
                            os.replace(tempZip.namelist()[0], file_path)
                        except NotADirectoryError:
                            pass
                        except FileNotFoundError:
                            path_to_create = "./"
                            for folder in file_path.split("/")[:-1]:
                                path_to_create += folder + "/"
                            os.makedirs(path_to_create)
                            os.replace(tempZip.namelist()[0], file_path)

                    os.remove("temp.zip")
                i += 1

            self.download_var.set("")
            os.chdir(old_path)
            if get_os() == "macosx":
                os.chmod(
                    path + "/" + exe + "/Contents/MacOs/Albion Online Client", 0o744
                )
            else:
                os.chmod(path + "/" + exe, stat.S_IXUSR)
                # add execute by owner permission for the binary file

        self.game_version_var.set(
            "Game version: " + get_game_version() + " (" + get_os() + ")"
        )
        self.download_progress["value"] = 100
        self.play_button.config(state="normal", text="Play")
        self.server_menu.config(state="normal")

        if not check_status():
            self.play_button.config(state="disabled", text="Server is down")

    def change_server_vars(self, event):
        global server, loginServer, path

        update_thread = threading.Thread(target=self.updater, args=(False,))
        update_thread.daemon = True
        update_thread.start()

        server = servers[self.server_var.get()][0]
        loginServer = servers[self.server_var.get()][1]
        path = servers[self.server_var.get()][2]

        self.game_version_var.set(
            "Game version: " + get_game_version() + " (" + get_os() + ")"
        )


if __name__ == "__main__":
    try:
        root = tkinter.Tk()
        window = fourAlbion(root)
        if touch_bar:
            PyTouchBar.prepare_tk_windows([root])
        root.mainloop()
    except KeyboardInterrupt:
        sys.exit(0)
