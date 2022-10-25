import bs4
import requests

def parse_log(url):
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.text, "html.parser")
    soup.encode("utf-8")
    data = soup.find("table", {"id": "metadata"})
    
    log_info = {
        "StardewVersion": data.get("data-game-version"),
        "SMAPI_ver": data.get("data-smapi-version"),
        "SMAPIMods": data.get("data-code-mods"),
        "ContentPacks": data.get("data-content-packs"),
        "OS": data.get("data-os"),
        "gamepath": data.get("data-game-path"),
        "success": True,
    }
    for key in log_info:
        if log_info[key] == None:
            log_info["success"] = False
    
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
    fixes_human = fixes_human.rsplit(", ", 1)[0] + " and " + fixes_human.rsplit(", ", 1)[1]
    log_info["suggested_fixes"] = fixes_human
    

            
    return log_info