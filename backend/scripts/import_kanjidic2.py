#!/usr/bin/env python3
"""
Import KANJIDIC2 (Kanji dictionary) data.

For development/testing, uses sample data.
For production, downloads and parses the full KANJIDIC2 XML file.
"""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.utils.content_utils import upsert_kanji
from scripts.generate_sample_data import generate_n5_kanji


async def import_kanjidic2(
    session: AsyncSession,
    jlpt_levels: List[str] = None,
    use_sample_data: bool = True,
) -> dict:
    """
    Import KANJIDIC2 kanji data.

    Args:
        session: Database session
        jlpt_levels: List of JLPT levels to import (e.g., ["N5", "N4"])
        use_sample_data: If True, use generated sample data instead of downloading

    Returns:
        Dictionary with import statistics
    """
    if jlpt_levels is None:
        jlpt_levels = ["N5"]

    imported = 0
    updated = 0
    skipped = 0

    if use_sample_data:
        # Use sample data for testing
        print("Using sample N5 kanji data...")
        kanji_list = generate_n5_kanji()

        # Filter by JLPT level
        kanji_list = [k for k in kanji_list if k["jlpt_level"] in jlpt_levels]

        # Import to database
        for kanji_data in kanji_list:
            try:
                await upsert_kanji(session, kanji_data)
                imported += 1
                print(f"  Imported: {kanji_data['character']} - {', '.join(kanji_data['meanings'][:2])}")
            except Exception as e:
                print(f"  Error importing {kanji_data.get('character')}: {e}")
                skipped += 1

    else:
        # TODO: Implement actual KANJIDIC2 XML parsing
        # This would download from https://www.edrdg.org/wiki/index.php/KANJIDIC_Project
        # and parse the XML using app.utils.content_utils.parse_kanjidic_entry
        print("ERROR: Full KANJIDIC2 import not yet implemented.")
        print("Use --sample flag to import sample data.")
        return {"imported": 0, "updated": 0, "skipped": 0}

    return {
        "imported": imported,
        "updated": updated,
        "skipped": skipped,
    }


def parse_args(args=None):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Import KANJIDIC2 kanji data"
    )
    parser.add_argument(
        "--level",
        type=str,
        default="N5",
        help="Comma-separated JLPT levels to import (default: N5)",
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        default=True,
        help="Use sample data (default)",
    )
    parser.add_argument(
        "--real",
        action="store_true",
        help="Download and use real KANJIDIC2 data (not yet implemented)",
    )

    return parser.parse_args(args)


async def main_async():
    """Async main function."""
    args = parse_args()

    # Parse JLPT levels
    jlpt_levels = [level.strip() for level in args.level.split(",")]

    # Use sample data unless --real is specified
    use_sample = not args.real

    print(f"Importing KANJIDIC2 kanji for levels: {', '.join(jlpt_levels)}")
    if use_sample:
        print("(Using sample data)")

    # Import data
    async with AsyncSessionLocal() as session:
        stats = await import_kanjidic2(
            session=session,
            jlpt_levels=jlpt_levels,
            use_sample_data=use_sample,
        )

        print("\n=== Import Statistics ===")
        print(f"Imported: {stats['imported']}")
        print(f"Updated:  {stats['updated']}")
        print(f"Skipped:  {stats['skipped']}")


def main():
    """Main entry point."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
