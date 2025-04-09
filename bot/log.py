import re
import string
import urllib.parse

import bs4
import discord
import requests

from config import NEXUS_API_KEY
import custom
from utils import flatten_index

# Template for SMAPI log info messages
smapi_log_message_template = string.Template(
    "**Log Info:** SMAPI $SMAPI_ver with SDV $StardewVersion on $OS, "
    "with $SMAPIMods C# mods and $ContentPacks content packs."
)
smapi_suggested_fixes_template = string.Template(
    "\n**Suggested fixes:** $suggested_fixes"
)

async def check_log_link(message: discord.Message):
    """
    Check log link

    Checks if a Discord Message object contains a smapi.io URL, and if so parses the content
    """
    for log_link in re.findall(r"https://smapi.io/log/[a-zA-Z0-9]{32}", message.content):
        log_info = _parse_log(log_link)
        await message.channel.send(log_info)

async def check_attachments(message: discord.Message):
    """
    Check attachments

    Checks if a Discord Message objects contains attachments titled 'SMAPI-latest.txt' or 'SMAPI-crash.txt'. If so, it automatically uploads them to smapi.io
    """
    for attachment in message.attachments:
        if attachment.filename == "SMAPI-latest.txt" or attachment.filename == "SMAPI-crash.txt":
            r = requests.get(attachment.url)
            log = urllib.parse.quote(r.text)
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
            }

            s = requests.post('https://smapi.io/log/', data="input={0}".format(log), headers=headers)
            logurl = s.text.split('</strong> <code>')[1].split('</code>')[0]
            await message.channel.send("Log found, uploaded to: " + logurl)

async def check_xnb_mods(message: discord.Message):
    """
    Check XNB mods

    Checks if a Discord Message object contains a SDV Nexus Mods URL. If so, uses the Nexus API to determine if the linked mod is using outdated technologies

    The 'xnbzola' custom command *must* still exist, if not this function should be changed
    """
    for mod_id in re.findall(r"https://www\.nexusmods\.com/stardewvalley/mods/(\d+)", message.content.replace("<", "").replace(">", "")):
        mod_id = mod_id.strip()
        files_endpoint = f'https://api.nexusmods.com/v1/games/stardewvalley/mods/{mod_id}/files.json"'

        files_info = requests.get(files_endpoint, params={
            'category': 'main'
        }, headers={
            'accept': 'application/json',
            'apikey': NEXUS_API_KEY
        }).json()

        if len(files_info['files']) == 0:
            continue

        index_url = files_info['files'][0]['content_preview_link']
        index = requests.get(index_url, headers={
            'accept': 'application/json',
        }).json()

        flat = flatten_index(index)
        xnbs = [f for f in flat if f['name'].endswith('.xnb')]
        manifests = [f for f in flat if f['name'].endswith('manifest.json')]


        if len(xnbs) != 0 and len(manifests) == 0:
            xnbzola = custom.parse_response('xnbzola')
            await message.reply(embed=xnbzola)
        else:
            continue
        break

def _parse_log(url: str) -> str:
    """
    Parse log

    Private function. Parses a smapi.io log to extract its recommendations and statistics.
    """
    json_url = url + '?format=RawDownload'
    r = requests.get(json_url)
    
    try:
        data = r.json()
    except:
        return "Oops, couldn't parse that file. Make sure you share a valid SMAPI log."

    if not data['IsValid'] or data['Error'] != None:
        return "Oops, couldn't parse that file. Make sure you share a valid SMAPI log."

    mods = data.get('Mods') or []

    log_info = {
        "StardewVersion": data.get("GameVersion"),
        "SMAPI_ver": data.get("ApiVersion"),
        "SMAPIMods": data.get("TotalCodeMods"),
        "ContentPacks": data.get("TotalContentPacks"),
        "OS": data.get("OperatingSystem"),
        "gamepath": data.get("GamePath"),
        "suggested_fixes": "",
        "success": True,
    }
    
    for key in log_info:
        if log_info[key] == None:
            log_info["success"] = False

    fixes = []

    if data.get("HasModUpdates"):
        fixes.append("One or more mods are out of date, consider updating them")
    if data.get("HasApiUpdate"):
        fixes.append("SMAPI is out of date, consider updating it")
        
    fixes_human = ", ".join(fixes)
    log_info["suggested_fixes"] = fixes_human

    output = smapi_log_message_template.substitute(log_info)
    if log_info["suggested_fixes"] != "":
        output += smapi_suggested_fixes_template.substitute(log_info)
    return output
