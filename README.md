# Governor

A Discord experience and leveling bot, designed to be used with the Stardew Valley server.

Written by aquova, 2020

https://github.com/aquova/governor

https://discord.gg/stardewvalley

## Overview

This bot was written as a replacement for the SDV server's previous XP bot, Mayor Lewis.

My personal hosting of the bot will be private, but users are free to host a version of the bot themselves.

## Installation

- Running the Discord bot itself requires Python 3. The Python libraries needed can be installed via: `python3 -m pip install -r requirements.txt`

- In order to run the leaderboard page on a webserver, PHP must be installed, along with the php-json, and php-sqlite3 packages.

## TODO

- [x] Deliver XP with 1 minute cooldown
- [x] Give ranks & roles upon level up
    - [x] Import from Mayor Lewis
- [ ] Display image with user avatar and level
- [x] Online leaderboard
- [ ] Custom commands
    - [x] Basic support
    - [x] Import from Mayor Lewis
    - [x] Support for mentioning a user in command
    - [ ] Add permissions so not anyone can add a command
    - [ ] Add ability to remove commands
- [ ] Speak through bot
- [ ] Easy setup script
- [ ] Event utilities
- [ ] Badge Overhaul
