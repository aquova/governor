import bs4
import requests

#create a log class, that will parse the log file and return the info
def parse_log(url):
    #get the log file
    r = requests.get(url)
    #parse the log file
    soup = bs4.BeautifulSoup(r.text, "html.parser")
    soup.encode("utf-8")
    #find the log info
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
            fixes.append("PyTKPerformanceOptimizationsOff")
        elif "Consider updating these mods to fix problems:" in innerHTML:
            fixes.append("OutdatedMods")
        elif "PyTK's image scaling isn't compatible with SMAPI strict mode" in innerHTML:
            fixes.append("PyTkImageScalingStrictModeOff")
        elif "You don't have the " in innerHTML and "Error Handler" in innerHTML:
            fixes.append("ErrorHandlerMissing")
        elif "which removes all deprecated APIs. This can significantly improve performance, but some mods may not work." in innerHTML:
            fixes.append("StrictModeOn")
    log_info["suggested_fixes"] = fixes

            
    return log_info