import json
from datetime import datetime

XP_PER_MINUTE = 10
XP_PER_LVL = 300
STARTING_XP = XP_PER_LVL

# Read values from config file
CONFIG_PATH = "./private/config.json"
with open(CONFIG_PATH) as config_file:
    cfg = json.load(config_file)

DISCORD_KEY = cfg['discord']
DB_PATH = "./private/governor.db"
ASSETS_PATH = "./assets"
FONTS_PATH = "./fonts"
TMP_PATH = "./private/tmp"
CMD_PREFIX = cfg['command_prefix']

ADMIN_ACCESS = cfg['roles']['admin_access']
MODDER_ROLE = cfg['roles']['modder']
MODDER_URL = cfg['modder_wiki_url']

SERVER_URL = cfg['server_url']
DEBUG_BOT = cfg['debug']

NO_SLOWMODE = cfg['channels']['slowmode_disabled']
XP_OFF = cfg['channels']['xp_disabled']
LOG_CHAN = cfg['channels']['log']
LIMIT_CHANS = cfg['channels']['limited']

GAME_ANNOUNCEMENT_CHANNEL = cfg['games']['announcement_channel']
AUTO_ADD_EPIC_GAMES = cfg['games']['auto_add_epic_games']
GAME_ANNOUNCE_TIME = datetime.strptime(cfg['games']['announcement_time'], "%I:%M %p").time()

PC_PLATFORM = cfg['roles']['platforms']['pc']
XBOX_PLATFORM = cfg['roles']['platforms']['xbox']
PS_PLATFORM = cfg['roles']['platforms']['ps']
NS_PLATFORM = cfg['roles']['platforms']['ns']
MOBILE_PLATFORM = cfg['roles']['platforms']['mobile']
VITA_PLATFORM = cfg['roles']['platforms']['vita']

# Import ranks from their configuration
RANKS_PATH = "./private/ranks.json"
with open(RANKS_PATH) as ranks_file:
    RANKS = json.load(ranks_file)['ranks']
