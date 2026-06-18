from sqlalchemy import text

from app.db.session import engine


def main() -> None:
    with engine.connect() as conn:
        row = conn.execute(text("SELECT current_database(), current_user, now()")).fetchone()
        print("Connected:", row)


if __name__ == "__main__":
    main()