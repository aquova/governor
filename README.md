# Governor

A Discord experience and leveling bot, designed to be used with the Stardew Valley server.

Written by aquova, 2020

https://github.com/aquova/governor

https://discord.gg/stardewvalley

## Overview

This bot was written as a replacement for the SDV server's previous XP bot, Mayor Lewis.

My personal hosting of the bot will be private, but users are free to host a version of the bot themselves.

## Installation

- A bash script is included for automatic setup, given a Debian-based server. Simply run `./setup.sh`

- In order to run the leaderboard page on a webserver, you must symlink the `web` directory into the desired location on your publicly hosted filesystem.

## TODO

- [x] Deliver XP with 1 minute cooldown
- [x] Give ranks & roles upon level up
    - [x] Import from Mayor Lewis
- [x] Display image with user avatar and level
- [x] Online leaderboard
    - [x] Basic functionality
    - [x] Custom domain
- [x] Custom commands
    - [x] Basic support
    - [x] Import from Mayor Lewis
    - [x] Support for mentioning a user in command
    - [x] Add permissions so not anyone can add a command
    - [x] Add ability to remove commands
- [x] Speak through bot
- [x] Debugging instance
- [x] Easy setup script
- [ ] Event utilities
- [ ] Badge Overhaul
