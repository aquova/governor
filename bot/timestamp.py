from datetime import datetime, timezone

# From here: https://en.wikipedia.org/wiki/List_of_time_zone_abbreviations
TZ = {
    "UTC+14": "+14", "LINT": "+1400",
    "CHADT": "+1345",
    "UTC+13": "+1300", "NZDT": "+1300", "PHOT": "+1300", "TKT": "+1300", "TOT": "+1300",
    "CHAST": "+1245",
    "UTC+12": "+1200", "ANAT": "+1200", "FJT": "+1200", "GILT": "+1200", "MAGT": "+1200", "MHT": "+1200", "NZST": "+1200", "PETT": "+1200", "TVT": "+1200", "WAKT": "+1200",
    "UTC+11": "+1100", "AEDT": "+1100", "AET": "+1100", "KOST": "+1100", "MIST": "+1100", "NCT": "+1100", "NFT": "+1100", "PONT": "+1100", "SAKT": "+1100", "SBT": "+1100", "SRET": "+1100", "VUT": "+1100",
    "ACDT": "+1030", "LHST": "+1030",
    "UTC+10": "+1000", "AEST": "+1000", "CHST": "+1000", "CHUT": "+1000", "DDUT": "+1000", "PGT": "+1000", "VLAT": "+1000",
    "ACST": "+0930",
    "UTC+9": "+0900", "CHOST": "+0900", "GAMT": "-0900", "JST": "+0900", "KST": "+0900", "PWT": "+0900", "TLT": "+0900", "ULAST": "+0900", "WIT": "+0900", "YAKT": "+0900",
    "UTC+8": "+0800", "AWST": "+0800", "BNT": "+0800", "CHOT": "+0800", "HKT": "+0800", "IRKT": "+0800", "MYT": "+0800", "PHT": "+0800", "PHST": "+0800", "SGT": "+0800", "SST": "+0800", "ULAT": "+0800", "WITA": "+0800", "WST": "+0800",
    "UTC+7": "+0700", "CXT": "+0700", "DAVT": "+0700", "HOVT": "+0700", "ICT": "+0700", "KRAT": "+0700", "NOVT": "+0700", "THA": "+0700", "WIB": "+0700",
    "CCT": "+0630", "MMT": "+0630",
    "UTC+6": "+0600", "ALMT": "+0600", "BIOT": "+0600", "BST": "+0600", "BTT": "+0600", "KGT": "+0600", "OMST": "+0600", "VOST": "+0600",
    "NPT": "+0545",
    "IST": "+0530", "SLST": "+0530",
    "UTC+5": "+0500", "AQTT": "+0500", "HMT": "+0500", "MAWT": "+0500", "MVT": "+0500", "ORAT": "+0500", "PKT": "+0500", "TFT": "+0500", "TJT": "+0500", "TMT": "+0500", "UZT": "+0500", "YEKT": "+0500",
    "AFT": "+0430", "IRDT": "+0430",
    "UTC+4": "+0400", "AZT": "+0400", "GET": "+0400", "GST": "+0400", "MUT": "+0400", "RET": "+0400", "SAMT": "+0400", "SCT": "+0400",
    "IRST": "+0330",
    "UTC+3": "+0300", "EAT": "+0300", "EEST": "+0300", "FET": "+0300", "IDT": "+0300", "IOT": "+0300", "MSK": "+0300", "SYOT": "+0300", "TRT": "+0300", "VOLT": "+0300",
    "UTC+2": "+0200", "CAT": "+0200", "CEST": "+0200", "EET": "+0200", "HAEC": "+0200", "KALT": "+0200", "MEST": "+0200", "SAST": "+0200", "WAST": "+0200",
    "UTC+1": "+0100", "CET": "+0100", "DFT": "+0100", "MET": "+0100", "WAT": "+0100", "WEST": "+0100",
    "UTC+0": "+0000", "AZOST": "+0000", "EGST": "+0000", "GMT": "+0000", "UTC": "+0000", "WET": "+0000",
    "UTC-1": "-0100", "AZOT": "-0100", "CVT": "-0100", "EGT": "-0100",
    "UTC-2": "-0200", "BRST": "-0200", "FNT": "-0200", "PMDT": "-0200", "UYST": "-0200", "WGST": "-0200",
    "NDT": "-0230",
    "UTC-3": "-0300", "ADT": "-0300", "AMST": "-0300", "ART": "-0300", "BRT": "-0300", "CLST": "-0300", "FKST": "-0300", "GFT": "-0300", "PMST": "-0300", "PYST": "-0300", "ROTT": "-0300", "SRT": "-0300", "UYT": "-0300", "WGT": "-0300",
    "NST": "-0330", "NT": "-0330",
    "UTC-4": "-0400", "AMT": "-0400", "AST": "-0400", "BOT": "-0400", "CLT": "-0400", "COST": "-0400", "ECT": "-0400", "EDT": "-0400", "ET": "-0400", "FKT": "-0400", "GYT": "-0400", "PYT": "-0400", "VET": "-0400",
    "UTC-5": "-0500", "ACT": "-0500", "CDT": "-0500", "COT": "-0500", "CT": "-0500", "EASST": "-0500", "EST": "-0500", "PET": "-0500",
    "UTC-6": "-0600", "CST": "-0600", "EAST": "-0600", "GALT": "-0600", "MDT": "-0600",
    "UTC-7": "-0700", "MST": "-0700", "PDT": "-0700",
    "UTC-8": "-0800", "AKDT": "-0800", "CIST": "-0800", "PST": "-0800",
    "UTC-9": "-0900", "AKST": "-0900", "GIT": "-0900", "HDT": "-0900",
    "MART": "-0930", "MIT": "-0930",
    "UTC-10": "-1000", "CKT": "-1000", "HST": "-1000", "SDT": "-1000", "TAHT": "-1000",
    "UTC-11": "-1100", "NUT": "-1100",
    "UTC-12": "-1200", "BIT": "-1200", "IDLW": "-1200",
}

def calculate_timestamps(date: str, time: str, tz: str) -> str:
    """
    Calculate timestamp

    Receives information from the user regarding a date, time, and timezone, and returns a series of options for that timestamp formatted in Discord's style
    """
    if tz.upper() in TZ:
        tz_offset = TZ[tz.upper()]
        combined_time = f"{date} {time} {tz_offset}"
        # strptime's docs claims that it supports a '%Z' field that accepts TZ abbreviations, but it seems very finicky
        desired = datetime.strptime(combined_time, "%Y/%m/%d %H:%M %z")
        epoch = datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        unix = int((desired - epoch).total_seconds())
        output = (
            f"Here are some timestamps for `{date} {time} UTC{tz_offset}` and how they'll display!\n"
            f"`<t:{unix}:F>` - <t:{unix}:F>\n"
            f"`<t:{unix}:f>` - <t:{unix}:f>\n"
            f"`<t:{unix}:D>` - <t:{unix}:D>\n"
            f"`<t:{unix}:d>` - <t:{unix}:d>\n"
            f"`<t:{unix}:t>` - <t:{unix}:t>\n"
            f"`<t:{unix}:T>` - <t:{unix}:T>\n"
            f"`<t:{unix}:R>` - <t:{unix}:R>"
        )
        return output
    raise IOError

