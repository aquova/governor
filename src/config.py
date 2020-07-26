from datetime import datetime
import json

XP_PER_LVL = 300
PLACEHOLDER_TOKEN = "YOUR DISCORD TOKEN HERE"
DEFAULT_CONFIG_SETTING = 0

# Read values from config file
with open('private/config.json') as config_file:
    cfg = json.load(config_file)

DISCORD_KEY = cfg['discord']
if DISCORD_KEY == PLACEHOLDER_TOKEN:
    print("Don't forget to set the 'discord' field in 'private/config.json' with your Discord bot key!")

DB_PATH = cfg['db_path']
CMD_PREFIX = cfg['command_prefix']
ADMIN_ACCESS = cfg['roles']['admin_access']
SERVER_URL = cfg['server_url']
OWNER = cfg['owner']
if OWNER == DEFAULT_CONFIG_SETTING:
    print("Don't forget to set the 'owner' field in 'private/config.json'!")

DEBUG_BOT = (cfg['debug'].upper() == "TRUE")

LVL_CHANS = cfg['channels']['lvl_allowed']
NO_SLOWMODE = cfg['channels']['slowmode_disabled']
XP_OFF = cfg['channels']['xp_disabled']

GAME_ANNOUNCEMENT_CHANNEL = cfg['games']['announcement_channel']
if GAME_ANNOUNCEMENT_CHANNEL == DEFAULT_CONFIG_SETTING:
    print("Don't forget to set the 'announcement_channel' field in 'private/config.json'!")

GAME_ANNOUNCE_TIME = datetime.strptime(cfg['games']['announcement_time'], "%I:%M %p")

# Event related channels
PUZZLE_EVENTS = cfg['channels']['events']['puzzle'] # Events where submissions shouldn't be seen by other members

# Import ranks from their configuration
with open(cfg['ranks_path']) as ranks_file:
    RANKS = json.load(ranks_file)['ranks']
