from dataclasses import dataclass
from achievements import AchivementID

@dataclass
class Rank:
    name: str
    level: int
    message: str
    roleid: int
    achivement: AchivementID
    welcome_channel: int | None
    welcome_message: str

RANKS = [
    Rank("Villager", 1, "", 222591661903970304, AchivementID.VILLAGER, None, ""),
    Rank("Cowpoke", 5, "You leveled up to Cowpoke. You can now speak in our voice channels and share images in all channels!", 744929308388098068, AchivementID.COWPOKE, None, ""),
    Rank("Farmer", 25, "You leveled up to Farmer. You're now a prettier shade of blue. Thanks for sticking around!", 176445608201158657, AchivementID.FARMER, None, ""),
    Rank("Shepherd", 100, "You leveled up to Shepherd. Wow, you've been talking a lot! Have a prettier, slightly more brag worthy, shade of blue.", 571537175741464576, AchivementID.SHEPHERD, None, ""),
    Rank("Rancher", 250, "You leveled up to Rancher. _That's level 250._ Woot!", 230788741084610560, AchivementID.RANCHER, None, ""),
    Rank("Cropmaster", 500, "You leveled up to Cropmaster. That's _level 500_! The deepening purple represents your mad descent into the server.", 405556651245043712, AchivementID.CROPMASTER, 709075692188336199, "Welcome to <#709075692188336199>! This is a special channel for Cropmasters like yourself. There is some important information in the pins so don't forget to check those out. Thank you for being a part of the community! :smiling_face_with_3_hearts: :kissing_heart:"),
    Rank("Desperado", 1000, "You leveled up to Desperado. That's _level 1000_! :open_mouth: You have been taken by the server's evil clutches and there is no escape for you. Congrats!", 405556702923063296, AchivementID.DESPERADO, None, ""),
]
