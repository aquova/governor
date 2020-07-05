import asyncio, datetime, discord

WAIT_TIME = 300 # How long to sleep between checks, in seconds
MAX_SLOWMODE = 15 # In seconds
THRESHOLD = 100 # Threshold between slowmode levels, arbitrary units

class Thermometer:
    def __init__(self):
        self.channel_dict = {}

    def start(self, server):
        self.server = server
        self.channels = [x for x in self.server.channels if type(x) == discord.TextChannel]
        # NOTE: CSV logging is temporary
        channel_ids = [str(x.id) for x in self.channels]
        csv_header = ", ".join(channel_ids) + '\n'
        with open("private/slowmode.csv", 'w') as f:
            f.write(csv_header)
        asyncio.ensure_future(self._calc_slowmode())

    async def user_spoke(self, message):
        channel = message.channel.id
        user_id = message.author.id
        if channel in self.channel_dict:
            self.channel_dict[channel].append(user_id)
        else:
            self.channel_dict[channel] = [user_id]

    async def _calc_slowmode(self):
        while True:
            await asyncio.sleep(WAIT_TIME)

            csv_entry = []
            # Iterate thru each channel, generating weighted value for each channel and adjusting slowmode if necessary
            for channel in self.channels:
                channel_id = channel.id
                # NOTE: CSV logging is temporary
                if channel_id not in self.channel_dict:
                    csv_data = f"Users: 0 Messages: 0"
                    csv_entry.append(csv_data)
                else:
                    spoken_list = self.channel_dict[channel_id]
                    spoken_set = set(spoken_list)
                    csv_data = f"Users: {len(spoken_set)} Messages: {len(spoken_list)}"
                    csv_entry.append(csv_data)

                # if channel_id not in self.channel_dict:
                #     continue

                # spoken_list = self.channel_dict[channel_id]
                # spoken_set = set(spoken_list)
                # metric = len(spoken_list) * (len(spoken_list) / len(spoken_set))
                # slowmode = min(MAX_SLOWMODE, int(metric / THRESHOLD))

                # try:
                #     if channel.slowmode_delay != slowmode:
                #         await channel.edit(slowmode_delay=slowmode)
                # except Exception as e:
                #     print(f"Exception: {str(e)}")

            self.channel_dict.clear()

            # NOTE: CSV logging is temporary
            entry = ", ".join(csv_entry) + '\n'
            with open("private/slowmode.csv", 'a') as f:
                f.write(entry)
