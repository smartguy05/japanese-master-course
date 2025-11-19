"""
AI prompts for content generation.

These prompts are used with Claude to generate lesson content,
example sentences, and grammar explanations.
"""

# =============================================================================
# Lesson Generation Prompts
# =============================================================================

LESSON_GENERATION_PROMPT = """
Generate a complete {lesson_type} lesson for JLPT {jlpt_level} level.

Lesson Topic: {topic}

Requirements:
1. Title: Clear and descriptive
2. Learning Objectives: 3-5 specific, measurable goals
3. Content Structure:
   - Introduction (context and motivation)
   - Core Teaching (explanations with examples)
   - Practice Exercises (5-10 interactive exercises)
   - Summary (key takeaways)
4. Estimated Duration: Realistic time estimate in minutes
5. Prerequisites: Required prior knowledge (lesson IDs or concepts)

Focus Areas for {jlpt_level}:
{level_specific_guidance}

Output Format (JSON):
{{
  "title": "Lesson title in English",
  "title_ja": "レッスンタイトル",
  "objectives": ["objective 1", "objective 2", ...],
  "introduction": {{
    "text": "Introduction text in English",
    "text_ja": "日本語の紹介"
  }},
  "content": [
    {{
      "type": "explanation|example|note",
      "text": "Content in English",
      "text_ja": "日本語のコンテンツ",
      "audio_text": "Text for TTS generation"
    }}
  ],
  "exercises": [
    {{
      "id": "ex1",
      "type": "multiple_choice|fill_blank|translation|matching",
      "question": "Question text",
      "question_ja": "質問",
      "options": ["option1", "option2", ...],
      "correct_answer": "correct answer",
      "explanation": "Why this is correct and what makes other options wrong"
    }}
  ],
  "summary": "Key takeaways and next steps",
  "estimated_minutes": 20
}}

Generate comprehensive, pedagogically sound content that builds on previous lessons.
Include furigana for kanji where appropriate for the JLPT level.
Ensure exercises test both recognition and production skills.
"""

# Level-specific guidance
JLPT_LEVEL_GUIDANCE = {
    "N5": """
- Focus on basic grammar patterns and everyday vocabulary
- Use simple sentence structures
- Include romaji for absolute beginners where appropriate
- Emphasize practical, daily conversation scenarios
- Keep explanations simple and clear
- Use lots of visual examples
""",
    "N4": """
- Introduce more complex grammar patterns
- Mix polite and casual forms
- Include compound sentences
- Focus on common situations (shopping, travel, work basics)
- Start reducing romaji usage
- Build on N5 foundation
""",
    "N3": """
- Complex grammar structures and nuances
- Business and formal contexts
- Idiomatic expressions
- Reading comprehension of longer texts
- No romaji - learners should be comfortable with kana
- Cultural context becomes important
""",
    "N2": """
- Advanced grammar and subtle distinctions
- Professional communication
- News articles and formal writing
- Keigo (honorific language)
- Technical and academic vocabulary
- Cultural and social nuances
""",
    "N1": """
- Native-level expressions and idioms
- Academic and specialized topics
- Literature and classical forms
- Regional dialects awareness
- Advanced keigo and formal registers
- Cultural and historical references
""",
}


HIRAGANA_LESSON_PROMPT = """
Generate a hiragana lesson for the {row} row ({characters}).

Include:
1. Character introduction with stroke order notes
2. Pronunciation guide (English approximation)
3. Mnemonic devices to remember each character
4. Common words using these characters
5. Writing practice exercises
6. Reading practice exercises

Output as JSON following the lesson generation format.
Make it engaging and memorable for complete beginners.
"""


KATAKANA_LESSON_PROMPT = """
Generate a katakana lesson for the {row} row ({characters}).

Include:
1. Character introduction with stroke order notes
2. Pronunciation guide (same as hiragana counterparts)
3. Comparison with hiragana equivalents
4. Common loanwords using these characters
5. Writing practice exercises
6. Reading practice exercises (focusing on loanwords)

Output as JSON following the lesson generation format.
Emphasize the use of katakana for foreign words and names.
"""


KANJI_LESSON_PROMPT = """
Generate a kanji lesson for: {kanji}

Include:
1. Character overview (meaning, common readings)
2. Stroke order and writing tips
3. On-yomi (Chinese reading) and Kun-yomi (Japanese reading)
4. Radicals and components
5. Common compound words using this kanji
6. Example sentences with furigana
7. Practice exercises (reading, writing, vocabulary)

Output as JSON following the lesson generation format.
Include mnemonic devices to aid memorization.
JLPT Level: {jlpt_level}
"""


VOCABULARY_LESSON_PROMPT = """
Generate a vocabulary lesson with the theme: {theme}

Include {word_count} vocabulary words appropriate for JLPT {jlpt_level}.

For each word:
1. Japanese word (kanji/kana)
2. Reading (hiragana)
3. English meaning
4. Part of speech
5. Example sentence
6. Usage notes (formal/informal, common contexts)

Create exercises testing:
- Recognition (Japanese to English)
- Production (English to Japanese)
- Usage in context
- Collocations and common phrases

Output as JSON following the lesson generation format.
"""


GRAMMAR_LESSON_PROMPT = """
Generate a grammar lesson for the pattern: {grammar_pattern}

Structure:
1. Pattern Definition
   - Japanese: {grammar_pattern}
   - Meaning: Clear explanation
   - Formation: How to construct it
   - Function: What it expresses

2. Usage Rules
   - When to use (contexts, situations)
   - When NOT to use (common mistakes)
   - Formality level (casual/polite/formal)
   - Register considerations

3. Examples (7-10 progressive examples)
   - Simple examples first
   - Then more complex usage
   - Both affirmative and negative forms
   - Questions using the pattern

4. Common Mistakes
   - What learners often get wrong
   - How to avoid these mistakes

5. Practice Exercises
   - Fill in the blank
   - Sentence transformation
   - Translation (both directions)
   - Error correction

6. Related Patterns
   - Similar grammar points
   - How they differ
   - When to use each

Output as JSON following the lesson generation format.
JLPT Level: {jlpt_level}
"""


# =============================================================================
# Example Sentence Generation
# =============================================================================

EXAMPLE_SENTENCE_GENERATION_PROMPT = """
Generate {count} example sentences demonstrating the usage of: {target_word}

Requirements:
1. Natural, conversational Japanese
2. Appropriate for {jlpt_level} learners
3. Diverse contexts (daily life, work, social situations)
4. Progressive difficulty (simple → complex)
5. Include translations and notes

Output Format (JSON):
{{
  "sentences": [
    {{
      "japanese": "Example sentence in Japanese",
      "reading": "ふりがな付きの文",
      "romaji": "Romaji version (for N5 only)",
      "translation": "English translation",
      "context": "Brief context note (when/where to use this)",
      "grammar_notes": "Key grammar points demonstrated",
      "audio_text": "Sentence for TTS"
    }}
  ]
}}

Focus on practical, real-world usage that helps learners understand when and how to use this word.
Vary the sentence patterns and grammatical contexts.
"""


# =============================================================================
# Conversation Scenario Generation
# =============================================================================

CONVERSATION_SCENARIO_PROMPT = """
Generate a conversation scenario for: {scenario_type}

Settings: {setting_description}
Participants: {participants}
JLPT Level: {jlpt_level}

Create a realistic, natural conversation that:
1. Uses appropriate politeness levels
2. Demonstrates common phrases and expressions
3. Includes cultural context notes
4. Has 6-12 exchanges
5. Is useful for real-life situations

Output Format (JSON):
{{
  "title": "Scenario title",
  "title_ja": "シナリオのタイトル",
  "setting": "Description of the setting",
  "participants": ["Person A", "Person B"],
  "exchanges": [
    {{
      "speaker": "Person A",
      "japanese": "Japanese text",
      "reading": "Furigana reading",
      "translation": "English translation",
      "notes": "Cultural or usage notes"
    }}
  ],
  "key_phrases": ["phrase 1", "phrase 2"],
  "cultural_notes": "Important cultural context",
  "practice_prompts": ["Practice prompt 1", "Practice prompt 2"]
}}

Make it engaging and memorable!
"""


# =============================================================================
# Helper Functions
# =============================================================================


def get_level_guidance(jlpt_level: str) -> str:
    """Get JLPT level-specific guidance."""
    return JLPT_LEVEL_GUIDANCE.get(jlpt_level, JLPT_LEVEL_GUIDANCE["N5"])


def format_lesson_prompt(
    lesson_type: str, jlpt_level: str, topic: str, **kwargs
) -> str:
    """
    Format a lesson generation prompt with specific parameters.

    Args:
        lesson_type: Type of lesson (hiragana, katakana, kanji, vocabulary, grammar)
        jlpt_level: JLPT level (N5-N1)
        topic: Main topic or focus of the lesson
        **kwargs: Additional parameters for the prompt

    Returns:
        Formatted prompt string
    """
    level_guidance = get_level_guidance(jlpt_level)

    return LESSON_GENERATION_PROMPT.format(
        lesson_type=lesson_type,
        jlpt_level=jlpt_level,
        topic=topic,
        level_specific_guidance=level_guidance,
        **kwargs,
    )


def format_hiragana_prompt(row: str, characters: str) -> str:
    """Format hiragana lesson prompt."""
    return HIRAGANA_LESSON_PROMPT.format(row=row, characters=characters)


def format_katakana_prompt(row: str, characters: str) -> str:
    """Format katakana lesson prompt."""
    return KATAKANA_LESSON_PROMPT.format(row=row, characters=characters)


def format_kanji_prompt(kanji: str, jlpt_level: str) -> str:
    """Format kanji lesson prompt."""
    return KANJI_LESSON_PROMPT.format(kanji=kanji, jlpt_level=jlpt_level)


def format_vocabulary_prompt(theme: str, word_count: int, jlpt_level: str) -> str:
    """Format vocabulary lesson prompt."""
    return VOCABULARY_LESSON_PROMPT.format(
        theme=theme, word_count=word_count, jlpt_level=jlpt_level
    )


def format_grammar_prompt(grammar_pattern: str, jlpt_level: str) -> str:
    """Format grammar lesson prompt."""
    return GRAMMAR_LESSON_PROMPT.format(
        grammar_pattern=grammar_pattern, jlpt_level=jlpt_level
    )
