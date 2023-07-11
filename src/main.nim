import dimscord, asyncdispatch

let discord = newDiscordClient("TOKEN")

proc onReady(s: Shard, r: Ready) {.event(discord).} =
  echo(r.user.name)
  echo(r.user.id)

proc threadCreate(s: Shard, g: Guild, c: GuildChannel) {.event(discord).} =
  # TODO: Join thread
  discard

proc guildMemberAdd(s: Shard, g: Guild, m: Member) {.event(discord).} =
  # TODO: update_user_count

proc guildMemberRemove(s: Shard, g: Guild, m: Member) {.event(discord).} =
  # TODO:
  # remove_from_cache
  # update_user_count

proc messageCreate(s: Shard, m: Message) {.event(discord).} =
  if m.author.bot: return
  let channel = await discord.api.getChannel(m.channel_id)

  # 'channel' is a tuple, with the first element populated if GulidChannel
  # Second element is populated if DMChannel
  if channel[1].isSome():
    return

  if m.content != "" and m.content[0] == CMD_PREFIX:
    # TODO
    discard

waitFor discord.startSession()
