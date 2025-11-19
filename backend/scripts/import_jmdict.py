#!/usr/bin/env python3
"""
Import JMDict (Japanese-English dictionary) data.

For development/testing, uses sample data.
For production, downloads and parses the full JMDict XML file.
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
from app.utils.content_utils import upsert_vocabulary, determine_jlpt_level
from scripts.generate_sample_data import generate_n5_vocabulary


async def import_jmdict(
    session: AsyncSession,
    jlpt_levels: List[str] = None,
    limit: int = None,
    use_sample_data: bool = True,
) -> dict:
    """
    Import JMDict vocabulary data.

    Args:
        session: Database session
        jlpt_levels: List of JLPT levels to import (e.g., ["N5", "N4"])
        limit: Maximum number of entries to import
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
        print("Using sample N5 vocabulary data...")
        vocab_list = generate_n5_vocabulary()

        # Filter by JLPT level
        vocab_list = [v for v in vocab_list if v["jlpt_level"] in jlpt_levels]

        # Apply limit
        if limit:
            vocab_list = vocab_list[:limit]

        # Import to database
        for vocab_data in vocab_list:
            try:
                await upsert_vocabulary(session, vocab_data)
                imported += 1
                print(f"  Imported: {vocab_data['word']} ({vocab_data['reading']})")
            except Exception as e:
                print(f"  Error importing {vocab_data.get('word')}: {e}")
                skipped += 1

    else:
        # TODO: Implement actual JMDict XML parsing
        # This would download from https://www.edrdg.org/jmdict/j_jmdict.html
        # and parse the XML using app.utils.content_utils.parse_jmdict_entry
        print("ERROR: Full JMDict import not yet implemented.")
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
        description="Import JMDict vocabulary data"
    )
    parser.add_argument(
        "--level",
        type=str,
        default="N5",
        help="Comma-separated JLPT levels to import (default: N5)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of entries to import",
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
        help="Download and use real JMDict data (not yet implemented)",
    )

    return parser.parse_args(args)


async def main_async():
    """Async main function."""
    args = parse_args()

    # Parse JLPT levels
    jlpt_levels = [level.strip() for level in args.level.split(",")]

    # Use sample data unless --real is specified
    use_sample = not args.real

    print(f"Importing JMDict vocabulary for levels: {', '.join(jlpt_levels)}")
    if use_sample:
        print("(Using sample data)")

    # Import data
    async with AsyncSessionLocal() as session:
        stats = await import_jmdict(
            session=session,
            jlpt_levels=jlpt_levels,
            limit=args.limit,
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
