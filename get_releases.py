from xmlrpc.client import ServerProxy
from collections import defaultdict
from progressbar import ProgressBar, Bar, ETA, AdaptiveETA, Percentage

pypi = ServerProxy("http://pypi.python.org/pypi")

start = pypi.changelog_last_serial()

packages = pypi.list_packages()

releases = defaultdict(list)

pb = ProgressBar(widgets=[Percentage(), ' ', Bar(), ' ', ETA(), ' ', AdaptiveETA()])

for pkg in pb(packages):
    rel = pypi.package_releases(pkg)
    all = pypi.package_releases(pkg, True)
    releases[pkg] = (set(rel), set(all)-set(rel))
    for r in all:
        urls = release_urls(pkg, r)
        data = release_data(pkg, r)
        dl = release_downloads(pkg, r)

end = pypi.changelog_last_serial()

if end > start:
    print("{} changes while this code ran".format(end-start))
