import json

# Read values from config file
with open('private/config.json') as config_file:
    cfg = json.load(config_file)

DISCORD_KEY = cfg['discord']
DB_PATH = cfg['db_path']
