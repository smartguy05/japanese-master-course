"""
Unit tests for content utilities (JMDict and KANJIDIC2 parsing).

TDD PHASE: RED - These tests will fail until implementation is complete.
"""

import pytest
import xml.etree.ElementTree as ET
from unittest.mock import AsyncMock, MagicMock

from app.utils.content_utils import (
    parse_jmdict_entry,
    parse_kanjidic_entry,
    determine_jlpt_level,
    extract_meanings,
    extract_on_readings,
    extract_kun_readings,
    upsert_vocabulary,
    upsert_kanji,
)


class TestJMDictParsing:
    """Test JMDict XML parsing functionality."""

    def test_parse_jmdict_entry_basic(self):
        """Test parsing basic JMDict entry with kanji and reading."""
        # Arrange - Sample JMDict entry XML (without entities)
        xml_text = """
        <entry>
            <k_ele>
                <keb>水</keb>
            </k_ele>
            <r_ele>
                <reb>みず</reb>
            </r_ele>
            <sense>
                <pos>noun</pos>
                <gloss>water</gloss>
            </sense>
        </entry>
        """
        entry = ET.fromstring(xml_text)

        # Act
        result = parse_jmdict_entry(entry)

        # Assert
        assert result is not None
        assert result["word"] == "水"
        assert result["reading"] == "みず"
        assert "water" in result["meanings"]
        assert result["part_of_speech"] == "noun"

    def test_parse_jmdict_entry_multiple_meanings(self):
        """Test parsing entry with multiple English meanings."""
        # Arrange
        xml_text = """
        <entry>
            <k_ele>
                <keb>本</keb>
            </k_ele>
            <r_ele>
                <reb>ほん</reb>
            </r_ele>
            <sense>
                <pos>noun</pos>
                <gloss>book</gloss>
                <gloss>volume</gloss>
                <gloss>main</gloss>
            </sense>
        </entry>
        """
        entry = ET.fromstring(xml_text)

        # Act
        result = parse_jmdict_entry(entry)

        # Assert
        assert len(result["meanings"]) == 3
        assert "book" in result["meanings"]
        assert "volume" in result["meanings"]
        assert "main" in result["meanings"]

    def test_parse_jmdict_entry_with_example_sentences(self):
        """Test parsing entry with example sentences."""
        # Arrange
        xml_text = """
        <entry>
            <k_ele>
                <keb>学校</keb>
            </k_ele>
            <r_ele>
                <reb>がっこう</reb>
            </r_ele>
            <sense>
                <pos>noun</pos>
                <gloss>school</gloss>
                <s_inf>Example: 学校に行く - go to school</s_inf>
            </sense>
        </entry>
        """
        entry = ET.fromstring(xml_text)

        # Act
        result = parse_jmdict_entry(entry)

        # Assert
        assert result["word"] == "学校"
        assert result["reading"] == "がっこう"
        assert "school" in result["meanings"]
        # Example sentences might be in separate field

    def test_parse_jmdict_entry_kana_only(self):
        """Test parsing entry with only kana (no kanji)."""
        # Arrange
        xml_text = """
        <entry>
            <r_ele>
                <reb>これ</reb>
            </r_ele>
            <sense>
                <pos>pronoun</pos>
                <gloss>this</gloss>
            </sense>
        </entry>
        """
        entry = ET.fromstring(xml_text)

        # Act
        result = parse_jmdict_entry(entry)

        # Assert
        assert result["word"] == "これ"
        assert result["reading"] == "これ"
        assert "this" in result["meanings"]

    def test_parse_jmdict_entry_verb(self):
        """Test parsing verb entry with part of speech."""
        # Arrange
        xml_text = """
        <entry>
            <k_ele>
                <keb>食べる</keb>
            </k_ele>
            <r_ele>
                <reb>たべる</reb>
            </r_ele>
            <sense>
                <pos>ichidan verb</pos>
                <gloss>to eat</gloss>
            </sense>
        </entry>
        """
        entry = ET.fromstring(xml_text)

        # Act
        result = parse_jmdict_entry(entry)

        # Assert
        assert result["word"] == "食べる"
        assert result["reading"] == "たべる"
        assert result["part_of_speech"] in ["verb", "ichidan verb"]


class TestKANJIDIC2Parsing:
    """Test KANJIDIC2 XML parsing functionality."""

    def test_parse_kanjidic_entry_basic(self):
        """Test parsing basic KANJIDIC2 entry."""
        # Arrange - Sample KANJIDIC2 entry XML
        xml_text = """
        <character>
            <literal>水</literal>
            <misc>
                <grade>1</grade>
                <stroke_count>4</stroke_count>
                <jlpt>4</jlpt>
            </misc>
            <reading_meaning>
                <rmgroup>
                    <reading r_type="ja_on">スイ</reading>
                    <reading r_type="ja_kun">みず</reading>
                    <meaning>water</meaning>
                </rmgroup>
            </reading_meaning>
        </character>
        """
        entry = ET.fromstring(xml_text)

        # Act
        result = parse_kanjidic_entry(entry)

        # Assert
        assert result is not None
        assert result["character"] == "水"
        assert result["stroke_count"] == 4
        assert result["grade"] == 1
        assert "スイ" in result["on_readings"]
        assert "みず" in result["kun_readings"]
        assert "water" in result["meanings"]

    def test_parse_kanjidic_entry_multiple_readings(self):
        """Test parsing entry with multiple on/kun readings."""
        # Arrange
        xml_text = """
        <character>
            <literal>生</literal>
            <misc>
                <grade>1</grade>
                <stroke_count>5</stroke_count>
            </misc>
            <reading_meaning>
                <rmgroup>
                    <reading r_type="ja_on">セイ</reading>
                    <reading r_type="ja_on">ショウ</reading>
                    <reading r_type="ja_kun">い.きる</reading>
                    <reading r_type="ja_kun">う.まれる</reading>
                    <meaning>life</meaning>
                    <meaning>birth</meaning>
                    <meaning>live</meaning>
                </rmgroup>
            </reading_meaning>
        </character>
        """
        entry = ET.fromstring(xml_text)

        # Act
        result = parse_kanjidic_entry(entry)

        # Assert
        assert len(result["on_readings"]) >= 2
        assert "セイ" in result["on_readings"]
        assert "ショウ" in result["on_readings"]
        assert len(result["kun_readings"]) >= 2
        assert len(result["meanings"]) >= 3

    def test_parse_kanjidic_entry_with_frequency(self):
        """Test parsing entry with frequency rank."""
        # Arrange
        xml_text = """
        <character>
            <literal>日</literal>
            <misc>
                <grade>1</grade>
                <stroke_count>4</stroke_count>
                <freq>1</freq>
            </misc>
            <reading_meaning>
                <rmgroup>
                    <reading r_type="ja_on">ニチ</reading>
                    <reading r_type="ja_kun">ひ</reading>
                    <meaning>day</meaning>
                    <meaning>sun</meaning>
                </rmgroup>
            </reading_meaning>
        </character>
        """
        entry = ET.fromstring(xml_text)

        # Act
        result = parse_kanjidic_entry(entry)

        # Assert
        assert result["character"] == "日"
        assert result["frequency_rank"] == 1


class TestJLPTLevelDetermination:
    """Test JLPT level determination logic."""

    def test_determine_jlpt_from_grade_1(self):
        """Test that grade 1 kanji maps to N5."""
        # Arrange
        kanji_data = {"grade": 1, "frequency_rank": 100}

        # Act
        result = determine_jlpt_level(kanji_data, content_type="kanji")

        # Assert
        assert result == "N5"

    def test_determine_jlpt_from_grade_2(self):
        """Test that grade 2 kanji maps to N4."""
        # Arrange
        kanji_data = {"grade": 2, "frequency_rank": 200}

        # Act
        result = determine_jlpt_level(kanji_data, content_type="kanji")

        # Assert
        assert result == "N4"

    def test_determine_jlpt_from_frequency_high(self):
        """Test that high frequency words map to N5."""
        # Arrange
        vocab_data = {"frequency_rank": 50}

        # Act
        result = determine_jlpt_level(vocab_data, content_type="vocabulary")

        # Assert
        assert result == "N5"

    def test_determine_jlpt_from_frequency_medium(self):
        """Test that medium frequency words map to N4."""
        # Arrange
        vocab_data = {"frequency_rank": 1500}

        # Act
        result = determine_jlpt_level(vocab_data, content_type="vocabulary")

        # Assert
        assert result == "N4"

    def test_determine_jlpt_default_n3(self):
        """Test default JLPT level when no markers available."""
        # Arrange
        data = {}

        # Act
        result = determine_jlpt_level(data, content_type="vocabulary")

        # Assert
        assert result == "N3"


class TestHelperFunctions:
    """Test helper parsing functions."""

    def test_extract_meanings_single(self):
        """Test extracting single meaning from sense element."""
        # Arrange
        xml_text = """
        <sense>
            <gloss>water</gloss>
        </sense>
        """
        sense = ET.fromstring(xml_text)

        # Act
        result = extract_meanings(sense)

        # Assert
        assert len(result) == 1
        assert "water" in result

    def test_extract_meanings_multiple(self):
        """Test extracting multiple meanings."""
        # Arrange
        xml_text = """
        <sense>
            <gloss>book</gloss>
            <gloss>volume</gloss>
            <gloss>counter for books</gloss>
        </sense>
        """
        sense = ET.fromstring(xml_text)

        # Act
        result = extract_meanings(sense)

        # Assert
        assert len(result) == 3
        assert all(m in result for m in ["book", "volume", "counter for books"])

    def test_extract_on_readings(self):
        """Test extracting on-yomi readings."""
        # Arrange
        xml_text = """
        <reading_meaning>
            <rmgroup>
                <reading r_type="ja_on">スイ</reading>
                <reading r_type="ja_on">ソウ</reading>
                <reading r_type="ja_kun">みず</reading>
            </rmgroup>
        </reading_meaning>
        """
        rm_group = ET.fromstring(xml_text)

        # Act
        result = extract_on_readings(rm_group)

        # Assert
        assert len(result) == 2
        assert "スイ" in result
        assert "ソウ" in result
        assert "みず" not in result  # Should not include kun readings

    def test_extract_kun_readings(self):
        """Test extracting kun-yomi readings."""
        # Arrange
        xml_text = """
        <reading_meaning>
            <rmgroup>
                <reading r_type="ja_on">スイ</reading>
                <reading r_type="ja_kun">みず</reading>
                <reading r_type="ja_kun">み</reading>
            </rmgroup>
        </reading_meaning>
        """
        rm_group = ET.fromstring(xml_text)

        # Act
        result = extract_kun_readings(rm_group)

        # Assert
        assert len(result) == 2
        assert "みず" in result
        assert "み" in result
        assert "スイ" not in result  # Should not include on readings


class TestDatabaseUpsert:
    """Test database upsert operations."""

    @pytest.mark.asyncio
    async def test_upsert_vocabulary_new_entry(self):
        """Test inserting new vocabulary entry."""
        # Arrange
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Mock commit and refresh as async
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        vocab_data = {
            "word": "水",
            "reading": "みず",
            "meanings": ["water"],
            "part_of_speech": "noun",
            "jlpt_level": "N5",
        }

        # Act
        result = await upsert_vocabulary(mock_session, vocab_data)

        # Assert
        assert result is not None
        # The function should add a new entry
        assert mock_session.add.called
        assert mock_session.commit.called

    @pytest.mark.asyncio
    async def test_upsert_vocabulary_duplicate_update(self):
        """Test updating existing vocabulary entry."""
        # Arrange
        mock_session = AsyncMock()
        existing_vocab = MagicMock()
        existing_vocab.word = "水"
        existing_vocab.meanings = ["water"]
        mock_session.execute.return_value.scalar_one_or_none.return_value = existing_vocab

        vocab_data = {
            "word": "水",
            "reading": "みず",
            "meanings": ["water", "cold water"],
            "part_of_speech": "noun",
            "jlpt_level": "N5",
        }

        # Act
        result = await upsert_vocabulary(mock_session, vocab_data)

        # Assert
        assert result is not None
        # Should update, not add new
        mock_session.add.assert_not_called()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_upsert_kanji_new_entry(self):
        """Test inserting new kanji entry."""
        # Arrange
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Mock commit and refresh as async
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        kanji_data = {
            "character": "水",
            "meanings": ["water"],
            "on_readings": ["スイ"],
            "kun_readings": ["みず"],
            "jlpt_level": "N5",
            "grade": 1,
            "stroke_count": 4,
        }

        # Act
        result = await upsert_kanji(mock_session, kanji_data)

        # Assert
        assert result is not None
        # The function should add a new entry
        assert mock_session.add.called
        assert mock_session.commit.called

    @pytest.mark.asyncio
    async def test_upsert_kanji_duplicate_skip(self):
        """Test that duplicate kanji entries are handled correctly."""
        # Arrange
        mock_session = AsyncMock()
        existing_kanji = MagicMock()
        existing_kanji.character = "水"
        mock_session.execute.return_value.scalar_one_or_none.return_value = existing_kanji

        kanji_data = {
            "character": "水",
            "meanings": ["water"],
            "on_readings": ["スイ"],
            "kun_readings": ["みず"],
            "jlpt_level": "N5",
            "grade": 1,
            "stroke_count": 4,
        }

        # Act
        result = await upsert_kanji(mock_session, kanji_data)

        # Assert
        # Should update existing entry
        mock_session.commit.assert_called_once()
