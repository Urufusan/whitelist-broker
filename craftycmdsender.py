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

import time
import requests
from dotenv import load_dotenv
import os

load_dotenv()

def get_player_whitelist():
    _r_post_obj = requests.get(os.environ.get("WHITELIST_API_ENDPOINT"), headers={'Authorization': f'WHA {os.environ.get("WHITELIST_API_TOKEN")}'})
    _r_post_obj.raise_for_status()
    
    return _r_post_obj.json()

def send_stdin_command(server_id, token, command):
    url = f"https://panel.jased.xyz/api/v2/servers/{server_id}/stdin"
    headers = {"Authorization": f"Bearer {token}"}
    data = command
    
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        print("Command sent successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Error sending command: {e}")

# Example usage:
server_id = "6719ecfc-b1c8-4dd9-8ba5-ddf57af14112"
token = os.environ.get("CRAFTY_TOKEN")
# command = "mem"

for h in get_player_whitelist():
    send_stdin_command(server_id, token, f"lpv user {h['name']} permission set serverpermissions.server.xairencraft")
