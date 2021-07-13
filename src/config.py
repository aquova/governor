from datetime import datetime
import discord, json

XP_PER_MINUTE = 10
XP_PER_LVL = 300
STARTING_XP = XP_PER_LVL

# Read values from config file
config_path = "/private/config.json"
with open(config_path) as config_file:
    cfg = json.load(config_file)

DISCORD_KEY = cfg['discord']
DB_PATH = "/private/governor.db"
ASSETS_PATH = "/governor/assets"
FONTS_PATH = "/governor/fonts"
TMP_PATH = "/private/tmp"
CMD_PREFIX = cfg['command_prefix']
ADMIN_ACCESS = cfg['roles']['admin_access']
SERVER_URL = cfg['server_url']
OWNER = cfg['owner']
DEBUG_BOT = (cfg['debug'].upper() == "TRUE")

LVL_CHANS = cfg['channels']['lvl_allowed']
NO_SLOWMODE = cfg['channels']['slowmode_disabled']
XP_OFF = cfg['channels']['xp_disabled']

GAME_ANNOUNCEMENT_CHANNEL = cfg['games']['announcement_channel']
GAME_ANNOUNCE_TIME = datetime.strptime(cfg['games']['announcement_time'], "%I:%M %p")

# Event related channels
EVENT_COORDINATOR = cfg['roles']['coordinator']
PUZZLE_EVENTS = cfg['channels']['events']['puzzle'] # Events where submissions shouldn't be seen by other members
VERIFY_EVENTS = cfg['channels']['events']['verify'] # Channel to approve event submissions
CURRENT_EVENTS = cfg['roles']['events']

# Import ranks from their configuration
ranks_path = "/private/ranks.json"
with open(ranks_path) as ranks_file:
    RANKS = json.load(ranks_file)['ranks']

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)
