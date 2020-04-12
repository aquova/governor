import json

XP_PER_LVL = 300

# Read values from config file
with open('private/config.json') as config_file:
    cfg = json.load(config_file)

DISCORD_KEY = cfg['discord']
DB_PATH = cfg['db_path']
CMD_PREFIX = cfg['command_prefix']
ADMIN_ACCESS = cfg['roles']['admin_access']
SERVER_URL = cfg['server_url']

# Import ranks from their configuration
with open(cfg['ranks_path']) as ranks_file:
    RANKS = json.load(ranks_file)['ranks']
