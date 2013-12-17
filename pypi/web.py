from xmlrpc.client import ServerProxy
import datetime

PYPI_URL = 'http://pypi.python.org/pypi'
pypi = ServerProxy(PYPI_URL)

class Package:
    def __init__(self, name, include_hidden=False):
        self.name = name
        self.releases = []
        self.include_hidden = include_hidden

    def get(self):
        releases = pypi.package_releases(self.name, self.include_hidden)
        self.releases = [Release(self.name, r) for r in releases]
        for r in self.releases:
            r.get()

class Release:
    def __init__(self, name, version):
        self.name = name
        self.version = version
        self.data = {}
        self.classifiers = []
        self.urls = []

    def get(self):
        data = pypi.release_data(self.name, self.version)
        if not data:
            raise ValueError("Invalid release: {}[{}]".format(self.name, self.version))
        self.data = data
        self.urls = pypi.release_urls(self.name, self.version)

class Changelog:
    def __init__(self, since):
        self.timestamp = None
        self.serial = None
        if isinstance(since, datetime.datetime):
            self.timestamp = int((dt - datetime(1970,1,1)).total_seconds())
        else:
            self.serial = since
        self.changes = []

    def get(self):
        if self.timestamp:
            changes = pypi.changelog(self.timestamp, True)
        else:
            changes = pypi.changelog_since_serial(self.serial)
        self.changes = changes

    def changed(self):
        packages = set()
        releases = set()
        for name, version, timestamp, action, serial in self.changes:
            if version is None:
                packages.add(name)
        for name, version, timestamp, action, serial in self.changes:
            if name not in packages:
                releases.add((name, version))
        return packages, releases
