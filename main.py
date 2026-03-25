"""
Main entry-point for the IndiaMART Data Engineering pipeline.

Usage:
    python main.py scrape          # Run the live web scraper
    python main.py sample          # Generate realistic sample data (offline)
    python main.py etl             # Run ETL on the latest raw data
    python main.py all             # sample → ETL  (full offline pipeline)
    python main.py scrape-all      # scrape → ETL  (full live pipeline)
"""

import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == "scrape":
        from src.scraper import run_scraper
        run_scraper()

    elif command == "sample":
        from src.sample_data import generate_sample_data
        generate_sample_data()

    elif command == "etl":
        from src.etl import run_etl
        run_etl()

    elif command == "all":
        from src.sample_data import generate_sample_data
        from src.etl import run_etl
        raw_path = generate_sample_data()
        run_etl(raw_path)

    elif command == "scrape-all":
        from src.scraper import run_scraper
        from src.etl import run_etl
        raw_path = run_scraper()
        run_etl(raw_path)

    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)
        


if __name__ == "__main__":
    main()
