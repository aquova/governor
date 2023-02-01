import bs4
import requests
import string

# Template for SMAPI log info messages
smapi_log_message_template = string.Template(
    "**Log Info:** SMAPI $SMAPI_ver with SDV $StardewVersion on $OS, "
    "with $SMAPIMods C# mods and $ContentPacks content packs."
)
smapi_suggested_fixes_template = string.Template(
    "\n**Suggested fixes:** $suggested_fixes"
)

def parse_log(url):
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.text, "html.parser")
    soup.encode("utf-8")
    data = soup.find("table", {"id": "metadata"})

    if data is None:
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
        fix_elems = soup.find("ul", {"id": "fix-list"}).find_all("li")
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
