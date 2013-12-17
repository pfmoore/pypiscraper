from .web import Package, Release
from .schema import packages, releases, classifiers, downloads, urls

def get_release(name, version):
    rel = Release(name, version)
    rel.get()

    d = {}
    for col in releases.columns:
        if col.name in rel.data:
            d[col.name] = rel.data[col.name]
    ins = releases.insert().values(**d)
    return ins

# import pypi
# from sqlalchemy import create_engine
# engine = create_engine('sqlite:///:memory:')
# from pypi.schema import metadata, releases
# metadata.bind = engine
# ins = pypi.get_releaset('pip', '1.4.1')
# releases.create()
# ins.execute()
# engine.execute("select * from releases").fetchone()
