from app.config import Settings


def run() -> None:
    settings = Settings()
    print(f"Kalshi bot starting in {settings.kalshi_env.value} mode")


if __name__ == "__main__":
    run()
