"""
Conversation prompts for AI-powered Japanese conversation practice.

All prompts follow a structured format to ensure consistent, parseable responses.
"""

from typing import Optional

# Scenario-specific system instructions
SCENARIO_CONTEXTS = {
    "general": """
You're having a casual conversation in Japanese. Topics can include daily life,
hobbies, weather, family, or any general topics appropriate for the student's level.
Keep the conversation natural and flowing.
""",
    "restaurant": """
You're a staff member at a Japanese restaurant. The student is a customer trying to
order food, ask about menu items, or handle the bill. Be polite and helpful, using
appropriate restaurant Japanese (keigo when appropriate).
""",
    "shopping": """
You're a shop clerk in Japan. The student is a customer looking to buy items,
ask about prices, sizes, or make a purchase. Use appropriate retail Japanese
and be courteous.
""",
    "directions": """
You're a helpful person on the street in Japan. The student is asking for directions
to various places. Provide clear directions and help them understand location-related
vocabulary and phrases.
""",
    "business": """
You're a colleague at a Japanese company. The student is practicing business Japanese
including formal greetings, office communication, and professional interactions.
Use appropriate business keigo (honorific language).
""",
    "interview": """
You're conducting a job interview in Japanese. Ask appropriate interview questions
and respond to the student's answers. Use formal business Japanese and maintain a
professional but friendly tone.
""",
    "introduction": """
You're meeting someone for the first time in Japan. Practice self-introductions,
asking about background, hobbies, and getting to know each other. Keep it friendly
and culturally appropriate.
""",
}


def get_conversation_system_prompt(
    user_level: str,
    scenario: str = "general",
) -> str:
    """
    Generate the system prompt for conversation practice.

    Args:
        user_level: JLPT level (N5, N4, N3, N2, N1)
        scenario: Conversation scenario

    Returns:
        Complete system prompt for the AI
    """
    scenario_context = SCENARIO_CONTEXTS.get(scenario, SCENARIO_CONTEXTS["general"])

    return f"""You are a patient and encouraging Japanese language tutor helping a student practice conversation.

STUDENT PROFILE:
- Current Level: {user_level}
- Learning Goal: Business-level Japanese proficiency
- Scenario: {scenario}

SCENARIO CONTEXT:
{scenario_context}

YOUR RESPONSIBILITIES:
1. Respond naturally in Japanese to continue the conversation
2. Match the complexity to the student's {user_level} level
3. If you notice grammar, particle, vocabulary, or usage errors, gently correct them
4. Provide brief, clear explanations for corrections in English
5. Maintain an encouraging and supportive tone
6. Focus on 1-2 key corrections per message to avoid overwhelming the student
7. Use the scenario context to guide conversation topics

RESPONSE FORMAT (CRITICAL - MUST FOLLOW EXACTLY):
Your response MUST be structured with XML-like tags:

<response>Your Japanese response here</response>
<correction>
Original: [the incorrect Japanese phrase]
Corrected: [the correct Japanese phrase]
Explanation: [brief English explanation of the error]
</correction>
<encouragement>Brief positive feedback in English</encouragement>

IMPORTANT NOTES:
- If there are NO errors, omit the <correction> tags entirely
- Keep corrections focused and specific
- Explanations should be concise (1-2 sentences max)
- Always include <response> and <encouragement> tags
- Do NOT use markdown or any other formatting
- The <correction> tag is OPTIONAL and should only appear when corrections are needed

EXAMPLES:

Example 1 (with correction):
<response>それはいいですね！どのくらい勉強しましたか？</response>
<correction>
Original: 私は学校に行きました
Corrected: 私は学校へ行きました
Explanation: For destinations, the particle へ (e) is more natural than に (ni) when indicating direction of movement.
</correction>
<encouragement>Great job forming a complete sentence! Your verb conjugation is perfect.</encouragement>

Example 2 (no correction needed):
<response>こんにちは！元気ですか？</response>
<encouragement>Perfect greeting! Your pronunciation looks good.</encouragement>

Now, respond to the student's message following this format exactly."""


def build_conversation_prompt(
    user_message: str,
    conversation_history: list[dict],
    user_level: str,
    scenario: str = "general",
    max_history: int = 10,
) -> str:
    """
    Build the complete conversation prompt including history.

    Args:
        user_message: The student's latest message
        conversation_history: List of previous messages [{"role": "user/assistant", "content": "..."}]
        user_level: JLPT level
        scenario: Conversation scenario
        max_history: Maximum number of history messages to include

    Returns:
        Complete prompt string for the AI
    """
    # Get system prompt
    system_prompt = get_conversation_system_prompt(user_level, scenario)

    # Build conversation history (keep only recent messages to avoid context overflow)
    recent_history = conversation_history[-max_history:] if conversation_history else []

    # Format history
    history_text = ""
    if recent_history:
        history_text = "\n\nCONVERSATION HISTORY:\n"
        for msg in recent_history:
            role_label = "Student" if msg["role"] == "user" else "You"
            history_text += f"{role_label}: {msg['content']}\n"

    # Add current message
    current_message = f"\n\nSTUDENT'S CURRENT MESSAGE:\n{user_message}\n\nYOUR RESPONSE:"

    return system_prompt + history_text + current_message


# Level-specific guidance
LEVEL_GUIDANCE = {
    "N5": {
        "vocabulary": "Basic everyday vocabulary (hiragana, katakana, ~100 kanji)",
        "grammar": "Present/past tense, basic particles (は、が、を、に、で、と、も)",
        "complexity": "Simple, short sentences (5-10 words)",
        "topics": "Self-introduction, daily routines, simple descriptions",
    },
    "N4": {
        "vocabulary": "Common vocabulary (~300 kanji), everyday expressions",
        "grammar": "Te-form, basic conjunctions, comparison, desire expressions",
        "complexity": "Simple compound sentences (10-15 words)",
        "topics": "Personal experiences, plans, opinions, simple conversations",
    },
    "N3": {
        "vocabulary": "Intermediate vocabulary (~650 kanji), common idioms",
        "grammar": "Conditionals, passives, causatives, various conjunctions",
        "complexity": "Complex sentences with multiple clauses",
        "topics": "Abstract concepts, explanations, expressing nuance",
    },
    "N2": {
        "vocabulary": "Advanced vocabulary (~1000 kanji), business terms",
        "grammar": "Advanced grammar, keigo (honorific language), formal expressions",
        "complexity": "Sophisticated sentence structures",
        "topics": "Business, news, complex discussions, formal situations",
    },
    "N1": {
        "vocabulary": "Professional vocabulary (~2000 kanji), technical terms",
        "grammar": "Expert-level grammar, literary expressions, advanced keigo",
        "complexity": "Native-like complexity",
        "topics": "Professional, academic, literary, any complex topic",
    },
}


def get_level_guidance(user_level: str) -> dict:
    """
    Get level-specific guidance for conversation complexity.

    Args:
        user_level: JLPT level (N5-N1)

    Returns:
        Dictionary with level-specific guidelines
    """
    return LEVEL_GUIDANCE.get(user_level, LEVEL_GUIDANCE["N5"])
