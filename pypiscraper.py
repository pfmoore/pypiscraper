import baker

@baker.command
def create(db):
    """Create a new database with an empty application schema.

    The database is specified using a SQLAlchemy style database URI.
    """
    from sqlalchemy import create_engine
    from pypi.schema import metadata
    engine = create_engine(db)
    metadata.create_all(engine)

if __name__ == '__main__':
    baker.run()
