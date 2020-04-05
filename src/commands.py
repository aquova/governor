import discord
import db, utils
from math import floor
from config import XP_PER_LVL

class CustomCommands:
    def __init__(self):
        self.cmd_dict = db.get_custom_cmds()

    def add_cmd(self, name, response):
        self.cmd_dict[name] = response
        db.set_new_custom_cmd(name, response)

cc = CustomCommands()

def get_custom_commands():
    return cc.cmd_dict

def define_cmd(message):
    cmd = utils.get_command(message)
    response = utils.remove_command(message)
    cc.add_cmd(cmd, response)

def get_xp(message):
    xp = db.fetch_user_xp(message.author.id)
    if xp == None:
        return "You have no XP :("
    else:
        return "You have {} XP".format(xp)

def get_level(message):
    xp = db.fetch_user_xp(message.author.id)
    if xp == None:
        return "You have no xp :("
    else:
        lvl = floor(xp / XP_PER_LVL)
        return "You are level {}".format(lvl)
