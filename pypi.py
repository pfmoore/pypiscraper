import sys
import sqlite3
from xmlrpc.client import ServerProxy

PYPI_URL = 'http://pypi.python.org/pypi'
pypi = ServerProxy(PYPI_URL)

db = sqlite3.connect('pypi.db')

def add_version(project, version, c):
    metadata = pypi.release_data(project, version)
    keys = ['name', 'version', 'stable_version', 'author', 'author_email', 'maintainer',
        'maintainer_email', 'home_page', 'license', 'summary', 'description', 'keywords',
        'platform', 'download_url', 'requires', 'requires_dist', 'provides', 'provides_dist',
        'requires_external', 'requires_python', 'obsoletes', 'obsoletes_dist', 'project_url',
        'docs_url']
    for k in keys:
        if k not in metadata or metadata[k] is None:
            metadata[k] = ''
    c.execute("delete from metadata where package = ? and version = ?",
            (project, version))
    c.execute("delete from classifiers where package = ? and version = ?",
            (project, version))
    c.execute("delete from urls where package = ? and version = ?",
            (project, version))
    print("{}: {}:: {} - {}".format(project, version, type(metadata['requires']), metadata['requires']))
    c.execute("""insert into metadata (
            package,
            version,
            stable_version,
            author,
            author_email,
            maintainer,
            maintainer_email,
            home_page,
            license,
            summary,
            description,
            keywords,
            platform,
            download_url,
            requires,
            requires_dist,
            provides,
            provides_dist,
            requires_external,
            requires_python,
            obsoletes,
            obsoletes_dist,
            project_url,
            docs_url
        )
        values (
            :name,
            :version,
            :stable_version,
            :author,
            :author_email,
            :maintainer,
            :maintainer_email,
            :home_page,
            :license,
            :summary,
            :description,
            :keywords,
            :platform,
            :download_url,
            :requires,
            :requires_dist,
            :provides,
            :provides_dist,
            :requires_external,
            :requires_python,
            :obsoletes,
            :obsoletes_dist,
            :project_url,
            :docs_url
        )""", metadata)
    c.executemany("""insert into classifiers (
            package, version, classifier
        )
        values (?, ?, ?)""",
        [(project, version, c) for c in metadata['classifiers']])
    urls = pypi.release_urls(project, version)
    keys = ['url', 'packagetype', 'filename', 'size', 'md5_digest',
        'downloads', 'has_sig', 'python_version', 'comment_text']
    for url in urls:
        url['package'] = project
        url['version'] = version
        for k in keys:
            if k not in url or url[k] is None:
                url[k] = ''
    c.executemany("""insert into urls (
        package,
        version,
        url,
        packagetype,
        filename,
        size,
        md5_digest,
        downloads,
        has_sig,
        python_version,
        comment_text
    )
    values (
        :package,
        :version,
        :url,
        :packagetype,
        :filename,
        :size,
        :md5_digest,
        :downloads,
        :has_sig,
        :python_version,
        :comment_text
    )""", urls)

def add_project(project, c):
    sys.stdout.write('.')
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
    c.execute("delete from metadata")
    c.execute("delete from classifiers")
    c.execute("delete from urls")

def reload_packages():
    c = db.cursor()
    clear(c)
    pkg = pypi.list_packages()
    c.executemany("insert into packages (package, updated_serial) values (?, NULL)",
        [(p,) for p in pkg])
    db.commit()
    return len(pkg)

def load_batch(n):
    ser = pypi.changelog_last_serial()
    c = db.cursor()
    c.execute("""select package from packages where updated_serial is null
    order by package
    limit ?""", (n,))
    for pkg, in c.fetchall():
        c.execute("""update packages
        set updated_serial = ?
        where package = ?""", (ser, pkg))
        add_project(pkg, c)
    db.commit()

if __name__ == '__main__':
    n = reload_packages()
    tot = 0
    while tot < n:
        sys.stdout.write(" " * 50)
        sys.stdout.write("\r" * 50)
        sys.stdout.write("{}/{} ".format(tot, n))
        load_batch(10)
        tot += 10

    sys.stdout.write(" " * 30)
    sys.stdout.write("\r" * 30)
    sys.stdout.write("Complete!")
