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

def txt_to_hash(_text):
    _m = hashlib.sha256(_text.encode('UTF-8'))
    return _m.hexdigest()

if __name__ == "__main__":
    page_text_hash = ""
    while True:
        page_text = "<h1>Whitelisted users</h1>\n<hr />\n<ul>"
        players = []
        # for thingy in whitelist_manupdate.sql_reader("SELECT mc_username FROM usertable where mc_username IS NOT NULL ORDER BY mc_username ASC"):
        #     page_text += f"<li id='{thingy['mc_username'].lower()}'>{thingy['mc_username']}</li>\n"
        for thingy in whitelist_manupdate.get_player_whitelist():
            players.append(thingy['name'])

        players.sort()
        
        for player in players:
            page_text += f"<li id='{player.lower()}'><img src='https://minotar.net/helm/{player.lower()}/8.png'>{player}</li>\n"
        page_text += "</ul>"
        if page_text_hash != (_t_t_h := txt_to_hash(page_text)):
            print("[WBroker HTML] Sending to page...")
            rentry.edit(os.environ.get("RENTRY_PAGE"), os.environ.get("RENTRY_PASSWD"), page_text)
            print("[WBroker HTML] Whitelist sent.")
            page_text_hash = _t_t_h
        else:
            print("Page hasn't changed!")
        time.sleep(20*60)