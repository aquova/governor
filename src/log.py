import re
import string
import urllib.parse

import bs4
import discord
import requests

_NEW_WIKI = "https://stardewvalleywiki.com"

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

async def check_wiki_link(message: discord.Message):
    for community_wiki_link in re.findall(r"https://stardewcommunitywiki\.com/[a-zA-Z0-9_/:\-%]*", message.content):
        link_path = urllib.parse.urlparse(community_wiki_link).path
        new_url = urllib.parse.urljoin(_NEW_WIKI, link_path)
        await message.channel.send(f"I notice you're linking to the old wiki, that wiki has been in a read-only state for several months. Here are the links to that page on the new wiki: {new_url}")

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
