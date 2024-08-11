import yaml
from datetime import datetime

XP_PER_MINUTE = 10
XP_PER_LVL = 300
STARTING_XP = XP_PER_LVL

# Read values from config file
CONFIG_PATH = "private/config.yaml"
with open(CONFIG_PATH) as config_file:
    cfg = yaml.safe_load(config_file)

DISCORD_KEY = cfg['discord']
DB_PATH = "./private/governor.db"
ASSETS_PATH = "./assets"
FONTS_PATH = "./fonts"
TMP_PATH = "./private/tmp"
CMD_PREFIX = cfg['command_prefix']
NEXUS_API_KEY = cfg['nexus_key']

ADMIN_ACCESS = cfg['roles']['admin_access']
MODDER_ROLE = cfg['roles']['modder']
MODDER_URL = cfg['modder_wiki_url']
RANKS = cfg["ranks"]

SERVER_URL = cfg['server_url']

NO_SLOWMODE = cfg['channels']['slowmode_disabled']
XP_OFF = cfg['channels']['xp_disabled']
LOG_CHAN = cfg['channels']['log']
LIMIT_CHANS = cfg['channels']['limited']
RESOLVED_TAG = cfg['tags']['resolved']

GAME_ANNOUNCEMENT_CHANNEL = cfg['games']['announcement_channel']
AUTO_ADD_EPIC_GAMES = cfg['games']['auto_add_epic_games']
GAME_ANNOUNCE_TIME = datetime.strptime(cfg['games']['announcement_time'], "%I:%M %p").time()

PC_PLATFORM = cfg['roles']['platforms']['pc']
XBOX_PLATFORM = cfg['roles']['platforms']['xbox']
PS_PLATFORM = cfg['roles']['platforms']['ps']
NS_PLATFORM = cfg['roles']['platforms']['ns']
MOBILE_PLATFORM = cfg['roles']['platforms']['mobile']
VITA_PLATFORM = cfg['roles']['platforms']['vita']
