import discord
from discord.ext import commands, tasks
import requests
import sys
import os
from dotenv import load_dotenv

load_dotenv()

def is_dev():
    def check(ctx: commands.Context[commands.Bot]):
        return ctx.message.author.id in (
            444785578152558592,
        )

    return commands.check(check)


intents = discord.Intents.default()
# intents.message_content = True
intents.voice_states = True
TEMP_ACTIVITY_ROLE = "Temp activity role"
REAL_ACTIVITY_ROLE = "Activities"
xairen_guild: discord.Guild = None
temp_act_role_object = None
real_act_role_object = None

client = commands.Bot(command_prefix = ">>", activity=discord.Activity(type=discord.ActivityType.playing, name="GNU C Compiler"), intents=intents)

@client.event
async def on_ready():
    xairen_guild = client.get_guild(1142268839636258891)
    temp_act_role_object = discord.utils.get(xairen_guild.roles, name=TEMP_ACTIVITY_ROLE)
    real_act_role_object = discord.utils.get(xairen_guild.roles, name=REAL_ACTIVITY_ROLE)
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    await client.process_commands(message)

@client.hybrid_command(help="Restarts the bot", aliases=["btr", "butter"])
@is_dev()
async def restart(ctx: commands.Context[commands.Bot]):
    print("Bot forced to restart with a command. Restarting...")
    await ctx.reply(
        "The bot will perform a restart in a second! <:flushe:1161201649788915722>"
    )
    executable = sys.executable
    os.execl(executable, executable, *sys.argv)

@client.hybrid_command(help="Sync your minecraft account with your Discord profile")
async def mcsync(ctx: commands.Context[commands.Bot], mc_username: str):
    print(f"Sync command called by {ctx.author.name} - {mc_username}")
    # PSEUDO: Add username to whitelist, add alias to mongoDB
    # TODO: Minecraft username regex
    pass

@client.hybrid_command(help="Send invities to users - manual trigger")
@is_dev()
async def mcsync(ctx: commands.Context[commands.Bot]):
    print("Mass invites started!")
    _valid_members_set = set()
    for _valid_role_id in [1214662167102492733, 1214662215198838846, 1215708993150787584, 1151653698758508564, 1221268481799094302]:
        _x_g_r_t: discord.Role = xairen_guild.get_role(_valid_role_id)
        _valid_members_set.update(_x_g_r_t.members)
    #PSEUDO: Send DM message to each "paid" member, asking them to >>mcsync their accounts
    for _prem_member in list(_valid_members_set):
        _prem_member.send(f"""
# Hello {_prem_member.name}!

## You are a channel supporter of Okayxairen, which means that you have been granted access to the exclusive Minecraft server!

In order to get whitelisted, you have to type ``>>mcsync yourusernamehere`` in this DM!
After that's done, you may join the server on IP: ``mc.okayxairen.com``.

```
example usage:

>>mcsync Urufusan_
```

If you encounter any issues with the bot, please report them to Urufusan!
""")
    pass

@client.event
async def on_voice_state_update(member:discord.Member, before:discord.VoiceState, after:discord.VoiceState):
    global temp_act_role_object
    global real_act_role_object  
    print(member, before.channel.name, after.channel.name)

    # print(rolle)
    if real_act_role_object not in member.roles:
        if after.channel.name == "asdasd":
            await member.add_roles(temp_act_role_object)
        elif before.channel.name == "asdasd":
            await member.remove_roles(temp_act_role_object)


client.run(os.environ.get('DISCORD_BOT_TOKEN'))