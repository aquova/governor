# Governor

A Discord experience and leveling bot, designed to be used with the Stardew Valley server.

Written by aquova, 2020-2021

https://github.com/aquova/governor

https://stardew.chat

https://discord.gg/stardewvalley

## Overview

This bot was written as a replacement for the SDV server's previous XP bot, Mayor Lewis. It also provides a leaderboard to show the monthly and all-time most active users.

My personal hosting of the bot will be private, but users are free to host a version of the bot themselves.

## Installation

- For the bot to run, `ranks.json` and `config.json` files must be created and placed in the `private` directory. These establish the settings for the bot. Examples are currently not provided, but they must match the layout specified in `src/config.py` and other files.

- While it is possible to run this directly on a machine, the full system can be run within Docker. Simply install both `Docker` and `Docker-Compose`, then start the project with `docker-compose up`. This will initiate both the bot, as well as a webserver hosting the leaderboard. You will need to provide your own `site.conf` file with your Nginx configuration.
