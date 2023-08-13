from .db.session import SessionLocal


def get_db():
    with SessionLocal() as session:
        yield session
