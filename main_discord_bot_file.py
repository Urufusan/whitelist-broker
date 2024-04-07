# Copyright (C) 2024 Urufusan
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from pprint import pprint
import time
import traceback
from typing import Any
import discord
from discord.ext import commands, tasks
import requests
import atexit
import sys
import os
from dotenv import load_dotenv
import pymysql
import pymysql.cursors
import re

legal_mc_username_checker_rgx = re.compile(r"^[a-zA-Z0-9_]{2,16}$")
sql_connection_ctx = None
ROLES_ID_CONSTANT = [1214662167102492733, 1214662215198838846, 1215708993150787584, 1151653698758508564, 1142282014821711872,
                     1221268481799094302, 1223681351903875222, 1223453351795101737, 1221760962714140753, 1142281928112881664]

load_dotenv()
PROXY_ID = "6719ecfc-b1c8-4dd9-8ba5-ddf57af14112"
CRAFTY_TOKEN_STR = os.environ.get("CRAFTY_TOKEN")

# SQL stuff
def _load_sql_conn():
    print("Connecting to SQL...")
    # Connect to the database
    _t_sql_connection_ctx = pymysql.connect(host=os.environ.get("Q_MYSQL_HOST"),
                                user=os.environ.get("Q_MYSQL_USER"),
                                password=os.environ.get("Q_MYSQL_PASSWD"),
                                database='user1',
                                cursorclass=pymysql.cursors.DictCursor)
    print("Connected to SQL.")
    return _t_sql_connection_ctx

sql_connection_ctx = _load_sql_conn()


def is_username_legal(_username: str):
    return bool(legal_mc_username_checker_rgx.match(_username))


def print_trace(ex: BaseException):
    print(''.join(traceback.TracebackException.from_exception(ex).format()))

def safeunload():
    global sql_connection_ctx
    if sql_connection_ctx.open:
        sql_connection_ctx.close()
        print("SQL connection closed on exit.")

atexit.register(safeunload)


def send_stdin_command_crafty(command: str, server_id = PROXY_ID, token = CRAFTY_TOKEN_STR):
    url = f"https://panel.jased.xyz/api/v2/servers/{server_id}/stdin"
    headers = {"Authorization": f"Bearer {token}"}
    data = command
    
#    try:
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    print("Command sent successfully.")
    # except requests.exceptions.RequestException as e:
    #     print(f"Error sending command: {e}")

def ensure_velocity_perms(_player_name: str, _group_name: str = "whitelistedmembers"):
    for _ in range(3):
        try:
            _ash_r_json = requests.get(f"https://api.ashcon.app/mojang/v2/user/{_player_name}").json()
            pprint(_ash_r_json['uuid'])
            break
        except KeyError:
             print("Failed to get player uuid!")
             time.sleep(2)
    send_stdin_command_crafty(f"lpv user {_ash_r_json['uuid']} parent set {_group_name}")
    print(f"[WBroker] Added velocity server perms to {_player_name}")

# with connection:
with sql_connection_ctx.cursor() as _t_cursor:
    # Create a new record
    # sql = "INSERT INTO `users` (`email`, `password`) VALUES (%s, %s)"
    # cursor.execute(sql, ('webmaster@python.org', 'very-secret'))
    _t_cursor.execute("select @@version")
    pprint(_t_cursor.fetchall())
# connection is not autocommit by default. So you must commit to save
# your changes.
# connection.commit()
    
# with connection:
with sql_connection_ctx.cursor() as _t_cursor:
    # Read a single record
    _t_sql_all_data = "SELECT * from usertable"
    _t_cursor.execute(_t_sql_all_data)
    pprint(_t_cursor.fetchall())
    
print("SQL OK")
# sql_connection_ctx.close()

def sql_writer(_SQL_statement: str, data: tuple[Any]):
    global sql_connection_ctx
    try:
        with sql_connection_ctx.cursor() as cursor:
            print("[WRITER]", data)
            # SQL statement to insert data into the table

            # Execute the SQL statement
            _t_r_c = cursor.execute(_SQL_statement, data)
            
            # Commit the transaction
            sql_connection_ctx.commit()
            # print("SQL OK")
            return _t_r_c
    except pymysql.OperationalError:
        sql_connection_ctx = _load_sql_conn()
        time.sleep(2)
        sql_writer(_SQL_statement, data)

def sql_reader(_SQL_statement: str):
    global sql_connection_ctx
    try:
        with sql_connection_ctx.cursor() as cursor:
            print("[READER]", _SQL_statement)
            # SQL statement to insert data into the table

            # Execute the SQL statement
            cursor.execute(_SQL_statement)
            
            # Commit the transaction
            # print("SQL OK")
            return cursor.fetchall()
    except pymysql.OperationalError:
        sql_connection_ctx = _load_sql_conn()
        time.sleep(2)
        return sql_reader(_SQL_statement)


def is_dev():
    def check(ctx: commands.Context[commands.Bot]):
        return ctx.message.author.id in (
            444785578152558592,
        )

    return commands.check(check)

def add_player_to_whitelist(_username: str):
    if not is_username_legal(_username):
        raise ValueError("Username is illegal (is not a real username)!")
    print("[WBroker] adding", _username)
    _r_post_obj = requests.post(os.environ.get("WHITELIST_API_ENDPOINT"), json={'name': _username}, headers={'Authorization': f'WHA {os.environ.get("WHITELIST_API_TOKEN")}'})
    _r_post_obj.raise_for_status()
    try:
        ensure_velocity_perms(_username)
    except Exception as e:
        print_trace(e)
    
    return _r_post_obj.text

def remove_player_from_whitelist(_username: str):
    print("[WBroker] removing", _username)
    _r_post_obj = requests.delete(os.environ.get("WHITELIST_API_ENDPOINT"), json={'name': _username}, headers={'Authorization': f'WHA {os.environ.get("WHITELIST_API_TOKEN")}'})
    _r_post_obj.raise_for_status()
    try:
        ensure_velocity_perms(_username, "default")
    except Exception as e:
        print_trace(e)

    return _r_post_obj.text

def get_player_whitelist():
    _r_post_obj = requests.get(os.environ.get("WHITELIST_API_ENDPOINT"), headers={'Authorization': f'WHA {os.environ.get("WHITELIST_API_TOKEN")}'})
    _r_post_obj.raise_for_status()
    
    return _r_post_obj.json()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True
intents.guilds = True

TEMP_ACTIVITY_ROLE = "Temp activity role"
REAL_ACTIVITY_ROLE = "Activities"
xairen_guild: discord.Guild = None
temp_act_role_object = None
real_act_role_object = None

client = commands.Bot(command_prefix = ">>", activity=discord.Activity(type=discord.ActivityType.playing, name="GNU C Compiler"), intents=intents)

@client.event
async def on_ready():
    global xairen_guild
    global temp_act_role_object
    global real_act_role_object
    xairen_guild = client.get_guild(1142268839636258891)
    print(xairen_guild)
    temp_act_role_object = discord.utils.get(xairen_guild.roles, name=TEMP_ACTIVITY_ROLE)
    real_act_role_object = discord.utils.get(xairen_guild.roles, name=REAL_ACTIVITY_ROLE)
    print(f'We have logged in as {client.user}')
    # batch_update.start()
    await client.tree.sync()


@client.event
async def on_message(message: discord.Message):
    # await ctx.defer()
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

@client.hybrid_command(help="Sync the minecraft role")
@is_dev()
async def syncroles(ctx: commands.Context[commands.Bot]):
    print("Syncing MC roles...")
    minecraft_role = discord.utils.get(xairen_guild.roles, name="Minecraft")
    for _discord_user_id in sql_reader("SELECT user_id FROM usertable"):
        try:
            _t_member_object = xairen_guild.get_member(int(_discord_user_id['user_id']))
            await _t_member_object.add_roles(minecraft_role, reason="Syncing members!")
        except AttributeError:
            print("failed getting user", _t_member_object)
            continue
    await ctx.reply("OK!")


@client.hybrid_command(help="Sync your minecraft account with your Discord profile")
async def mcsync(ctx: commands.Context[commands.Bot], mc_username: str):
    await ctx.defer()
    _changed_user = False
    _valid_members_set = set()
    for _valid_role_id in ROLES_ID_CONSTANT:
        _x_g_r_t: discord.Role = xairen_guild.get_role(_valid_role_id)
        print(_x_g_r_t)
        _valid_members_set.update(_x_g_r_t.members)
    if ctx.author in _valid_members_set:
        pass
    else:
        # print(_valid_members_set)
        await ctx.reply("Nah mate ur not kewl enough lol (No role perm)")
        return
    
    print(f"Sync command called by {ctx.author.name} - {mc_username}")
    if not is_username_legal(mc_username):
        print("FAIL USER")
        await ctx.reply("The provided username is illegal (not a real minecraft username)!")
        return
    
    if _t_s_r_o := sql_reader(f"SELECT user_id FROM usertable WHERE mc_username = '{mc_username}'"):
        if _t_s_r_o[0]['user_id']:
            print("Duplicate checker", _t_s_r_o)
            await ctx.reply("## Conflict error!\nThis username is already whitelisted!")
            return
    
    try:
        sql_writer("INSERT INTO usertable (user_id, mc_username) VALUES (%s, %s)", (str(ctx.author.id), mc_username))
    except pymysql.err.IntegrityError:
        _existing_entry_for_removal = sql_reader(f"SELECT mc_username, already_invited FROM usertable WHERE user_id = {str(ctx.author.id)}")
        _changed_user = not _existing_entry_for_removal[0]['already_invited']
        if _existing_entry_for_removal[0]['mc_username']: remove_player_from_whitelist(_existing_entry_for_removal[0]['mc_username'])
        sql_writer("INSERT INTO usertable (user_id, mc_username) VALUES (%s, %s) ON DUPLICATE KEY UPDATE mc_username = VALUES(mc_username), mc_uuid = ''",  (str(ctx.author.id), mc_username))
    
    add_player_to_whitelist(mc_username)
    #          INSERT INTO usertable (user_id, mc_username) VALUES (%s, %s) ON DUPLICATE KEY UPDATE mc_username = VALUES(mc_username)
    await ctx.reply(f"Successfully added ``{mc_username}`` to the whitelist!" if not _changed_user else f"Successfully changed whitelisted nick from ``{_existing_entry_for_removal[0]['mc_username']}`` to ``{mc_username}``!")
    await client.get_channel(1221955537139400724).send(f"Successfully added ``{mc_username}`` to the whitelist!" if not _changed_user else f"Successfully changed whitelisted nick from ``{_existing_entry_for_removal[0]['mc_username']}`` to ``{mc_username}``!")
    # PSEUDO: Add username to whitelist, add alias to mongoDB
    # TODO: Minecraft username regex
    pass

@client.hybrid_command(help="Look up a minecraft account within Discord")
async def whois(ctx: commands.Context[commands.Bot], mc_username: str):
    if not is_username_legal(mc_username):
        print("FAIL USER")
        await ctx.reply("The provided username is illegal (not a real minecraft username)!")
        return
    print("Running query:", mc_username)
    try:
        _raw_uid = sql_reader(f"SELECT user_id FROM usertable WHERE mc_username = '{mc_username}'")[0]['user_id']
    except IndexError:
        _raw_uid = ""
    if _raw_uid:
        _e = discord.Embed()
        _e.set_footer(text=mc_username)
        _e.set_image(url=f"https://mc-heads.net/head/{mc_username}/128.png")
        await ctx.reply(f"## Found user!\nMinecraft username ``{mc_username}`` is linked to user ``{client.get_user(int(_raw_uid)).name}`` [ <@{_raw_uid}> ]!", embed=_e)
    else:
        await ctx.reply(f"Username ``{mc_username}`` has either never joined the server or the user has never linked their Discord profile to their Minecraft account.")
    

@client.hybrid_command(help="Send invities to users - manual trigger")
@is_dev()
async def massinvite(ctx: commands.Context[commands.Bot]):
    print("Mass invites started!")
    _valid_members_set = set()
    # for _valid_role_id in [1214662167102492733, 1214662215198838846, 1215708993150787584, 1151653698758508564, 1221268481799094302]:
    for _valid_role_id in ROLES_ID_CONSTANT:
        _x_g_r_t: discord.Role = xairen_guild.get_role(_valid_role_id)
        _valid_members_set.update(_x_g_r_t.members)
    #PSEUDO: Send DM message to each "paid" member, asking them to >>mcsync their accounts
    for _prem_member in list(_valid_members_set):
        try:
            sql_writer("INSERT INTO usertable (user_id, already_invited) VALUES (%s, 1)", (str(_prem_member.id),))
        except Exception as e:
            print(e)
            print(f"{_prem_member.name} is already in the database, skipping!")
            continue
        #sql_writer("UPDATE usertable SET active = TRUE WHERE user_id = %s", (str(_prem_member.id),))
        print(f"Invite sent to {_prem_member.name}!")
        await _prem_member.send(f"""
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

# @client.event
# async def on_voice_state_update(member:discord.Member, before:discord.VoiceState, after:discord.VoiceState):
#     global temp_act_role_object
#     global real_act_role_object  
#     print(member, before.channel.name, after.channel.name)

#     # print(rolle)
#     if real_act_role_object not in member.roles:
#         if after.channel.name == "asdasd":
#             await member.add_roles(temp_act_role_object)
#         elif before.channel.name == "asdasd":
#             await member.remove_roles(temp_act_role_object)

@client.event
async def on_command_error(ctx: commands.Context[commands.Bot], error: commands.CommandError):
    command = ctx.command
    if not command:
        return

    error = getattr(error, "original", error)
    print(
        f"Ignoring exception in command {ctx.prefix}{command.qualified_name} called by {(ctx.author, ctx.channel)}"
        + "\n"
        f"{''.join(traceback.format_exception(type(error), error, error.__traceback__))}"
    )
    await ctx.reply(f"# ERROR\nThere was an error in {ctx.prefix}{command.qualified_name}, type: {type(error).__name__}",
    )


@tasks.loop(minutes=10.0)
async def batch_update():
    print("Mass invites started!")
    _valid_members_set = set()
    try:
        # for _valid_role_id in [1214662167102492733, 1214662215198838846, 1215708993150787584, 1151653698758508564, 1221268481799094302]:
        for _valid_role_id in ROLES_ID_CONSTANT:
            _x_g_r_t: discord.Role = xairen_guild.get_role(_valid_role_id)
            _valid_members_set.update(_x_g_r_t.members)
        #PSEUDO: Send DM message to each "paid" member, asking them to >>mcsync their accounts
        for _prem_member in list(_valid_members_set):
            try:
                sql_writer("INSERT INTO usertable (user_id, already_invited) VALUES (%s, 1)", (str(_prem_member.id),))
            except Exception as e:
                print(e)
                print(f"{_prem_member.name} is already in the database, skipping!")
                continue
            #sql_writer("UPDATE usertable SET active = TRUE WHERE user_id = %s", (str(_prem_member.id),))
            print(f"Invite sent to {_prem_member.name}!")
            await _prem_member.send(f"""
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
        if False:
            print("Syncing MC roles...")
            minecraft_role = discord.utils.get(xairen_guild.roles, name="Minecraft")
            for _discord_user_id in sql_reader("SELECT user_id FROM usertable"):
                try:
                    _t_member_object = xairen_guild.get_member(int(_discord_user_id['user_id']))
                    await _t_member_object.add_roles(minecraft_role, reason="Syncing members!")
                except AttributeError:
                    print("failed getting user", _t_member_object)
                    continue
            print("Roles sync finished!")
    except Exception as e:
        # hacky
        print_trace(e)

client.run(os.environ.get('DISCORD_BOT_TOKEN'))