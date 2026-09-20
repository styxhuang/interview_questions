from app.config import get_settings
from db.database import build_engine, init_database


def main() -> None:
    settings = get_settings()
    engine = build_engine(settings.database_url)
    init_database(engine)
    print(f"initialized database: {settings.database_url}")


if __name__ == "__main__":
    main()
