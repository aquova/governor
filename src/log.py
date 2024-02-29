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
    for log_link in re.findall(r"https://smapi.io/log/[a-zA-Z0-9]{32}", message.content):
        log_info = _parse_log(log_link)
        await message.channel.send(log_info)

async def check_attachments(message: discord.Message):
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
            await message.reply(custom.parse_response('xnbzola'))
        else:
            continue
        break

def _parse_log(url):
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.text, "html.parser")
    soup.encode("utf-8")
    data = soup.find("table", {"id": "metadata"})

    if not isinstance(data, bs4.Tag):
        return "Oops, couldn't parse that file. Make sure you share a valid SMAPI log."

    log_info = {
        "StardewVersion": data.get("data-game-version"),
        "SMAPI_ver": data.get("data-smapi-version"),
        "SMAPIMods": data.get("data-code-mods"),
        "ContentPacks": data.get("data-content-packs"),
        "OS": data.get("data-os"),
        "gamepath": data.get("data-game-path"),
        "suggested_fixes": "",
        "success": True,
    }
    for key in log_info:
        if log_info[key] == None:
            log_info["success"] = False

    try:
        fix_list = soup.find("ul", {"id": "fix-list"})
        if isinstance(fix_list, bs4.Tag):
            fix_elems = fix_list.find_all("li")
            fixes = []
            for fix in fix_elems:
                innerHTML = fix.decode_contents()
                if "PyTK 1.23.* or earlier isn't compatible with newer SMAPI performance" in innerHTML:
                    fixes.append("Pytk isn't compatible with newer SMAPI performance optimizations, consider removing it")
                elif "Consider updating these mods to fix problems:" in innerHTML:
                    fixes.append("One or more mods are out of date, consider updating them")
                elif "PyTK's image scaling isn't compatible with SMAPI strict mode" in innerHTML:
                    fixes.append("Pytk's image scaling isn't compatible with SMAPI strict mode, disable it")
                elif "You don't have the " in innerHTML and "Error Handler" in innerHTML:
                    fixes.append("You don't have the Error Handler mod installed, reinstall SMAPI to get it")
                elif "which removes all deprecated APIs. This can significantly improve performance, but some mods may not work." in innerHTML:
                    fixes.append("SMAPI is running in strict mode, which removes all deprecated APIs. This can significantly improve performance, but some mods may not work.")
            fixes_human = ", ".join(fixes)
            log_info["suggested_fixes"] = fixes_human
    except AttributeError:
        pass

    output = smapi_log_message_template.substitute(log_info)
    if log_info["suggested_fixes"] != "":
        output += smapi_suggested_fixes_template.substitute(log_info)
    return output