"""
Content utilities for parsing and importing Japanese dictionary data.

Supports JMDict and KANJIDIC2 XML formats.
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vocabulary import Vocabulary
from app.models.kanji import Kanji


# Part of Speech mapping for JMDict
POS_MAPPING = {
    "&n;": "noun",
    "&v1;": "ichidan verb",
    "&v5;": "godan verb",
    "&adj-i;": "i-adjective",
    "&adj-na;": "na-adjective",
    "&adv;": "adverb",
    "&pn;": "pronoun",
    "&conj;": "conjunction",
    "&int;": "interjection",
    "&aux;": "auxiliary",
    "&prt;": "particle",
}


def parse_jmdict_entry(entry: ET.Element) -> Optional[Dict[str, Any]]:
    """
    Parse a single JMDict entry from XML.

    Args:
        entry: XML element representing a JMDict entry

    Returns:
        Dictionary with vocabulary data or None if invalid
    """
    try:
        # Extract kanji form (or use kana if no kanji)
        kanji_element = entry.find("k_ele/keb")
        kana_element = entry.find("r_ele/reb")

        if kanji_element is not None:
            word = kanji_element.text
        elif kana_element is not None:
            word = kana_element.text
        else:
            return None

        # Extract reading (kana)
        reading = kana_element.text if kana_element is not None else word

        # Extract meanings and part of speech from sense element
        sense = entry.find("sense")
        if sense is None:
            return None

        meanings = extract_meanings(sense)
        if not meanings:
            return None

        # Extract part of speech
        pos_element = sense.find("pos")
        part_of_speech = "noun"  # Default
        if pos_element is not None:
            pos_text = pos_element.text
            if pos_text in POS_MAPPING:
                part_of_speech = POS_MAPPING[pos_text]
            elif pos_text:
                # Use the value directly if it's already a string
                part_of_speech = pos_text

        return {
            "word": word,
            "reading": reading,
            "meanings": meanings,
            "part_of_speech": part_of_speech,
        }

    except Exception as e:
        # Log error but don't crash
        print(f"Error parsing JMDict entry: {e}")
        return None


def parse_kanjidic_entry(entry: ET.Element) -> Optional[Dict[str, Any]]:
    """
    Parse a single KANJIDIC2 entry from XML.

    Args:
        entry: XML element representing a KANJIDIC2 character entry

    Returns:
        Dictionary with kanji data or None if invalid
    """
    try:
        # Extract character
        literal = entry.find("literal")
        if literal is None or not literal.text:
            return None

        character = literal.text

        # Extract misc data (grade, stroke count, frequency)
        misc = entry.find("misc")
        grade = None
        stroke_count = None
        frequency_rank = None
        jlpt = None

        if misc is not None:
            grade_elem = misc.find("grade")
            if grade_elem is not None and grade_elem.text:
                grade = int(grade_elem.text)

            stroke_elem = misc.find("stroke_count")
            if stroke_elem is not None and stroke_elem.text:
                stroke_count = int(stroke_elem.text)

            freq_elem = misc.find("freq")
            if freq_elem is not None and freq_elem.text:
                frequency_rank = int(freq_elem.text)

            jlpt_elem = misc.find("jlpt")
            if jlpt_elem is not None and jlpt_elem.text:
                jlpt = int(jlpt_elem.text)

        # Extract readings and meanings
        reading_meaning = entry.find("reading_meaning")
        if reading_meaning is None:
            return None

        on_readings = extract_on_readings(reading_meaning)
        kun_readings = extract_kun_readings(reading_meaning)

        # Extract meanings
        meanings = []
        rmgroup = reading_meaning.find("rmgroup")
        if rmgroup is not None:
            for meaning in rmgroup.findall("meaning"):
                # Only get English meanings (no xml:lang attribute or lang="en")
                lang = meaning.get("{http://www.w3.org/XML/1998/namespace}lang")
                if lang is None or lang == "en":
                    if meaning.text:
                        meanings.append(meaning.text)

        if not meanings:
            return None

        return {
            "character": character,
            "meanings": meanings,
            "on_readings": on_readings,
            "kun_readings": kun_readings,
            "grade": grade,
            "stroke_count": stroke_count,
            "frequency_rank": frequency_rank,
            "jlpt_old": jlpt,  # Old JLPT numbering (4=N5, 3=N4, etc.)
        }

    except Exception as e:
        print(f"Error parsing KANJIDIC entry: {e}")
        return None


def determine_jlpt_level(data: Dict[str, Any], content_type: str = "vocabulary") -> str:
    """
    Determine JLPT level based on available data.

    Args:
        data: Dictionary with frequency, grade, or other markers
        content_type: "vocabulary" or "kanji"

    Returns:
        JLPT level string (N5, N4, N3, N2, N1)
    """
    if content_type == "kanji":
        # Use grade for kanji
        grade = data.get("grade")
        if grade == 1:
            return "N5"
        elif grade == 2:
            return "N4"
        elif grade in [3, 4]:
            return "N3"
        elif grade in [5, 6]:
            return "N2"

        # Use frequency rank
        freq = data.get("frequency_rank")
        if freq and freq <= 100:
            return "N5"
        elif freq and freq <= 500:
            return "N4"
        elif freq and freq <= 1500:
            return "N3"

    else:  # vocabulary
        # Use frequency rank for vocabulary
        freq = data.get("frequency_rank")
        if freq and freq <= 500:
            return "N5"
        elif freq and freq <= 1500:
            return "N4"
        elif freq and freq <= 3000:
            return "N3"

    # Default to N3
    return "N3"


def extract_meanings(sense: ET.Element) -> List[str]:
    """
    Extract English meanings from JMDict sense element.

    Args:
        sense: XML sense element

    Returns:
        List of meaning strings
    """
    meanings = []
    for gloss in sense.findall("gloss"):
        if gloss.text:
            meanings.append(gloss.text)
    return meanings


def extract_on_readings(reading_meaning: ET.Element) -> List[str]:
    """
    Extract on-yomi readings from KANJIDIC2 reading_meaning element.

    Args:
        reading_meaning: XML reading_meaning element

    Returns:
        List of on-yomi reading strings
    """
    readings = []
    rmgroup = reading_meaning.find("rmgroup")
    if rmgroup is not None:
        for reading in rmgroup.findall("reading"):
            if reading.get("r_type") == "ja_on" and reading.text:
                readings.append(reading.text)
    return readings


def extract_kun_readings(reading_meaning: ET.Element) -> List[str]:
    """
    Extract kun-yomi readings from KANJIDIC2 reading_meaning element.

    Args:
        reading_meaning: XML reading_meaning element

    Returns:
        List of kun-yomi reading strings
    """
    readings = []
    rmgroup = reading_meaning.find("rmgroup")
    if rmgroup is not None:
        for reading in rmgroup.findall("reading"):
            if reading.get("r_type") == "ja_kun" and reading.text:
                readings.append(reading.text)
    return readings


async def upsert_vocabulary(
    session: AsyncSession,
    vocab_data: Dict[str, Any]
) -> Vocabulary:
    """
    Insert or update vocabulary entry in database.

    Args:
        session: Database session
        vocab_data: Dictionary with vocabulary data

    Returns:
        Vocabulary model instance
    """
    # Check if vocabulary already exists
    result = await session.execute(
        select(Vocabulary).where(
            Vocabulary.word == vocab_data["word"],
            Vocabulary.reading == vocab_data["reading"]
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        # Update existing entry
        for key, value in vocab_data.items():
            if hasattr(existing, key):
                setattr(existing, key, value)
        await session.commit()
        await session.refresh(existing)
        return existing
    else:
        # Create new entry
        vocab = Vocabulary(**vocab_data)
        session.add(vocab)
        await session.commit()
        await session.refresh(vocab)
        return vocab


async def upsert_kanji(
    session: AsyncSession,
    kanji_data: Dict[str, Any]
) -> Kanji:
    """
    Insert or update kanji entry in database.

    Args:
        session: Database session
        kanji_data: Dictionary with kanji data

    Returns:
        Kanji model instance
    """
    # Check if kanji already exists
    result = await session.execute(
        select(Kanji).where(Kanji.character == kanji_data["character"])
    )
    existing = result.scalar_one_or_none()

    if existing:
        # Update existing entry
        for key, value in kanji_data.items():
            if hasattr(existing, key):
                setattr(existing, key, value)
        await session.commit()
        await session.refresh(existing)
        return existing
    else:
        # Create new entry
        kanji = Kanji(**kanji_data)
        session.add(kanji)
        await session.commit()
        await session.refresh(kanji)
        return kanji
