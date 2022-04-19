# 4lbion
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a> [![CodeFactor](https://www.codefactor.io/repository/github/jusdepatate/4lbion/badge/master)](https://www.codefactor.io/repository/github/jusdepatate/4lbion/overview/master)
<br>Custom launcher/game updater for Albion Online.
<br>**It doesn't offers cheat or injection or anything, it isn't mean to be better than the official launcher, it's just a training in Python.**
<br>I managed to understand how the launcher updates itself and the game and how it downloads/checks files so I had the idea to make my own version in Tkinter/Python3... Tkinter isn't the best GUI builder but at least it works :D.

Reading the source code can lead to several headaches and mental health problems.

**Online player number is scraped from Steam not from Albion it is not really representative**

This software or the author are not affiliated with Sandbox Interactive.

## Installation
First, install Python3 and Tkinter
```
git clone https://github.com/jusdepatate/4lbion.git
cd 4lbion
pip install -r requirements.py
python3 4lbion.py
```
You can take [4lbion.desktop](4lbion.desktop) as a good example of a desktop launcher for 4lbion.

#### `Albion-Online_Data/resources.assets.resS` takes a while to download/check, why ?
This file is pretty big (1.8Go at time of writing), so it is normal for it to take a while.

## Tested on
- Manjaro 19 -> 21
- Windows 10 -> 11
- Debian 11

## Configuration
Everything happens in `4lbion.json` in the working directory.

 - Very rare case:
 
You might want to use WSL to test compatibility between Windows and Linux, in this case, make sure you are always executing 4lbion from the same folder and change `basePath` to `.` in `4lbion.json`.