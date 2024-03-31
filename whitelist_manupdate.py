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

# from pprint import pprint
import time
import traceback
# from typing import Any
# import discord
# from discord.ext import commands, tasks
import requests
# import atexit
# import sys
import os
from dotenv import load_dotenv
import pymysql
import pymysql.cursors
import re

legal_mc_username_checker_rgx = re.compile(r"^[a-zA-Z0-9_]{2,16}$")
ROLES_ID_CONSTANT = [1214662167102492733, 1214662215198838846, 1215708993150787584, 1151653698758508564, 1142282014821711872,
                     1221268481799094302, 1223681351903875222, 1223453351795101737, 1221760962714140753, 1142281928112881664]


def is_username_legal(_username: str):
    return bool(legal_mc_username_checker_rgx.match(_username))

load_dotenv()

def print_trace(ex: BaseException):
    print(''.join(traceback.TracebackException.from_exception(ex).format()))

print("Connecting to SQL...")
# Connect to the database
sql_connection_ctx = pymysql.connect(host=os.environ.get("Q_MYSQL_HOST"),
                             user=os.environ.get("Q_MYSQL_USER"),
                             password=os.environ.get("Q_MYSQL_PASSWD"),
                             database='user1',
                             cursorclass=pymysql.cursors.DictCursor)
print("Connected to SQL.")

def sql_reader(_SQL_statement: str,):
    with sql_connection_ctx.cursor() as cursor:
        print("[READER]", _SQL_statement)
        # SQL statement to insert data into the table

        # Execute the SQL statement
        cursor.execute(_SQL_statement)
        
        # Commit the transaction
        # print("SQL OK")
        return cursor.fetchall()

def add_player_to_whitelist(_username: str):
    if not is_username_legal(_username):
        raise ValueError("Username is illegal (is not a real username)!")
    print("[WBroker] adding", _username)
    _r_post_obj = requests.post(os.environ.get("WHITELIST_API_ENDPOINT"), json={'name': _username}, headers={'Authorization': f'WHA {os.environ.get("WHITELIST_API_TOKEN")}'})
    _r_post_obj.raise_for_status()
    
    return _r_post_obj.text

for thingy in sql_reader("USE user1 ; SELECT mc_username FROM usertable where mc_username IS NOT NULLd"):
    add_player_to_whitelist(thingy['mc_username'])
    time.sleep(0.5)