import discord
from discord.ext import commands, tasks
import os

intents = discord.Intents.default()
# intents.message_content = True
intents.voice_states = True
TEMP_ACTIVITY_ROLE = "Temp activity role"
REAL_ACTIVITY_ROLE = "Activities"
xairen_guild = None
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

@client.event
async def on_voice_state_update(member:discord.Member, before:discord.VoiceState, after:discord.VoiceState):
    print(member, before.channel.name, after.channel.name)

    # print(rolle)
    if real_act_role_object not in member.roles:
        if after.channel.name == "asdasd":
            await member.add_roles(temp_act_role_object)
        elif before.channel.name == "asdasd":
            await member.remove_roles(temp_act_role_object)


client.run(os.environ.get('TOKEN'))