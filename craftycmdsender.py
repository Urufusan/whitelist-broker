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
server_id = "dcb39d17-6a4d-4f68-bf67-f9687e734372"
token = os.environ.get("CRAFTY_TOKEN")
# command = "mem"
with open("beemoviescript.txt") as f:
    z = f.readlines()
for h in z:
    send_stdin_command(server_id, token, f"say {h.strip()}")
    time.sleep(2)
