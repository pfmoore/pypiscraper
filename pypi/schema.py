from sqlalchemy import (
        Table, Column, Boolean, Integer, String, DateTime, MetaData,
        ForeignKeyConstraint, CheckConstraint
    )
from sqlalchemy.sql import and_

metadata = MetaData()

packages = Table("packages", metadata,
        Column('name', String, primary_key=True),

        Column('updated', DateTime),
        Column('update_serial', Integer),
    )

releases = Table("releases", metadata,
        Column('name', String, primary_key=True),
        Column('version', String, primary_key=True),
        Column('stable_version', String),

        Column('author', String),
        Column('author_email', String),
        Column('maintainer', String),
        Column('maintainer_email', String),

        Column('home_page', String),
        Column('license', String),
        Column('summary', String),
        Column('description', String),
        Column('keywords', String),

        Column('platform', String),
        Column('provides', String),
        Column('provides_dist', String),
        Column('requires', String),
        Column('requires_dist', String),
        Column('requires_external', String),
        Column('requires_python', String),
        Column('obsoletes', String),
        Column('obsoletes_dist', String),

        Column('download_url', String),
        Column('project_url', String),
        Column('bugtrack_url', String),
        Column('docs_url', String),
        Column('package_url', String),
        Column('release_url', String),

        Column('_pypi_hidden', Boolean),
        Column('_pypi_ordering', Integer),
        Column('cheesecake_code_kwalitee_id', String),
        Column('cheesecake_documentation_id', String),
        Column('cheesecake_installability_id', String),

        Column('updated', DateTime),
        Column('update_serial', Integer),

        ForeignKeyConstraint(['name'], ['packages.name'],
            name='releases_packages_fk',
            ondelete='CASCADE', onupdate='CASCADE'),
    )

classifiers = Table("classifiers", metadata,
        Column("name", String, primary_key=True),
        Column("version", String, primary_key=True),
        Column("id", Integer, primary_key=True),
        Column("classifier", String),

        Column('updated', DateTime),
        Column('update_serial', Integer),

        ForeignKeyConstraint(['name', 'version'], ['releases.name', 'releases.version'],
            name='classifiers_releases_fk',
            ondelete='CASCADE', onupdate='CASCADE'),
    )

project_urls = Table("project_urls", metadata,
        Column("name", String, primary_key=True),
        Column("version", String, primary_key=True),
        Column("id", Integer, primary_key=True),
        Column("url", String),

        Column('updated', DateTime),
        Column('update_serial', Integer),

        ForeignKeyConstraint(['name', 'version'], ['releases.name', 'releases.version'],
            name='project_url_releases_fk',
            ondelete='CASCADE', onupdate='CASCADE'),
    )

dependencies = Table("dependencies", metadata,
        Column("name", String, primary_key=True),
        Column("version", String, primary_key=True),
        Column("type", String,
            CheckConstraint("type in ('provides', 'requires', 'obsoletes', 'provides_dist', 'requires_dist', 'obsoletes_dist', 'requires_external')"),
            primary_key=True,
        ),
        Column("id", Integer, primary_key=True),
        Column("requirement", String),

        Column('updated', DateTime),
        Column('update_serial', Integer),

        ForeignKeyConstraint(['name', 'version'], ['releases.name', 'releases.version'],
            name='dependencies_releases_fk',
            ondelete='CASCADE', onupdate='CASCADE'),
    )


downloads = Table("downloads", metadata,
        Column("name", String, primary_key=True),
        Column("version", String, primary_key=True),
        Column("last_month", Integer),
        Column("last_week", Integer),
        Column("last_day", Integer),

        Column('updated', DateTime),
        Column('update_serial', Integer),

        ForeignKeyConstraint(['name', 'version'], ['releases.name', 'releases.version'],
            name='downloads_releases_fk',
            ondelete='CASCADE', onupdate='CASCADE'),
    )

urls = Table("urls", metadata,
        Column("name", String, primary_key=True),
        Column("version", String, primary_key=True),
        Column("id", Integer, primary_key=True),

        Column("url", String),
        Column("filename", String),
        Column("has_sig", Boolean),
        Column("md5_digest", String),

        Column("comment_text", String),
        Column("packagetype", String),
        Column("python_version", String),

        Column("downloads", Integer),
        Column("size", Integer),
        Column("upload_time", DateTime),

        Column('updated', DateTime),
        Column('update_serial', Integer),

        ForeignKeyConstraint(['name', 'version'], ['releases.name', 'releases.version'],
            name='urls_releases_fk',
            ondelete='CASCADE', onupdate='CASCADE'),
    )

def delete(name, version=None):
    tables = [urls, downloads, classifiers, releases]
    if version is None:
        tables.append(packages)
    statements = []
    for t in tables:
        if version is None:
            cond = (t.c.name == name)
        else:
            cond = and_(
                t.c.name == name,
                t.c.version == version
            )
        statements.append(t.delete().where(cond))
    return statements
