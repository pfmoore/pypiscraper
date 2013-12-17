import sys
import sqlite3
from xmlrpc.client import ServerProxy
import requests
from datetime import datetime

PYPI_URL = 'http://pypi.python.org/pypi'
pypi = ServerProxy(PYPI_URL)
db = sqlite3.connect('pypi.db')

def add_version(project, version, c):
    r = requests.get('https://pypi.python.org/pypi/{}/{}/json'.format(project,
        version))
    c.execute("update releases set json = ? where package = ? and version = ?", (r.text,
        project, version))

def add_project(project, c):
    sys.stdout.write('.')
    sys.stdout.flush()
    r = requests.get('https://pypi.python.org/pypi/{}/json'.format(project))
    c.execute("update packages set json = ? where package = ?", (r.text,
        project))
    c.execute("delete from releases where package = ?", (project,))
    rels = set(pypi.package_releases(project, False))
    all = set(pypi.package_releases(project, True))
    c.executemany("insert into releases (package, version, hidden) values (?, ?, ?)",
        [(project, r, r not in rels) for r in all])
    for rel in all:
        add_version(project, rel, c)

def clear(c):
    c.execute("delete from packages")
    c.execute("delete from releases")

def reload_packages(do_clear=False):
    c = db.cursor()
    if do_clear:
        clear(c)
        pkg = pypi.list_packages()
        c.executemany("insert into packages (package, json) values (?, NULL)",
            [(p,) for p in pkg])
        db.commit()
        return len(pkg), 0
    else:
        c.execute("select count(*), count(json) from packages")
        total, done = c.fetchone()
        return total, done

def load_batch(n):
    c = db.cursor()
    c.execute("""select package from packages where json is null
    order by package
    limit ?""", (n,))
    for pkg, in c.fetchall():
        add_project(pkg, c)
    db.commit()

def get_since(dt):
    timestamp = int((dt - datetime(1970,1,1)).total_seconds())
    changes = pypi.changelog(timestamp, True)
    c = db.cursor()
    update_projects(changes, c)

def get_updates():
    c = db.cursor()
    c.execute("""select latest from last_serial""")
    get_from = int(c.fetchone()[0])
    changes = pypi.changelog_since_serial(get_from)
    if changes:
        update_projects(changes, c)
    else:
        print("No changes to apply.")

def update_projects(changes, c):
    c.execute("""update last_serial set latest = ?""", (changes[-1][4],))
    projects_changed = set()
    for name, version, timestamp, action, serial in changes:
        projects_changed.add(name)
    print("Projects to update:", len(projects_changed))
    for i, project in enumerate(projects_changed):
        print("Updating", i, project)
        c.execute("""delete from packages where package = ?""", (project,))
        c.execute("""insert into packages (package, json) values (?, NULL)""", (project,))
        add_project(project, c)
        db.commit()

def total_load():
    n, tot = reload_packages()
    while tot < n:
        sys.stdout.write("\r")
        sys.stdout.write(" " * 50)
        sys.stdout.write("\r")
        sys.stdout.write("{}/{} ".format(tot, n))
        sys.stdout.flush()
        load_batch(10)
        tot += 10

    sys.stdout.write("\r")
    sys.stdout.write(" " * 50)
    sys.stdout.write("\r")
    sys.stdout.write("Complete!\n")
    sys.stdout.flush()

def get_since_5_dec():
    dt = datetime(2013,12,5)
    get_since(dt)

if __name__=='__main__':
    get_updates()
