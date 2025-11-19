"""
Integration tests for import scripts (JMDict and KANJIDIC2).

TDD PHASE: RED - These tests will fail until scripts are implemented.
"""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vocabulary import Vocabulary
from app.models.kanji import Kanji


class TestSampleDataGeneration:
    """Test sample data generator functionality."""

    @pytest.mark.asyncio
    async def test_generate_sample_n5_kanji(self, db_session: AsyncSession):
        """Test generating and importing sample N5 kanji data."""
        # This will be implemented with the sample data generator
        # For now, we manually create sample data to test the import flow
        from scripts.generate_sample_data import generate_n5_kanji

        # Act
        kanji_list = generate_n5_kanji()

        # Assert
        assert len(kanji_list) >= 20
        assert all("character" in k for k in kanji_list)
        assert all("meanings" in k for k in kanji_list)
        assert all(k.get("jlpt_level") == "N5" for k in kanji_list)

        # Verify essential N5 kanji are included
        characters = [k["character"] for k in kanji_list]
        essential_kanji = ["日", "月", "火", "水", "木", "金", "土"]
        assert all(k in characters for k in essential_kanji)

    @pytest.mark.asyncio
    async def test_generate_sample_n5_vocabulary(self, db_session: AsyncSession):
        """Test generating and importing sample N5 vocabulary data."""
        from scripts.generate_sample_data import generate_n5_vocabulary

        # Act
        vocab_list = generate_n5_vocabulary()

        # Assert
        assert len(vocab_list) >= 100
        assert all("word" in v for v in vocab_list)
        assert all("reading" in v for v in vocab_list)
        assert all("meanings" in v for v in vocab_list)
        assert all(v.get("jlpt_level") == "N5" for v in vocab_list)

        # Verify essential vocabulary is included
        words = [v["word"] for v in vocab_list]
        essential_words = ["これ", "それ", "あれ", "私", "日本"]
        # At least some essential words should be present
        assert any(w in words for w in essential_words)

    @pytest.mark.asyncio
    async def test_import_sample_data_to_database(self, db_session: AsyncSession):
        """Test importing sample data into the database."""
        from scripts.generate_sample_data import import_sample_data_to_db

        # Act
        stats = await import_sample_data_to_db(db_session)

        # Assert
        assert stats["kanji_count"] >= 20
        assert stats["vocabulary_count"] >= 100

        # Verify data is in database
        result = await db_session.execute(
            select(Kanji).where(Kanji.jlpt_level == "N5")
        )
        kanji_list = result.scalars().all()
        assert len(kanji_list) >= 20

        result = await db_session.execute(
            select(Vocabulary).where(Vocabulary.jlpt_level == "N5")
        )
        vocab_list = result.scalars().all()
        assert len(vocab_list) >= 100


class TestJMDictImport:
    """Test JMDict import functionality."""

    @pytest.mark.asyncio
    async def test_import_jmdict_filters_by_jlpt_level(self, db_session: AsyncSession):
        """Test that JMDict import correctly filters by JLPT level."""
        from scripts.import_jmdict import import_jmdict

        # Act - Import only N5 vocabulary
        stats = await import_jmdict(
            db_session,
            jlpt_levels=["N5"],
            limit=50,
            use_sample_data=True  # Use sample data for testing
        )

        # Assert
        assert stats["imported"] > 0
        assert stats["skipped"] >= 0

        # Verify only N5 vocab was imported
        result = await db_session.execute(select(Vocabulary))
        all_vocab = result.scalars().all()
        assert all(v.jlpt_level == "N5" for v in all_vocab)

    @pytest.mark.asyncio
    async def test_import_jmdict_handles_duplicates(self, db_session: AsyncSession):
        """Test that re-importing JMDict data handles duplicates correctly."""
        from scripts.import_jmdict import import_jmdict

        # Act - Import twice
        stats1 = await import_jmdict(
            db_session,
            jlpt_levels=["N5"],
            limit=10,
            use_sample_data=True
        )
        stats2 = await import_jmdict(
            db_session,
            jlpt_levels=["N5"],
            limit=10,
            use_sample_data=True
        )

        # Assert - Second import should update, not duplicate
        result = await db_session.execute(select(Vocabulary))
        vocab_count = len(result.scalars().all())

        # Should not double the count
        assert vocab_count == stats1["imported"]
        assert stats2["updated"] > 0 or stats2["skipped"] > 0

    @pytest.mark.asyncio
    async def test_import_jmdict_respects_limit(self, db_session: AsyncSession):
        """Test that JMDict import respects the limit parameter."""
        from scripts.import_jmdict import import_jmdict

        # Act
        limit = 20
        stats = await import_jmdict(
            db_session,
            jlpt_levels=["N5"],
            limit=limit,
            use_sample_data=True
        )

        # Assert
        assert stats["imported"] <= limit

        result = await db_session.execute(select(Vocabulary))
        vocab_count = len(result.scalars().all())
        assert vocab_count <= limit


class TestKANJIDIC2Import:
    """Test KANJIDIC2 import functionality."""

    @pytest.mark.asyncio
    async def test_import_kanjidic_filters_by_jlpt_level(self, db_session: AsyncSession):
        """Test that KANJIDIC2 import correctly filters by JLPT level."""
        from scripts.import_kanjidic2 import import_kanjidic2

        # Act - Import only N5 kanji
        stats = await import_kanjidic2(
            db_session,
            jlpt_levels=["N5"],
            use_sample_data=True
        )

        # Assert
        assert stats["imported"] > 0

        # Verify only N5 kanji was imported
        result = await db_session.execute(select(Kanji))
        all_kanji = result.scalars().all()
        assert all(k.jlpt_level == "N5" for k in all_kanji)
        assert len(all_kanji) >= 20  # Minimum N5 kanji

    @pytest.mark.asyncio
    async def test_import_kanjidic_includes_grade_1_kanji(self, db_session: AsyncSession):
        """Test that N5 import includes all grade 1 kanji."""
        from scripts.import_kanjidic2 import import_kanjidic2

        # Act
        stats = await import_kanjidic2(
            db_session,
            jlpt_levels=["N5"],
            use_sample_data=True
        )

        # Assert - Grade 1 kanji should be included
        result = await db_session.execute(
            select(Kanji).where(Kanji.grade == 1)
        )
        grade_1_kanji = result.scalars().all()
        assert len(grade_1_kanji) > 0

        # Essential grade 1 kanji
        result = await db_session.execute(
            select(Kanji).where(Kanji.character.in_(["日", "月", "火", "水"]))
        )
        essential = result.scalars().all()
        assert len(essential) == 4

    @pytest.mark.asyncio
    async def test_import_kanjidic_handles_duplicates(self, db_session: AsyncSession):
        """Test that re-importing KANJIDIC2 data handles duplicates correctly."""
        from scripts.import_kanjidic2 import import_kanjidic2

        # Act - Import twice
        stats1 = await import_kanjidic2(
            db_session,
            jlpt_levels=["N5"],
            use_sample_data=True
        )
        stats2 = await import_kanjidic2(
            db_session,
            jlpt_levels=["N5"],
            use_sample_data=True
        )

        # Assert
        result = await db_session.execute(select(Kanji))
        kanji_count = len(result.scalars().all())

        # Should not duplicate (kanji.character is unique)
        assert kanji_count == stats1["imported"]
        assert stats2["updated"] > 0 or stats2["skipped"] > 0


class TestImportCLI:
    """Test command-line interface for import scripts."""

    def test_jmdict_import_cli_args(self):
        """Test JMDict import script accepts correct CLI arguments."""
        from scripts.import_jmdict import parse_args

        # Act
        args = parse_args(["--level", "N5,N4", "--limit", "1000"])

        # Assert
        assert args.level == "N5,N4"
        assert args.limit == 1000

    def test_kanjidic_import_cli_args(self):
        """Test KANJIDIC2 import script accepts correct CLI arguments."""
        from scripts.import_kanjidic2 import parse_args

        # Act
        args = parse_args(["--level", "N5,N4,N3"])

        # Assert
        assert args.level == "N5,N4,N3"

    def test_sample_data_generator_cli_args(self):
        """Test sample data generator accepts correct CLI arguments."""
        from scripts.generate_sample_data import parse_args

        # Act
        args = parse_args(["--output", "test_data.json"])

        # Assert
        assert args.output == "test_data.json"


class TestDataValidation:
    """Test validation of imported data."""

    @pytest.mark.asyncio
    async def test_imported_kanji_has_required_fields(self, db_session: AsyncSession):
        """Test that imported kanji has all required fields."""
        from scripts.generate_sample_data import import_sample_data_to_db

        # Act
        await import_sample_data_to_db(db_session)

        # Assert - Get a sample kanji
        result = await db_session.execute(
            select(Kanji).where(Kanji.character == "水")
        )
        kanji = result.scalar_one_or_none()

        assert kanji is not None
        assert kanji.character == "水"
        assert len(kanji.meanings) > 0
        assert len(kanji.on_readings) > 0
        assert len(kanji.kun_readings) > 0
        assert kanji.jlpt_level in ["N5", "N4", "N3", "N2", "N1"]
        assert kanji.stroke_count > 0
        assert kanji.grade is not None

    @pytest.mark.asyncio
    async def test_imported_vocabulary_has_required_fields(self, db_session: AsyncSession):
        """Test that imported vocabulary has all required fields."""
        from scripts.generate_sample_data import import_sample_data_to_db

        # Act
        await import_sample_data_to_db(db_session)

        # Assert - Get a sample vocabulary
        result = await db_session.execute(
            select(Vocabulary).limit(1)
        )
        vocab = result.scalar_one_or_none()

        assert vocab is not None
        assert vocab.word
        assert vocab.reading
        assert len(vocab.meanings) > 0
        assert vocab.part_of_speech
        assert vocab.jlpt_level in ["N5", "N4", "N3", "N2", "N1"]

    @pytest.mark.asyncio
    async def test_imported_data_is_valid_japanese(self, db_session: AsyncSession):
        """Test that imported Japanese text is valid UTF-8."""
        from scripts.generate_sample_data import import_sample_data_to_db

        # Act
        await import_sample_data_to_db(db_session)

        # Assert - Check kanji
        result = await db_session.execute(select(Kanji).limit(5))
        kanji_list = result.scalars().all()

        for kanji in kanji_list:
            # Should be valid single Japanese character
            assert len(kanji.character) == 1
            # Should be in Unicode CJK range
            char_code = ord(kanji.character)
            assert char_code >= 0x4E00  # Start of CJK Unified Ideographs

        # Assert - Check vocabulary
        result = await db_session.execute(select(Vocabulary).limit(5))
        vocab_list = result.scalars().all()

        for vocab in vocab_list:
            # Should contain valid Japanese characters
            assert vocab.word
            assert vocab.reading
            # Reading should be hiragana/katakana
            # (This is a simplified check)
            assert len(vocab.reading) > 0
