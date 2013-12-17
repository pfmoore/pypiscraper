import json
from xmlrpc.client import ServerProxy

pypi = ServerProxy("http://pypi.python.org/pypi")

now = pypi.changelog_last_serial()
changes = pypi.changelog_since_serial(now-200000)
with open("changes.json", "w") as f:
    json.dump((now, changes), f)
