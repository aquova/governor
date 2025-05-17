from dataclasses import dataclass
from datetime import datetime, time
import os

import yaml

@dataclass
class RankData:
    name: str
    level: int
    message: str
    role_id: int
    welcome_channels: list[int]
    welcome_message: str

CURRENT_DIR = os.path.dirname(__file__)

XP_PER_MINUTE = 10
XP_PER_LVL = 300
STARTING_XP = XP_PER_LVL

# Read values from config file
CONFIG_PATH = "private/config.yaml"
with open(CONFIG_PATH) as config_file:
    cfg = yaml.safe_load(config_file)

DISCORD_KEY: str = cfg['discord']
DB_PATH = "./private/governor.db"
ASSETS_PATH = os.path.join(CURRENT_DIR, "assets")
FONTS_PATH = os.path.join(CURRENT_DIR, "fonts")
TMP_PATH = "./private/tmp"
CMD_PREFIX: str = cfg['command_prefix']
NEXUS_API_KEY: str = cfg['nexus_key']

ADMIN_ACCESS: list[int] = cfg['roles']['admin_access']
MODDER_ROLE: int = cfg['roles']['modder']
MODDER_URL: str = cfg['modder_wiki_url']

RANKS: list[RankData] = []
for rank in cfg["ranks"]:
    RANKS.append(RankData(rank["name"], rank["level"], rank["message"], rank["role_id"], rank["welcome"]["channels"], rank["welcome"]["message"]))

SERVER_URL: str = cfg['server_url']

NO_SLOWMODE: list[int] = cfg['channels']['slowmode_disabled']
XP_OFF: list[int] = cfg['channels']['xp_disabled']
LOG_CHAN: int = cfg['channels']['log']
LIMIT_CHANS: list[int] = cfg['channels']['limited']

FORUM_CHAN: int = cfg['channels']['forum']
RESOLVED_TAG: int = cfg['tags']['resolved']
OPEN_TAG: int = cfg['tags']['open']
PROGRESS_TAGS: list[int] = cfg['tags']['progress']

GAME_ANNOUNCEMENT_CHANNEL: int = cfg['games']['announcement_channel']
AUTO_ADD_EPIC_GAMES: bool = cfg['games']['auto_add_epic_games']
GAME_ANNOUNCE_TIME: time = datetime.strptime(cfg['games']['announcement_time'], "%I:%M %p").time()
