#!/usr/bin/env python3
"""
Generate sample Japanese learning data for testing and development.

Creates N5-level kanji, vocabulary, and lessons without requiring
external dictionary downloads.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.utils.content_utils import upsert_kanji, upsert_vocabulary


def generate_n5_kanji() -> List[Dict]:
    """
    Generate N5 level kanji data.

    Returns:
        List of dictionaries with kanji data
    """
    n5_kanji = [
        {
            "character": "日",
            "meanings": ["day", "sun", "Japan"],
            "on_readings": ["ニチ", "ジツ"],
            "kun_readings": ["ひ", "か"],
            "jlpt_level": "N5",
            "grade": 1,
            "stroke_count": 4,
            "frequency_rank": 1,
            "radical": "日",
            "examples": [
                {"word": "日本", "reading": "にほん", "meaning": "Japan"},
                {"word": "毎日", "reading": "まいにち", "meaning": "every day"}
            ]
        },
        {
            "character": "月",
            "meanings": ["month", "moon"],
            "on_readings": ["ゲツ", "ガツ"],
            "kun_readings": ["つき"],
            "jlpt_level": "N5",
            "grade": 1,
            "stroke_count": 4,
            "frequency_rank": 18,
            "radical": "月",
            "examples": [
                {"word": "月曜日", "reading": "げつようび", "meaning": "Monday"},
                {"word": "一月", "reading": "いちがつ", "meaning": "January"}
            ]
        },
        {
            "character": "火",
            "meanings": ["fire"],
            "on_readings": ["カ"],
            "kun_readings": ["ひ"],
            "jlpt_level": "N5",
            "grade": 1,
            "stroke_count": 4,
            "frequency_rank": 560,
            "radical": "火",
            "examples": [
                {"word": "火曜日", "reading": "かようび", "meaning": "Tuesday"}
            ]
        },
        {
            "character": "水",
            "meanings": ["water"],
            "on_readings": ["スイ"],
            "kun_readings": ["みず"],
            "jlpt_level": "N5",
            "grade": 1,
            "stroke_count": 4,
            "frequency_rank": 365,
            "radical": "水",
            "examples": [
                {"word": "水曜日", "reading": "すいようび", "meaning": "Wednesday"},
                {"word": "水", "reading": "みず", "meaning": "water"}
            ]
        },
        {
            "character": "木",
            "meanings": ["tree", "wood"],
            "on_readings": ["モク", "ボク"],
            "kun_readings": ["き"],
            "jlpt_level": "N5",
            "grade": 1,
            "stroke_count": 4,
            "frequency_rank": 418,
            "radical": "木",
            "examples": [
                {"word": "木曜日", "reading": "もくようび", "meaning": "Thursday"},
                {"word": "木", "reading": "き", "meaning": "tree"}
            ]
        },
        {
            "character": "金",
            "meanings": ["gold", "money", "metal"],
            "on_readings": ["キン", "コン"],
            "kun_readings": ["かね", "かな"],
            "jlpt_level": "N5",
            "grade": 1,
            "stroke_count": 8,
            "frequency_rank": 91,
            "radical": "金",
            "examples": [
                {"word": "金曜日", "reading": "きんようび", "meaning": "Friday"},
                {"word": "お金", "reading": "おかね", "meaning": "money"}
            ]
        },
        {
            "character": "土",
            "meanings": ["soil", "earth", "ground"],
            "on_readings": ["ド", "ト"],
            "kun_readings": ["つち"],
            "jlpt_level": "N5",
            "grade": 1,
            "stroke_count": 3,
            "frequency_rank": 348,
            "radical": "土",
            "examples": [
                {"word": "土曜日", "reading": "どようび", "meaning": "Saturday"}
            ]
        },
        {
            "character": "人",
            "meanings": ["person", "people"],
            "on_readings": ["ジン", "ニン"],
            "kun_readings": ["ひと"],
            "jlpt_level": "N5",
            "grade": 1,
            "stroke_count": 2,
            "frequency_rank": 5,
            "radical": "人",
            "examples": [
                {"word": "日本人", "reading": "にほんじん", "meaning": "Japanese person"},
                {"word": "人", "reading": "ひと", "meaning": "person"}
            ]
        },
        {
            "character": "本",
            "meanings": ["book", "origin", "main"],
            "on_readings": ["ホン"],
            "kun_readings": ["もと"],
            "jlpt_level": "N5",
            "grade": 1,
            "stroke_count": 5,
            "frequency_rank": 10,
            "radical": "木",
            "examples": [
                {"word": "日本", "reading": "にほん", "meaning": "Japan"},
                {"word": "本", "reading": "ほん", "meaning": "book"}
            ]
        },
        {
            "character": "一",
            "meanings": ["one"],
            "on_readings": ["イチ", "イツ"],
            "kun_readings": ["ひと"],
            "jlpt_level": "N5",
            "grade": 1,
            "stroke_count": 1,
            "frequency_rank": 2,
            "radical": "一",
            "examples": [
                {"word": "一人", "reading": "ひとり", "meaning": "one person"},
                {"word": "一月", "reading": "いちがつ", "meaning": "January"}
            ]
        },
        {
            "character": "二",
            "meanings": ["two"],
            "on_readings": ["ニ", "ジ"],
            "kun_readings": ["ふた"],
            "jlpt_level": "N5",
            "grade": 1,
            "stroke_count": 2,
            "frequency_rank": 9,
            "radical": "二",
            "examples": [
                {"word": "二人", "reading": "ふたり", "meaning": "two people"},
                {"word": "二月", "reading": "にがつ", "meaning": "February"}
            ]
        },
        {
            "character": "三",
            "meanings": ["three"],
            "on_readings": ["サン"],
            "kun_readings": ["み"],
            "jlpt_level": "N5",
            "grade": 1,
            "stroke_count": 3,
            "frequency_rank": 17,
            "radical": "一",
            "examples": [
                {"word": "三人", "reading": "さんにん", "meaning": "three people"},
                {"word": "三月", "reading": "さんがつ", "meaning": "March"}
            ]
        },
        {
            "character": "四",
            "meanings": ["four"],
            "on_readings": ["シ"],
            "kun_readings": ["よ", "よん"],
            "jlpt_level": "N5",
            "grade": 1,
            "stroke_count": 5,
            "frequency_rank": 53,
            "radical": "囗",
            "examples": [
                {"word": "四月", "reading": "しがつ", "meaning": "April"}
            ]
        },
        {
            "character": "五",
            "meanings": ["five"],
            "on_readings": ["ゴ"],
            "kun_readings": ["いつ"],
            "jlpt_level": "N5",
            "grade": 1,
            "stroke_count": 4,
            "frequency_rank": 69,
            "radical": "二",
            "examples": [
                {"word": "五月", "reading": "ごがつ", "meaning": "May"}
            ]
        },
        {
            "character": "六",
            "meanings": ["six"],
            "on_readings": ["ロク"],
            "kun_readings": ["む"],
            "jlpt_level": "N5",
            "grade": 1,
            "stroke_count": 4,
            "frequency_rank": 105,
            "radical": "八",
            "examples": [
                {"word": "六月", "reading": "ろくがつ", "meaning": "June"}
            ]
        },
        {
            "character": "七",
            "meanings": ["seven"],
            "on_readings": ["シチ"],
            "kun_readings": ["なな"],
            "jlpt_level": "N5",
            "grade": 1,
            "stroke_count": 2,
            "frequency_rank": 123,
            "radical": "一",
            "examples": [
                {"word": "七月", "reading": "しちがつ", "meaning": "July"}
            ]
        },
        {
            "character": "八",
            "meanings": ["eight"],
            "on_readings": ["ハチ"],
            "kun_readings": ["や"],
            "jlpt_level": "N5",
            "grade": 1,
            "stroke_count": 2,
            "frequency_rank": 131,
            "radical": "八",
            "examples": [
                {"word": "八月", "reading": "はちがつ", "meaning": "August"}
            ]
        },
        {
            "character": "九",
            "meanings": ["nine"],
            "on_readings": ["キュウ", "ク"],
            "kun_readings": ["ここの"],
            "jlpt_level": "N5",
            "grade": 1,
            "stroke_count": 2,
            "frequency_rank": 147,
            "radical": "乙",
            "examples": [
                {"word": "九月", "reading": "くがつ", "meaning": "September"}
            ]
        },
        {
            "character": "十",
            "meanings": ["ten"],
            "on_readings": ["ジュウ"],
            "kun_readings": ["とお"],
            "jlpt_level": "N5",
            "grade": 1,
            "stroke_count": 2,
            "frequency_rank": 16,
            "radical": "十",
            "examples": [
                {"word": "十月", "reading": "じゅうがつ", "meaning": "October"}
            ]
        },
        {
            "character": "百",
            "meanings": ["hundred"],
            "on_readings": ["ヒャク"],
            "kun_readings": ["もも"],
            "jlpt_level": "N5",
            "grade": 1,
            "stroke_count": 6,
            "frequency_rank": 74,
            "radical": "白",
            "examples": [
                {"word": "百", "reading": "ひゃく", "meaning": "hundred"}
            ]
        },
    ]

    return n5_kanji


def generate_n5_vocabulary() -> List[Dict]:
    """
    Generate N5 level vocabulary data.

    Returns:
        List of dictionaries with vocabulary data
    """
    n5_vocabulary = [
        # Pronouns
        {"word": "私", "reading": "わたし", "meanings": ["I", "me"], "part_of_speech": "pronoun", "jlpt_level": "N5", "frequency_rank": 8},
        {"word": "これ", "reading": "これ", "meanings": ["this"], "part_of_speech": "pronoun", "jlpt_level": "N5", "frequency_rank": 45},
        {"word": "それ", "reading": "それ", "meanings": ["that"], "part_of_speech": "pronoun", "jlpt_level": "N5", "frequency_rank": 23},
        {"word": "あれ", "reading": "あれ", "meanings": ["that over there"], "part_of_speech": "pronoun", "jlpt_level": "N5", "frequency_rank": 134},
        {"word": "どれ", "reading": "どれ", "meanings": ["which"], "part_of_speech": "pronoun", "jlpt_level": "N5", "frequency_rank": 167},

        # Basic nouns
        {"word": "日本", "reading": "にほん", "meanings": ["Japan"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 12},
        {"word": "人", "reading": "ひと", "meanings": ["person", "people"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 5},
        {"word": "学校", "reading": "がっこう", "meanings": ["school"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 89},
        {"word": "先生", "reading": "せんせい", "meanings": ["teacher"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 112},
        {"word": "学生", "reading": "がくせい", "meanings": ["student"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 156},

        # Time
        {"word": "今", "reading": "いま", "meanings": ["now"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 34},
        {"word": "今日", "reading": "きょう", "meanings": ["today"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 56},
        {"word": "明日", "reading": "あした", "meanings": ["tomorrow"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 234},
        {"word": "昨日", "reading": "きのう", "meanings": ["yesterday"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 345},
        {"word": "毎日", "reading": "まいにち", "meanings": ["every day"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 178},

        # Common verbs
        {"word": "食べる", "reading": "たべる", "meanings": ["to eat"], "part_of_speech": "ichidan verb", "jlpt_level": "N5", "frequency_rank": 267},
        {"word": "飲む", "reading": "のむ", "meanings": ["to drink"], "part_of_speech": "godan verb", "jlpt_level": "N5", "frequency_rank": 389},
        {"word": "行く", "reading": "いく", "meanings": ["to go"], "part_of_speech": "godan verb", "jlpt_level": "N5", "frequency_rank": 23},
        {"word": "来る", "reading": "くる", "meanings": ["to come"], "part_of_speech": "irregular verb", "jlpt_level": "N5", "frequency_rank": 45},
        {"word": "見る", "reading": "みる", "meanings": ["to see", "to look"], "part_of_speech": "ichidan verb", "jlpt_level": "N5", "frequency_rank": 12},
        {"word": "聞く", "reading": "きく", "meanings": ["to hear", "to listen", "to ask"], "part_of_speech": "godan verb", "jlpt_level": "N5", "frequency_rank": 89},
        {"word": "話す", "reading": "はなす", "meanings": ["to speak", "to talk"], "part_of_speech": "godan verb", "jlpt_level": "N5", "frequency_rank": 134},
        {"word": "読む", "reading": "よむ", "meanings": ["to read"], "part_of_speech": "godan verb", "jlpt_level": "N5", "frequency_rank": 178},
        {"word": "書く", "reading": "かく", "meanings": ["to write"], "part_of_speech": "godan verb", "jlpt_level": "N5", "frequency_rank": 201},
        {"word": "する", "reading": "する", "meanings": ["to do"], "part_of_speech": "irregular verb", "jlpt_level": "N5", "frequency_rank": 1},

        # Adjectives
        {"word": "大きい", "reading": "おおきい", "meanings": ["big", "large"], "part_of_speech": "i-adjective", "jlpt_level": "N5", "frequency_rank": 298},
        {"word": "小さい", "reading": "ちいさい", "meanings": ["small", "little"], "part_of_speech": "i-adjective", "jlpt_level": "N5", "frequency_rank": 312},
        {"word": "新しい", "reading": "あたらしい", "meanings": ["new"], "part_of_speech": "i-adjective", "jlpt_level": "N5", "frequency_rank": 245},
        {"word": "古い", "reading": "ふるい", "meanings": ["old"], "part_of_speech": "i-adjective", "jlpt_level": "N5", "frequency_rank": 367},
        {"word": "良い", "reading": "いい", "meanings": ["good"], "part_of_speech": "i-adjective", "jlpt_level": "N5", "frequency_rank": 67},
        {"word": "悪い", "reading": "わるい", "meanings": ["bad"], "part_of_speech": "i-adjective", "jlpt_level": "N5", "frequency_rank": 234},

        # Food
        {"word": "水", "reading": "みず", "meanings": ["water"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 365},
        {"word": "お茶", "reading": "おちゃ", "meanings": ["tea"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 456},
        {"word": "ご飯", "reading": "ごはん", "meanings": ["rice", "meal"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 389},
        {"word": "パン", "reading": "パン", "meanings": ["bread"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 478},

        # Places
        {"word": "家", "reading": "いえ", "meanings": ["house", "home"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 78},
        {"word": "駅", "reading": "えき", "meanings": ["station"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 234},
        {"word": "店", "reading": "みせ", "meanings": ["shop", "store"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 198},
        {"word": "病院", "reading": "びょういん", "meanings": ["hospital"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 267},

        # Numbers (continued from kanji)
        {"word": "千", "reading": "せん", "meanings": ["thousand"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 123},
        {"word": "万", "reading": "まん", "meanings": ["ten thousand"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 156},

        # Common phrases
        {"word": "はい", "reading": "はい", "meanings": ["yes"], "part_of_speech": "interjection", "jlpt_level": "N5", "frequency_rank": 45},
        {"word": "いいえ", "reading": "いいえ", "meanings": ["no"], "part_of_speech": "interjection", "jlpt_level": "N5", "frequency_rank": 89},
        {"word": "ありがとう", "reading": "ありがとう", "meanings": ["thank you"], "part_of_speech": "interjection", "jlpt_level": "N5", "frequency_rank": 234},
        {"word": "すみません", "reading": "すみません", "meanings": ["excuse me", "sorry"], "part_of_speech": "interjection", "jlpt_level": "N5", "frequency_rank": 178},
    ]

    # Add more to reach 100
    more_vocab = [
        {"word": "本", "reading": "ほん", "meanings": ["book"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 10},
        {"word": "机", "reading": "つくえ", "meanings": ["desk"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 456},
        {"word": "椅子", "reading": "いす", "meanings": ["chair"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 478},
        {"word": "ドア", "reading": "ドア", "meanings": ["door"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 489},
        {"word": "窓", "reading": "まど", "meanings": ["window"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 456},
        {"word": "猫", "reading": "ねこ", "meanings": ["cat"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 512},
        {"word": "犬", "reading": "いぬ", "meanings": ["dog"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 498},
        {"word": "魚", "reading": "さかな", "meanings": ["fish"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 445},
        {"word": "鳥", "reading": "とり", "meanings": ["bird"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 467},
        {"word": "花", "reading": "はな", "meanings": ["flower"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 423},
        {"word": "木", "reading": "き", "meanings": ["tree"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 418},
        {"word": "山", "reading": "やま", "meanings": ["mountain"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 234},
        {"word": "川", "reading": "かわ", "meanings": ["river"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 267},
        {"word": "海", "reading": "うみ", "meanings": ["sea", "ocean"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 298},
        {"word": "空", "reading": "そら", "meanings": ["sky"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 312},
        {"word": "雨", "reading": "あめ", "meanings": ["rain"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 345},
        {"word": "雪", "reading": "ゆき", "meanings": ["snow"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 378},
        {"word": "風", "reading": "かぜ", "meanings": ["wind"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 389},
        {"word": "天気", "reading": "てんき", "meanings": ["weather"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 401},
        {"word": "朝", "reading": "あさ", "meanings": ["morning"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 234},
        {"word": "昼", "reading": "ひる", "meanings": ["noon", "daytime"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 312},
        {"word": "夜", "reading": "よる", "meanings": ["night"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 267},
        {"word": "朝ご飯", "reading": "あさごはん", "meanings": ["breakfast"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 456},
        {"word": "昼ご飯", "reading": "ひるごはん", "meanings": ["lunch"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 478},
        {"word": "晩ご飯", "reading": "ばんごはん", "meanings": ["dinner"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 489},
        {"word": "時計", "reading": "とけい", "meanings": ["clock", "watch"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 445},
        {"word": "カメラ", "reading": "カメラ", "meanings": ["camera"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 512},
        {"word": "写真", "reading": "しゃしん", "meanings": ["photograph"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 298},
        {"word": "映画", "reading": "えいが", "meanings": ["movie"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 345},
        {"word": "音楽", "reading": "おんがく", "meanings": ["music"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 378},
        {"word": "スポーツ", "reading": "スポーツ", "meanings": ["sport"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 423},
        {"word": "テレビ", "reading": "テレビ", "meanings": ["television"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 389},
        {"word": "ラジオ", "reading": "ラジオ", "meanings": ["radio"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 456},
        {"word": "新聞", "reading": "しんぶん", "meanings": ["newspaper"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 312},
        {"word": "雑誌", "reading": "ざっし", "meanings": ["magazine"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 401},
        {"word": "手紙", "reading": "てがみ", "meanings": ["letter"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 445},
        {"word": "電話", "reading": "でんわ", "meanings": ["telephone"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 234},
        {"word": "名前", "reading": "なまえ", "meanings": ["name"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 156},
        {"word": "友達", "reading": "ともだち", "meanings": ["friend"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 234},
        {"word": "家族", "reading": "かぞく", "meanings": ["family"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 198},
        {"word": "父", "reading": "ちち", "meanings": ["father"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 267},
        {"word": "母", "reading": "はは", "meanings": ["mother"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 278},
        {"word": "兄", "reading": "あに", "meanings": ["older brother"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 334},
        {"word": "姉", "reading": "あね", "meanings": ["older sister"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 345},
        {"word": "弟", "reading": "おとうと", "meanings": ["younger brother"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 356},
        {"word": "妹", "reading": "いもうと", "meanings": ["younger sister"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 367},
        {"word": "子供", "reading": "こども", "meanings": ["child"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 198},
        {"word": "男", "reading": "おとこ", "meanings": ["man", "male"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 178},
        {"word": "女", "reading": "おんな", "meanings": ["woman", "female"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 189},
        {"word": "車", "reading": "くるま", "meanings": ["car"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 123},
        {"word": "自転車", "reading": "じてんしゃ", "meanings": ["bicycle"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 345},
        {"word": "バス", "reading": "バス", "meanings": ["bus"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 312},
        {"word": "電車", "reading": "でんしゃ", "meanings": ["train"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 234},
        {"word": "飛行機", "reading": "ひこうき", "meanings": ["airplane"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 389},
        {"word": "船", "reading": "ふね", "meanings": ["ship", "boat"], "part_of_speech": "noun", "jlpt_level": "N5", "frequency_rank": 401},
    ]

    n5_vocabulary.extend(more_vocab)
    return n5_vocabulary[:100]  # Return exactly 100


async def import_sample_data_to_db(session: AsyncSession) -> Dict[str, int]:
    """
    Import sample data into the database.

    Args:
        session: Database session

    Returns:
        Statistics dictionary with counts
    """
    kanji_list = generate_n5_kanji()
    vocab_list = generate_n5_vocabulary()

    kanji_count = 0
    vocab_count = 0

    # Import kanji
    for kanji_data in kanji_list:
        await upsert_kanji(session, kanji_data)
        kanji_count += 1

    # Import vocabulary
    for vocab_data in vocab_list:
        await upsert_vocabulary(session, vocab_data)
        vocab_count += 1

    return {
        "kanji_count": kanji_count,
        "vocabulary_count": vocab_count,
    }


def parse_args(args=None):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate sample Japanese learning data"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="sample_data.json",
        help="Output JSON file path (default: sample_data.json)",
    )
    parser.add_argument(
        "--import-db",
        action="store_true",
        help="Import data directly into database",
    )

    return parser.parse_args(args)


async def main_async():
    """Async main function."""
    args = parse_args()

    kanji_data = generate_n5_kanji()
    vocab_data = generate_n5_vocabulary()

    if args.import_db:
        # Import to database
        print("Importing sample data to database...")
        async with AsyncSessionLocal() as session:
            stats = await import_sample_data_to_db(session)
            print(f"✓ Imported {stats['kanji_count']} kanji")
            print(f"✓ Imported {stats['vocabulary_count']} vocabulary words")
    else:
        # Write to JSON file
        output_data = {
            "kanji": kanji_data,
            "vocabulary": vocab_data,
        }

        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"✓ Generated {len(kanji_data)} N5 kanji")
        print(f"✓ Generated {len(vocab_data)} N5 vocabulary words")
        print(f"✓ Saved to {args.output}")


def main():
    """Main entry point."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
