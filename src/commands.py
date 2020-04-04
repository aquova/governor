import discord
import utils
from math import floor
from config import XP_PER_LVL

def get_xp(message):
    xp = utils.fetch_user_xp(message.author.id)
    if xp == None:
        return "You have no XP :("
    else:
        return "You have {} XP".format(xp)

def get_level(message):
    xp = utils.fetch_user_xp(message.author.id)
    if xp == None:
        return "You have no xp :("
    else:
        lvl = floor(xp / XP_PER_LVL)
        return "You are level {}".format(lvl)
