import json
import datetime
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql import select, func

from progressbar import ProgressBar, Bar, Percentage, AdaptiveETA
def pb(name):
    return [name, ': ', Percentage(), ' ', Bar(), ' ', AdaptiveETA()]

engine = create_engine('sqlite:///pypi.db')
metadata = MetaData(bind=engine)
releases = Table('releases', metadata, autoload=True)

for n_rel, in select([func.count()]).select_from(releases).execute():
    print(n_rel)

e2 = create_engine('sqlite:///p2.db')
from pypi.schema import metadata as m2
m2.bind=e2
m2.create_all()

with e2.begin() as conn:
    pbar = ProgressBar(widgets=pb('Packages'))
    l = list(select([releases.c.package]).select_from(releases).group_by(releases.c.package).execute())
    for p, in pbar(l):
        # print(p)
        conn.execute(m2.tables['packages'].insert().values(name=p))

    pbar = ProgressBar(widgets=pb('Releases'), maxval=n_rel)
    pbar.start()
    for i, r in enumerate(releases.select().execute()):
        pbar.update(i+1)
        try:
            j = json.loads(r.json)
        except ValueError:
            # print("Invalid JSON for {}/{}".format(r.package, r.version))
            continue
        info = j['info']
        urls = j['urls']
        ins = m2.tables['releases'].insert().values(
            name=r.package,
            version=r.version,
            stable_version=info.get('stable_version'),

            author=info.get('author'),
            author_email=info.get('author_email'),
            maintainer=info.get('maintainer'),
            maintainer_email=info.get('maintainer_email'),

            home_page=info.get('home_page'),
            license=info.get('license'),
            summary=info.get('summary'),
            description=info.get('description'),
            keywords=info.get('keywords'),

            platform=info.get('platform'),
            requires_python=info.get('requires_python'),

            download_url=info.get('download_url'),
            bugtrack_url=info.get('bugtrack_url'),
            docs_url=info.get('docs_url'),
            package_url=info.get('package_url'),
            release_url=info.get('release_url'),

            _pypi_hidden=info.get('_pypi_hidden'),
            _pypi_ordering=info.get('_pypi_ordering'),
            cheesecake_code_kwalitee_id=info.get('cheesecake_code_kwalitee_id'),
            cheesecake_documentation_id=info.get('cheesecake_documentation_id'),
            cheesecake_installability_id=info.get('cheesecake_installability_id'),
        )
        conn.execute(ins)
        for req_type in ('provides', 'requires', 'obsoletes', 'provides_dist', 'requires_dist', 'obsoletes_dist', 'requires_external'):
            reqs = info.get(req_type, [])
            for i, req in enumerate(reqs):
                ins2 = m2.tables['dependencies'].insert().values(
                    name=r.package,
                    version=r.version,
                    type=req_type,
                    id=i+1,
                    requirement=req,
                )
                conn.execute(ins2)
        for i, url in enumerate(info.get('project_url', [])):
            ins3 = m2.tables['project_urls'].insert().values(
                name=r.package,
                version=r.version,
                id=i+1,
                url=url,
            )
            conn.execute(ins3)
        for i, c in enumerate(info.get('classifiers', [])):
            ins4 = m2.tables['classifiers'].insert().values(
                name=r.package,
                version=r.version,
                id=i+1,
                classifier=c,
            )
            conn.execute(ins4)
        if urls:
            for i, u in enumerate(urls):
                upl = datetime.datetime.strptime(u['upload_time'], '%Y-%m-%dT%H:%M:%S')
                ins5 = m2.tables['urls'].insert().values(
                    name=r.package,
                    version=r.version,
                    id=i+1,
                    filename=u['filename'],
                    has_sig=int(u['has_sig']), # Boolean
                    md5_digest=u['md5_digest'],
                    comment_text=u['comment_text'],
                    packagetype=u['packagetype'],
                    python_version=u['python_version'],
                    downloads=int(u['downloads']), # Integer
                    size=int(u['size']), # Integer
                    upload_time=upl, # DateTime
                )
                conn.execute(ins5)
            dl = info.get('downloads', {})
            ins6 = m2.tables['downloads'].insert().values(
                name=r.package,
                version=r.version,
                last_month=int(dl.get('last_month', 0)),
                last_week=int(dl.get('last_week', 0)),
                last_day=int(dl.get('last_day', 0)),
            )
            conn.execute(ins6)
    pbar.finish()

    for t in m2.sorted_tables:
        for n, in conn.execute(select([func.count()]).select_from(t)):
            print(t.name, n)

##e2.execute("attach database 'p.db' as p")
##pbar = ProgressBar(widgets=pb('Copy'))
##for tbl in pbar(m2.sorted_tables):
##    e2.execute("create table p.{name} as select * from {name}".format(name=tbl.name))
