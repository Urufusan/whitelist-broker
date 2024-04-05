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
import rentry
import whitelist_manupdate
import os
import hashlib
import random

motd_list = [
    "&#2F9BD9X&#4B89DFa&#6677E5i&#8265EBr&#9D53F1e&#B941F7n&#C93FEBc&#D543DAr&#E148C9a&#ED4CB8f&#F950A7t &#F950A7- &#ED4CB8R&#E148C9e&#D543DAm&#C93FEBa&#B941F7s&#9D53F1t&#8265EBe&#6677E5r&#4B89DFe&#2F9BD9d",
    "&#2F9BD9B&#458CDEe&#5C7EE3l&#726FE7l&#8861ECe&#9F52F1'&#B543F6s  &#C53EF1:&#CF41E33&#D844D6v&#E248C8i&#EC4BBAl&#F54FADl&#FF529Fe",
    "&#2F9BD9g&#4F86E0a&#6F71E7y &#905CEEp&#B047F5p&#C73EEEl &#D543DAc&#E348C7i&#F14DB3t&#FF529Fy",
    "&#2F9BD9O&#3B93DCX&#478BDEC&#5383E1r&#5F7BE3a&#6B73E6f&#786CE9t &#8464EB- &#905CEEm&#9C54F0c&#A84CF3.&#B444F5o&#C03CF8k&#C047F9a&#C151F9y&#C15CFAx&#C267FAa&#C271FBi&#C37CFCr&#C387FCe&#C391FDn&#C49CFD.&#C4A7FEc&#C5B1FEo&#C5BCFFm",
    "&#2F9BD9g&#31A6DEo&#33B1E3o&#35BBE7f&#37C6ECy &#39D1F1s&#3BDCF6e&#47DEF9r&#5CD8FAv&#71D3FBe&#86CDFCr&#9BC7FD!&#B0C2FE!&#C5BCFF!",
    "&#D92F2FP&#DE4431L&#E35933U&#E76D35H&#EC8237!&#F19739!&#F6AC3B!&#F4B64B!&#ECB769!&#E4B887!&#DDB9A5!&#D5BAC3!&#CDBBE1!&#C5BCFF!"
]


def txt_to_hash(_text):
    _m = hashlib.sha256(_text.encode('UTF-8'))
    return _m.hexdigest()

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

if __name__ == "__main__":
    page_text_hash = ""
    while True:
        page_text = "<h1>Whitelisted users</h1>\n<hr />\n<ul>"
        players = []
        # for thingy in whitelist_manupdate.sql_reader("SELECT mc_username FROM usertable where mc_username IS NOT NULL ORDER BY mc_username ASC"):
        #     page_text += f"<li id='{thingy['mc_username'].lower()}'>{thingy['mc_username']}</li>\n"
        try:
            for thingy in whitelist_manupdate.get_player_whitelist():
                players.append(thingy['name'])
        except requests.exceptions.ConnectionError:
            print("uh oh, fetching failed!")
            time.sleep(10)
            continue
        
        players.sort(key=str.lower)
        
        for player in players:
            page_text += f"<li id='{player.lower()}'><img src='https://mc-heads.net/avatar/{player.lower()}/8.png'>{player}</li>\n"
        page_text += "</ul>"
        if page_text_hash != (_t_t_h := txt_to_hash(page_text)):
            print("[WBroker HTML] Sending to page...")
            rentry.edit(os.environ.get("RENTRY_PAGE"), os.environ.get("RENTRY_PASSWD"), page_text)
            print("[WBroker HTML] Whitelist sent.")
            page_text_hash = _t_t_h
        else:
            print("Page hasn't changed!")
        
        send_stdin_command(server_id, os.environ.get("CRAFTY_TOKEN"), f"setmotd {random.choice(motd_list)}")
        time.sleep(5*60)