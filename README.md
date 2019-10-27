[![PyPI Version](https://img.shields.io/pypi/v/lifxtools.svg)](https://pypi.python.org/pypi/lifxtools/)
[![GitHub release](https://img.shields.io/github/release-pre/drtexxofficial/lifxtools.svg)](https://GitHub.com/DrTexx/lifxtools/releases/)
[![GitHub license](https://img.shields.io/github/license/DrTexx/lifxtools.svg?branch=master)](https://github.com/DrTexx/lifxtools/blob/master/LICENSE)
[![Github all releases](https://img.shields.io/github/downloads/DrTexx/lifxtools/total.svg)](https://GitHub.com/DrTexx/lifxtools/releases/)
[![Platform: Windows,Mac,Linux](https://img.shields.io/badge/Platform-Windows%20%7C%20Mac%20%7C%20Linux-blue.svg)](#)


# lifxtools

***[DISCLAIMER]: IF YOU SUFFER PHOTOSENSITIVE EPLILEPSY, PLEASE DO NOT PLAY WITH THESE SCRIPTS. I CAN NOT GUARENTEE YOUR EPLILEPSY WILL NOT BE TRIGGERED BY A DEMO OR TECHNICAL BUG.***

_[NOTE]: This readme is a work-in-progress. If you require any specific information, please submit a github issue. I will try my best to address any questions you have in this readme once I get the chance. Thanks! :)_

_[NOTE]: For the moment, live_audio_level.py is WAAAAY less responsive on Windows than on Linux, this is being worked on._

_[NOTE]: The latest version of a dependency (PyAudio v0.2.11) doesn't support the most recent version of python (3.7.4) on Windows 10 as of this commit (2019/10/07 @ 07:75PM)_

_[NOTE]: Mac requires a method to pipe your desktop audio into an audio input, soundflower can be used for this_

## Starting scripts
1. Ensure you've navigated to the root of the repo after cloning

### GUI (WIP)
#### Linux
1. `python3 -m lifxtools`

### Real-time Audio Visualiser
#### Linux
1. `chmod +x live_audio_level.py` (ensure live_audio_level.py is executable)
1. `python3 -m venv venv` (set up a venv)
1. `source venv/bin/activate` (activate the venv)
1. `pip install -r requirements.txt` (install the necessary requirements)
1. `./live_audio_level.py` (launch the script)



## Notable usages
### average_screen_color.py
(Ultra-slow fade mode)
Stanley Kubrick's A Clockwork Orange is well enhanced by the effect of average_screen_color.py; first few minutes of the film are of particularly strong effect.

(Slow fade mode)
Blade Runner (1997). Movie full of both muted and vibrant tones. Takes full advantage of the vividness of the colour of lifx bulbs

(Game fade mode)
Half-Life 2: Episode 1. The first few levels of this game are truly awesome with live colour averages.

## Todo
### Public Transport API Intergration
Intergration for multiple public transport APIs. This will involve making a package to translate multiple APIs to the general format (which is likely object-based)

Planned APIs to intergrate:
- PTV (Public Transport Victoria)

### Better colours for "Dusk and Dawn" lifx bulbs
The plan:

| color condition | effect        |
| ---             | ---           |
| blue > red      | cooler light  |
| blue == red     | neutral light |
| blue < red      | warmer light  |

### Add preferences for monitor refresh related
With the addition of benchmarking capabilities available to the user, this will allow users to compare their color average processing time with the refresh rate of their displays. Ideally, this number should be as close to matching as possible (with consideration for network speed also)

### Don't send packets if colour is identical to last sent colour
This has the intention of saving network bandwidth (and potenially a small amount of processing time)

### Add firewall issue detection
Add tests for if a firewall is in place and whether it may cause issues for the scripts, if it's detected that it will, return a verbose error to the user to help them rectify the issue.
