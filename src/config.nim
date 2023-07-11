import json

import types

const XP_PER_MINUTE* = 10
const XP_PER_LEVEL* = 300
const STARTING_XP* = XP_PER_LEVEL

const CONFIG_PATH = "private/config.json"
const RANKS_PATH = "private/ranks.json"
const DB_PATH* = "private/governor.db"
const ASSETS_PATH* = "assets"
const FONTS_PATH* = "fonts"
const TMP_PATH* = "private/tmp"

let cfg = parseFile(CONFIG_PATH)

let CMD_PREFIX* = cfg["command_prefix"].getStr()

let ADMIN_ACCESS = cfg['roles']['admin_access'].getElems()
let DEFINE_ACCESS = cfg['roles']['define_access'].getElems()

let SERVER_URL = cfg['server_url'].getStr()
let OWNER = cfg['owner'].getStr()
let DEBUG_BOT = cfg['debug'].getBool()

let LVL_CHANS = cfg['channels']['lvl_allowed'].getElems()
let NO_SLOWMODE = cfg['channels']['slowmode_disabled'].getElems()
let XP_OFF = cfg['channels']['xp_disabled'].getElems()
let LOG_CHAN = cfg['channels']['log'].getStr()
let LIMIT_CHANS = cfg['channels']['limited'].getElems()

let GAME_ANNOUNCEMENT_CHANNEL = cfg['games']['announcement_channel'].getStr()
let AUTO_ADD_EPIC_GAMES = cfg['games']['auto_add_epic_games'].getBool()
let GAME_ANNOUNCE_TIME = cfg['games']['announcement_time'].getStr()

var pronoun_roles* = newTable[Pronouns, string]()
pronoun_roles[HeHim] = cfg['roles']['pronouns']['he'].getStr()
pronoun_roles[SheHer] = cfg['roles']['pronouns']['she'].getStr()
pronoun_roles[TheyThem] = cfg['roles']['pronouns']['they'].getStr()
pronoun_roles[ItIts] = cfg['roles']['pronouns']['it'].getStr()
pronoun_roles[Any] = cfg['roles']['pronouns']['any'].getStr()
pronoun_roles[Ask] = cfg['roles']['pronouns']['ask'].getStr()

let PC_PLATFORM = cfg['roles']['platforms']['pc'].getStr()
let XBOX_PLATFORM = cfg['roles']['platforms']['xbox'].getStr()
let PS_PLATFORM = cfg['roles']['platforms']['ps'].getStr()
let NS_PLATFORM = cfg['roles']['platforms']['ns'].getStr()
let MOBILE_PLATFORM = cfg['roles']['platforms']['mobile'].getStr()
let VITA_PLATFORM = cfg['roles']['platforms']['vita'].getStr()

# Import ranks from their configuration
with open(RANKS_PATH) as ranks_file:
    RANKS = json.load(ranks_file)['ranks']
