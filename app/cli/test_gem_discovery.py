from app.db.session import SessionLocal
from app.sources.gem.discovery import GeMDiscoveryRunner


def main() -> None:
    db = SessionLocal()
    try:
        runner = GeMDiscoveryRunner(db)
        result = runner.run()
        print(result)
    finally:
        db.close()


if __name__ == "__main__":
    main()
