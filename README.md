# Governor

A Discord experience and leveling bot, designed to be used with the Stardew Valley server.

Written by aquova, 2020-2021

https://github.com/aquova/governor

https://discord.gg/stardewvalley

## Overview

This bot was written as a replacement for the SDV server's previous XP bot, Mayor Lewis.

My personal hosting of the bot will be private, but users are free to host a version of the bot themselves.

## Installation

- For the bot to run, `ranks.json` and `config.json` files must be created and placed in the `private` directory. These establish the settings for the bot. Examples are currently not provided, but they must match the layout specified in `src/config.py` and other files.

- A Dockerfile is provided for running the bot within a Linux container, as well as a simple script `docker_run.sh` for running.

- This bot has a sister project - https://github.com/aquova/stardew.chat - which presents user leaderboards and custom commands to be presented as a webpage.
