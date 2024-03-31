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

import requests
import rentry
import whitelist_manupdate
import os
import hashlib

def txt_to_hash(_text):
    _m = hashlib.sha256(_text.encode('UTF-8'))
    return _m.hexdigest()

if __name__ == "__main__":
    page_text = "<h1>Whitelisted users</h1>\n<hr />\n<ul>"
    for thingy in whitelist_manupdate.sql_reader("SELECT mc_username FROM usertable where mc_username IS NOT NULL ORDER BY mc_username DESC"):
        page_text += f"<li>{thingy['mc_username']}</li>\n"
    page_text += "</ul>"
    rentry.edit(os.environ.get("RENTRY_PAGE"), os.environ.get("RENTRY_PASSWD"), page_text)