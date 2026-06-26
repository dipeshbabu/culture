import json
import os
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Dict, List, Tuple

import streamlit as st

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dependency may be absent in fallback demos
    load_dotenv = None


APP_TITLE = "Culture Remix Translator"
TAGLINE = "Most translation apps translate words. This translates context."
DEFAULT_PORTKEY_MODEL = "@vertexai/anthropic.claude-opus-4-6"
ARCHIVE_PATH = Path("culture-remix-archive.local.json")

FieldList = List[Tuple[str, str]]

TRANSLATOR_FIELDS: FieldList = [
    ("literal_meaning", "Literal meaning"),
    ("cultural_meaning", "Cultural meaning"),
    ("common_misunderstanding", "What people misunderstand"),
    ("personal_style_explanation", "Friend-style explanation"),
    ("modern_analogy", "Modern analogy"),
    ("say_it_out_loud", "Say it out loud"),
    ("sensitivity_note", "Nuance note"),
]

COPILOT_FIELDS: FieldList = [
    ("best_version", "Best version"),
    ("professional_version", "Professional version"),
    ("warm_personal_version", "Warm personal version"),
    ("short_message", "Short message"),
    ("caption_or_speech_line", "Caption or speech line"),
    ("why_it_works", "Why it works"),
    ("sensitivity_note", "Nuance note"),
]

MISUNDERSTANDING_FIELDS: FieldList = [
    ("what_they_missed", "What they missed"),
    ("respectful_reply", "Respectful reply"),
    ("shorter_reply", "Shorter reply"),
    ("repair_strategy", "Repair strategy"),
    ("what_not_to_say", "What not to say"),
    ("sensitivity_note", "Nuance note"),
]

FAMILY_FIELDS: FieldList = [
    ("what_older_generation_may_mean", "What they may mean"),
    ("what_younger_generation_may_feel", "What the other side may feel"),
    ("kind_response", "Kind response"),
    ("boundary_version", "Boundary version"),
    ("bridge_sentence", "Bridge sentence"),
    ("sensitivity_note", "Nuance note"),
]

COMPARE_FIELDS: FieldList = [
    ("shared_ground", "Shared ground"),
    ("key_differences", "Key differences"),
    ("likely_misread", "Likely misread"),
    ("bridge_analogy", "Bridge analogy"),
    ("explanation_for_target", "Explanation for target culture"),
    ("sensitivity_note", "Nuance note"),
]

ARCHIVE_FIELDS: FieldList = [
    ("archive_title", "Archive title"),
    ("family_story", "Family story"),
    ("meaning_underneath", "Meaning underneath"),
    ("how_to_explain_it", "How to explain it"),
    ("preservation_note", "Preservation note"),
]

EXAMPLES = [
    "Why Nepali parents ask \"khana khayau?\" instead of saying \"I love you\"",
    "Dashain tika",
    "Auntie culture",
    "Namaste, but not in a yoga-studio way",
]

TRANSLATOR_PRESETS = [
    {
        "label": "Khana Khayau?",
        "concept": EXAMPLES[0],
        "background": "Nepali / South Asian",
        "audience": "American coworkers",
        "tone": "First-gen kid explaining it to coworkers",
    },
    {
        "label": "Dashain Tika",
        "concept": "Dashain tika",
        "background": "Nepali",
        "audience": "American friends",
        "tone": "Warm and thoughtful",
    },
    {
        "label": "Auntie Culture",
        "concept": "Auntie culture",
        "background": "South Asian",
        "audience": "College friends",
        "tone": "Funny but respectful",
    },
    {
        "label": "Namaste Context",
        "concept": "Namaste, but not in a yoga-studio way",
        "background": "Nepali / Indian",
        "audience": "Western wellness audience",
        "tone": "Friend explaining to friend",
    },
]

COPILOT_PRESETS = [
    {
        "label": "Time-Off Note",
        "task": "Workplace time-off note",
        "context": "I want to explain why Dashain matters to me when I ask for time off.",
        "background": "Nepali",
        "audience": "Manager",
        "tone": "Professional but personal",
    },
    {
        "label": "Wedding Toast",
        "task": "Speech or toast",
        "context": "I want to explain receiving blessings from elders without making it sound overly formal.",
        "background": "Nepali / South Asian",
        "audience": "Mixed-culture wedding guests",
        "tone": "Warm and thoughtful",
    },
    {
        "label": "Instagram Caption",
        "task": "Social caption",
        "context": "I want to caption a photo of Dashain tika in a way that feels personal, not generic.",
        "background": "Nepali",
        "audience": "Friends who do not know Dashain",
        "tone": "Text message, natural",
    },
]

MISUNDERSTANDING_PRESETS = [
    {
        "label": "Auntie Gossip",
        "concept": "Auntie culture",
        "misunderstanding": "My coworker thought auntie culture just meant gossip.",
        "background": "South Asian",
        "audience": "Coworker",
        "outcome": "Correct them kindly",
    },
    {
        "label": "Namaste Yoga",
        "concept": "Namaste",
        "misunderstanding": "Someone said namaste is just a yoga studio word.",
        "background": "Nepali / Indian",
        "audience": "Friend",
        "outcome": "Explain without making it awkward",
    },
    {
        "label": "Food Pressure",
        "concept": "Khana khayau?",
        "misunderstanding": "They thought my parents were only pressuring me to eat.",
        "background": "Nepali / South Asian",
        "audience": "Partner",
        "outcome": "Explain without making it awkward",
    },
]

FAMILY_PRESETS = [
    {
        "label": "Did You Eat?",
        "situation": "My mom keeps asking if I ate. I know she cares, but sometimes it feels like pressure.",
        "older_side": "She is trying to show care through food and checking in.",
        "younger_side": "I want to feel trusted and not monitored.",
        "background": "Nepali / South Asian",
        "goal": "Set a soft boundary",
    },
    {
        "label": "Career Advice",
        "situation": "My parents keep suggesting safer career paths even though I want to pursue creative work.",
        "older_side": "They may connect stability with safety, sacrifice, and love.",
        "younger_side": "I want them to understand that creative work is not the same as being irresponsible.",
        "background": "Immigrant family",
        "goal": "Explain both sides",
    },
    {
        "label": "Calling Home",
        "situation": "My family feels hurt when I do not call often, but frequent calls can feel overwhelming.",
        "older_side": "Calls may be how they feel included and reassured.",
        "younger_side": "I need independence and a rhythm I can actually keep.",
        "background": "First-gen / immigrant family",
        "goal": "Respond kindly",
    },
]

COMPARE_PRESETS = [
    {
        "label": "Dashain & Thanksgiving",
        "concept": "Dashain tika",
        "source": "Nepali",
        "target": "American",
        "familiarity": "They understand Thanksgiving, Christmas family gatherings, and receiving blessings at major life events.",
    },
    {
        "label": "Namaste & Handshake",
        "concept": "Namaste",
        "source": "Nepali / Indian",
        "target": "American",
        "familiarity": "They understand handshakes, respectful greetings, and small gestures of politeness.",
    },
    {
        "label": "Aunties & Community Elders",
        "concept": "Auntie culture",
        "source": "South Asian",
        "target": "American",
        "familiarity": "They understand neighbors, family friends, church/community elders, and local social networks.",
    },
]

ARCHIVE_PRESETS = [
    {
        "label": "Khana Khayau?",
        "title": "Khana khayau?",
        "memory": "My parents ask if I ate whenever they call, even when they do not say emotional things directly.",
        "meaning": "It is a way of checking if I am okay and showing care through food.",
        "background": "Nepali / South Asian",
    },
    {
        "label": "Festival Clothes",
        "title": "Festival clothes",
        "memory": "My family takes photos in traditional clothes during festivals, even when everyone is busy or tired.",
        "meaning": "It preserves continuity and reminds us that we still belong to something together.",
        "background": "Diaspora family",
    },
    {
        "label": "Elder Blessings",
        "title": "Blessings from elders",
        "memory": "During festivals, elders bless us before we leave or start something important.",
        "meaning": "It is not just ritual. It is a way of sending protection, pride, and family memory with us.",
        "background": "Nepali / South Asian",
    },
]

BASE_SYSTEM_PROMPT = """You are Culture Remix Translator, a cultural communication assistant.

Your job is not only to translate words. Your job is to translate context, emotion, social meaning, family meaning, and common misunderstandings.

Be respectful, specific, warm, and clear. Avoid stereotypes. Do not pretend all people from a culture experience something the same way. Use phrases like "often," "can mean," or "in many families" when appropriate.

Return valid JSON only. Do not include markdown, comments, or any text outside the JSON object."""

MODE_INTROS = {
    "Context Translator": "Explain a phrase, tradition, food, slang term, or family habit through cultural context.",
    "Cultural Copilot": "Turn cultural meaning into a message, caption, email, speech, or workplace explanation.",
    "Misunderstanding Resolver": "Repair a moment where someone misunderstood a cultural phrase, practice, or habit.",
    "Family Translator": "Translate between generations, especially immigrant parents, elders, first-gen kids, and family members.",
    "Compare Cultures": "Explain one cultural concept through another culture's familiar reference points.",
    "Personal Archive": "Save family sayings, rituals, food memories, and traditions as a living cultural archive.",
}


def clean_concept(concept: str) -> str:
    return concept.strip() or EXAMPLES[0]


def field_names(fields: FieldList) -> List[str]:
    return [key for key, _ in fields]


def schema_instructions(fields: FieldList) -> str:
    return "\n".join(f"- {key}" for key in field_names(fields))


def set_model_status(message: str) -> None:
    try:
        st.session_state.model_status = message
    except Exception:
        pass


def extract_json_object(content: str) -> str:
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```json").removeprefix("```").strip()
        cleaned = cleaned.removesuffix("```").strip()

    if not cleaned.startswith("{"):
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            cleaned = cleaned[start : end + 1]

    return cleaned


def parse_json_response(content: str, fields: FieldList) -> Dict[str, str]:
    parsed = json.loads(extract_json_object(content))
    missing = [key for key in field_names(fields) if key not in parsed]
    if missing:
        raise ValueError(f"LLM response was missing expected fields: {', '.join(missing)}")
    return {key: str(parsed[key]).strip() for key, _ in fields}


def make_retry_prompt(fields: FieldList, previous_content: str, error: Exception) -> str:
    return f"""The previous response could not be parsed as the required JSON.

Parse error: {error.__class__.__name__}: {error}

Return JSON only with exactly these fields:
{schema_instructions(fields)}

Previous response:
{previous_content[:3000]}"""


def get_portkey_max_tokens() -> int:
    try:
        return int(os.getenv("PORTKEY_MAX_TOKENS", "2048"))
    except ValueError:
        return 2048


def get_portkey_timeout() -> int:
    try:
        return int(os.getenv("PORTKEY_TIMEOUT_SECONDS", "90"))
    except ValueError:
        return 90


def get_portkey_retries() -> int:
    try:
        return max(0, int(os.getenv("PORTKEY_RETRIES", "1")))
    except ValueError:
        return 1


def load_archive_items() -> List[Dict[str, object]]:
    if not ARCHIVE_PATH.exists():
        return []

    try:
        data = json.loads(ARCHIVE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []

    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]


def persist_archive_items(items: List[Dict[str, object]]) -> None:
    try:
        ARCHIVE_PATH.write_text(json.dumps(items, indent=2), encoding="utf-8")
    except OSError as exc:
        st.warning(f"Archive could not be saved locally: {exc}")


def ensure_archive_loaded() -> None:
    if "archive_items" not in st.session_state:
        st.session_state.archive_items = load_archive_items()


def call_structured_model(
    mode_name: str,
    fields: FieldList,
    user_prompt: str,
    fallback: Dict[str, str],
) -> Dict[str, str]:
    api_key = os.getenv("PORTKEY_API_KEY")
    model = os.getenv("PORTKEY_MODEL", DEFAULT_PORTKEY_MODEL)
    if not api_key:
        set_model_status("Using fallback: PORTKEY_API_KEY is not configured.")
        return fallback

    try:
        from portkey_ai import Portkey

        client = Portkey(
            base_url=os.getenv(
                "PORTKEY_BASE_URL", "https://ai-gateway.apps.cloud.rt.nyu.edu/v1"
            ),
            api_key=api_key,
        )
        system_prompt = f"""{BASE_SYSTEM_PROMPT}

Mode: {mode_name}

Return valid JSON only with exactly these fields:
{schema_instructions(fields)}"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        attempts = get_portkey_retries() + 1
        last_error: Exception | None = None
        last_content = ""
        for attempt in range(attempts):
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=get_portkey_max_tokens(),
                temperature=0.7 if attempt == 0 else 0.2,
                timeout=get_portkey_timeout(),
            )
            last_content = response.choices[0].message.content or "{}"
            try:
                parsed = parse_json_response(last_content, fields)
                suffix = "" if attempt == 0 else f" after {attempt + 1} attempts"
                set_model_status(f"Using live model: {model}{suffix}")
                return parsed
            except (json.JSONDecodeError, ValueError) as exc:
                last_error = exc
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": make_retry_prompt(fields, last_content, exc)},
                ]

        raise ValueError(f"Could not parse model JSON after {attempts} attempts: {last_error}")
    except Exception as exc:
        st.warning(
            "The live model response was unavailable or malformed, so the app used the reliable demo fallback."
        )
        st.caption(f"Fallback reason: {exc.__class__.__name__}: {exc}")
        set_model_status(f"Using fallback: {exc.__class__.__name__}: {exc}")
        return fallback


def fallback_translator(concept: str, background: str, audience: str, tone: str) -> Dict[str, str]:
    query = concept.lower()
    context = f"for {audience.strip() or 'someone from a different background'}"
    voice = tone.strip() or "Friend explaining to friend"

    if "khana" in query or "eat" in query or "khayau" in query:
        return {
            "literal_meaning": "\"Khana khayau?\" means \"Did you eat?\" or \"Have you eaten?\"",
            "cultural_meaning": "In many Nepali and South Asian families, asking about food can be a quiet way to check on someone's wellbeing. It can carry care, affection, and emotional attention without saying those feelings directly.",
            "common_misunderstanding": "Outsiders may hear it as a small practical question, or as pressure to eat. Often, it is also a love language and a way of saying, \"Are you okay?\"",
            "personal_style_explanation": f"{voice}: In my family, \"Did you eat?\" can be less about the meal and more about care. It is a practical question, but it also means someone is thinking about you.",
            "modern_analogy": "It is a bit like a check-in text that says \"get home safe\" or \"drink water\". The words are simple, but the feeling underneath is care.",
            "say_it_out_loud": "\"When my parents ask if I ate, it can be their way of saying they love me and want to know I am okay.\"",
            "sensitivity_note": "Not every Nepali or South Asian family uses this phrase the same way. Tone, relationship, generation, and household habits all change how it feels.",
        }

    if "dashain" in query:
        return {
            "literal_meaning": "Dashain tika refers to receiving tika, often a mixture of rice, yogurt, and vermilion, along with jamara and blessings during Dashain.",
            "cultural_meaning": "For many Nepali families, it is a moment of reunion, respect for elders, blessing, renewal, and being folded back into family ties.",
            "common_misunderstanding": "It can look like only a religious mark or a holiday custom. For many people, the deeper meaning is the blessing, the visit, the family hierarchy, and the feeling of being remembered.",
            "personal_style_explanation": f"{voice}: Dashain tika is when elders bless you, put tika and jamara on you, and you feel connected to family across distance, age, and tradition.",
            "modern_analogy": "It is like a family reunion, a blessing ceremony, and a yearly emotional reset happening in one ritual.",
            "say_it_out_loud": "\"Dashain tika is a family blessing ritual where elders mark you with tika and jamara, and the bigger meaning is connection, respect, and being blessed.\"",
            "sensitivity_note": "Dashain practices vary by region, caste, religion, family, and personal belief. Some people experience it mainly as culture, some as faith, and some with mixed feelings.",
        }

    if "auntie" in query:
        return {
            "literal_meaning": "\"Auntie\" can mean an actual aunt, but it can also refer to an older woman in the community or a family friend.",
            "cultural_meaning": "In many communities, aunties are part care system, part social authority, part gossip network, and part extended family.",
            "common_misunderstanding": "People may assume auntie only means a biological relative. Often it signals a broader community role, where someone is close enough to feed you, correct you, ask questions, and report back to your parents.",
            "personal_style_explanation": f"{voice}: Auntie culture is when older women around you are not exactly family, but they still act like they have a stake in your life.",
            "modern_analogy": "It is like a neighborhood group chat with snacks, memory, moral authority, and live commentary.",
            "say_it_out_loud": "\"An auntie is not always my actual aunt. She can be a community elder who cares about me, watches everything, and absolutely has opinions.\"",
            "sensitivity_note": "The word can be affectionate or annoying depending on context. It also differs across South Asian, African, Caribbean, Middle Eastern, and other communities.",
        }

    if "namaste" in query:
        return {
            "literal_meaning": "Namaste is a greeting often paired with folded hands, used to show respect and acknowledgment.",
            "cultural_meaning": "In many Nepali and Indian contexts, it can communicate politeness, humility, respect for elders, and social warmth. It is ordinary lived etiquette, not only a spiritual slogan.",
            "common_misunderstanding": "In Western wellness spaces, namaste can get flattened into a yoga-studio catchphrase. That can miss its everyday use as a respectful greeting in actual families and communities.",
            "personal_style_explanation": f"{voice}: Namaste is not just a mystical word. For many of us, it is a normal respectful greeting, especially with elders or in formal moments.",
            "modern_analogy": "It is closer to a respectful hello plus a small bow than to a decorative wellness quote.",
            "say_it_out_loud": "\"Namaste is a respectful greeting in my culture. It can be spiritual, but it is also everyday politeness and respect.\"",
            "sensitivity_note": "Usage varies by language, region, religion, and generation. The concern is not that outsiders can never say it, but that context and respect matter.",
        }

    base = concept.strip() or "this cultural concept"
    fallback_background = background.strip() or "the speaker's background"
    return {
        "literal_meaning": f"{base} is a culturally specific phrase, practice, or habit that may not translate cleanly word for word.",
        "cultural_meaning": f"In the context of {fallback_background}, it can carry social meaning, memory, affection, identity, or belonging beyond the literal words.",
        "common_misunderstanding": "People outside the culture may treat it as strange, overly formal, funny, or only practical when it may have emotional or relational meaning.",
        "personal_style_explanation": f"{voice}: I would explain it as one of those cultural things where the action matters, but the feeling underneath matters even more.",
        "modern_analogy": f"It is like a shared inside reference that helps people from the same background quickly understand care, respect, humor, or family expectations {context}.",
        "say_it_out_loud": f"\"It is hard to translate directly, but in my background, {base} can be a way of showing connection and context, not just the literal meaning.\"",
        "sensitivity_note": "This is a broad explanation. Cultural meaning changes by region, family, generation, class, religion, and personal experience.",
    }


def fallback_copilot(task: str, context: str, audience: str, tone: str) -> Dict[str, str]:
    audience_text = audience.strip() or "the person reading it"
    subject = context.strip() or "this cultural moment"
    return {
        "best_version": f"I would explain {subject} as something that carries more feeling than the literal action. It is a way of showing care, respect, memory, or belonging, depending on the family and context.",
        "professional_version": f"I wanted to share a bit of context: {subject} is culturally meaningful for me, and it can represent family connection, respect, and care beyond its literal meaning.",
        "warm_personal_version": f"For me, {subject} is not just a custom. It is connected to family, memory, and the way people show care without always saying it directly.",
        "short_message": f"{subject} is hard to translate directly, but it is one of those cultural things where the feeling underneath matters most.",
        "caption_or_speech_line": f"Some things do not translate word for word. They translate through memory, family, and feeling.",
        "why_it_works": f"This version gives {audience_text} enough context without turning the explanation into a lecture or flattening the culture into one rule.",
        "sensitivity_note": f"Keep the wording flexible. Culture changes by family, region, generation, and relationship, so avoid saying everyone experiences {subject} the same way.",
    }


def fallback_misunderstanding(concept: str, misunderstanding: str, audience: str) -> Dict[str, str]:
    subject = concept.strip() or "this cultural practice"
    missed = misunderstanding.strip() or "they focused only on the literal meaning"
    return {
        "what_they_missed": f"They may have missed that {subject} can carry emotional or social meaning beyond the surface action. The misunderstanding was: {missed}.",
        "respectful_reply": f"I get why it might look that way from the outside. For me, {subject} is not only about the literal action. It can also be about care, respect, belonging, or family memory.",
        "shorter_reply": f"It is less about the literal act and more about the meaning behind it.",
        "repair_strategy": "Start by validating why it may seem confusing, then explain the feeling underneath, then give a simple example from lived experience.",
        "what_not_to_say": "Avoid making the other person feel ignorant or saying that everyone from the culture sees it the same way.",
        "sensitivity_note": "A good repair leaves room for variation. Say what it means in your family or community rather than claiming one universal meaning.",
    }


def fallback_family(situation: str, older_side: str, younger_side: str) -> Dict[str, str]:
    subject = situation.strip() or "this family moment"
    return {
        "what_older_generation_may_mean": f"In {subject}, the older generation may be trying to show care, protection, respect, or responsibility through actions instead of direct emotional language.",
        "what_younger_generation_may_feel": "The younger person may understand the care but still feel pressure, guilt, control, or emotional distance if the message is indirect.",
        "kind_response": "I know this is your way of caring about me, and I appreciate it. I also want to be able to explain what I need directly.",
        "boundary_version": "I hear the care behind it, but I need a little space. I will let you know what I need, and I still know you care.",
        "bridge_sentence": "Both sides may be trying to stay connected, but they are using different emotional languages.",
        "sensitivity_note": "Family dynamics vary widely. This should be used as a bridge, not as a diagnosis of any parent, elder, or child.",
    }


def fallback_compare(concept: str, source_culture: str, target_culture: str) -> Dict[str, str]:
    subject = concept.strip() or "this cultural concept"
    source = source_culture.strip() or "the source culture"
    target = target_culture.strip() or "the target culture"
    return {
        "shared_ground": f"{subject} in {source} may connect to familiar ideas in {target}: family gathering, respect, care, obligation, memory, or belonging.",
        "key_differences": "The emotional weight, who participates, what counts as respectful, and how directly feelings are spoken may differ.",
        "likely_misread": f"Someone from {target} may read {subject} as only symbolic, formal, or practical if they do not know the family meaning behind it.",
        "bridge_analogy": "Think of it as a family ritual where the action matters, but the real message is connection and recognition.",
        "explanation_for_target": f"In {source}, {subject} can be a way people express values that may be familiar in {target}, but through different rituals, words, or expectations.",
        "sensitivity_note": "Comparisons should create a bridge, not claim two cultures are the same. Use analogies as entry points, then explain the differences.",
    }


def fallback_archive(title: str, memory: str, meaning: str) -> Dict[str, str]:
    archive_title = title.strip() or "Family memory"
    story = memory.strip() or "A family saying, ritual, food memory, or tradition worth preserving."
    meaning_text = meaning.strip() or "It carries care, belonging, memory, and a feeling that is hard to translate directly."
    return {
        "archive_title": archive_title,
        "family_story": story,
        "meaning_underneath": meaning_text,
        "how_to_explain_it": f"I would explain {archive_title} as something that matters because of the feeling and relationship behind it, not only the visible action.",
        "preservation_note": "Save who said it, when it happened, what it felt like, and what outsiders might miss. Those details preserve the cultural texture.",
    }


def build_translator_response(concept: str, background: str, audience: str, tone: str) -> Dict[str, str]:
    prompt = f"""Cultural phrase or concept: {concept}
User background: {background}
Target audience: {audience}
Tone: {tone}

Explain this concept to the target audience."""
    return call_structured_model(
        "Context Translator",
        TRANSLATOR_FIELDS,
        prompt,
        fallback_translator(concept, background, audience, tone),
    )


def build_copilot_response(task: str, context: str, background: str, audience: str, tone: str) -> Dict[str, str]:
    prompt = f"""Writing task: {task}
Cultural context to communicate: {context}
User background: {background}
Audience: {audience}
Tone: {tone}

Write useful versions the user could actually send or say. Avoid cringe, over-formality, and generic cultural claims."""
    return call_structured_model(
        "Cultural Copilot",
        COPILOT_FIELDS,
        prompt,
        fallback_copilot(task, context, audience, tone),
    )


def build_misunderstanding_response(
    concept: str,
    misunderstanding: str,
    background: str,
    audience: str,
    desired_outcome: str,
) -> Dict[str, str]:
    prompt = f"""Cultural concept: {concept}
User background: {background}
Who misunderstood it: {audience}
What happened or what they said: {misunderstanding}
Desired outcome: {desired_outcome}

Help the user repair the misunderstanding respectfully and clearly."""
    return call_structured_model(
        "Misunderstanding Resolver",
        MISUNDERSTANDING_FIELDS,
        prompt,
        fallback_misunderstanding(concept, misunderstanding, audience),
    )


def build_family_response(
    situation: str,
    older_side: str,
    younger_side: str,
    background: str,
    goal: str,
) -> Dict[str, str]:
    prompt = f"""Family situation: {situation}
Cultural background: {background}
Older generation or first person's perspective: {older_side}
Younger generation or second person's perspective: {younger_side}
Goal for the conversation: {goal}

Translate the emotional meaning on both sides and give kind language they could use."""
    return call_structured_model(
        "Family Translator",
        FAMILY_FIELDS,
        prompt,
        fallback_family(situation, older_side, younger_side),
    )


def build_compare_response(
    concept: str,
    source_culture: str,
    target_culture: str,
    target_familiarity: str,
) -> Dict[str, str]:
    prompt = f"""Concept to explain: {concept}
Source culture or background: {source_culture}
Target culture or background: {target_culture}
Target audience may be familiar with: {target_familiarity}

Compare cultures carefully. Use analogies as bridges, not as claims that the cultures are identical."""
    return call_structured_model(
        "Compare Cultures",
        COMPARE_FIELDS,
        prompt,
        fallback_compare(concept, source_culture, target_culture),
    )


def build_archive_response(title: str, memory: str, meaning: str, background: str) -> Dict[str, str]:
    prompt = f"""Archive title or phrase: {title}
Cultural or family background: {background}
Memory, ritual, food, saying, or tradition: {memory}
Meaning the user wants preserved: {meaning}

Turn this into a concise cultural archive entry that preserves feeling, context, and nuance."""
    return call_structured_model(
        "Personal Archive",
        ARCHIVE_FIELDS,
        prompt,
        fallback_archive(title, memory, meaning),
    )


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            color-scheme: light;
            --accent: #0070f3;
            --accent-strong: #005bd3;
            --warm: #b45309;
            --ink: #09090b;
            --muted: #71717a;
            --soft: #3f3f46;
            --surface: #ffffff;
            --surface-raised: #fafafa;
            --card: #ffffff;
            --card-hover: #f7f7f8;
            --line: #e4e4e7;
            --line-strong: #c9c9cf;
            --bg-top: #ffffff;
            --bg-bot: #f4f4f5;
            --focus: rgba(0, 112, 243, 0.22);
            --shadow: 0 18px 44px rgba(24, 24, 27, 0.08);
        }

        .stApp {
            background:
                linear-gradient(180deg, rgba(255, 255, 255, 0.94) 0%, rgba(244, 244, 245, 0.96) 100%);
            color: var(--ink);
            overflow-x: hidden;
            overscroll-behavior-x: none;
            -webkit-tap-highlight-color: transparent;
        }

        .skip-link {
            background: var(--ink);
            border-radius: 10px;
            color: #ffffff;
            font-weight: 700;
            left: 1rem;
            padding: 0.65rem 0.85rem;
            position: fixed;
            top: 1rem;
            transform: translateY(-180%);
            transition: transform 140ms ease;
            z-index: 9999;
        }

        .skip-link:focus-visible {
            box-shadow: 0 0 0 3px var(--focus);
            outline: 0;
            transform: translateY(0);
        }

        #main-content {
            scroll-margin-top: 1rem;
        }

        header[data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        #MainMenu,
        footer {
            visibility: hidden;
        }

        .block-container {
            max-width: 1180px;
            padding-top: 2rem;
            padding-bottom: 4rem;
            padding-left: max(1.25rem, env(safe-area-inset-left));
            padding-right: max(1.25rem, env(safe-area-inset-right));
        }

        h1 {
            color: var(--ink);
            font-size: clamp(2.55rem, 6vw, 5.25rem) !important;
            font-weight: 800 !important;
            line-height: 0.95 !important;
            letter-spacing: 0 !important;
            margin-bottom: 0.85rem !important;
            max-width: 900px;
            text-wrap: balance;
        }

        .tagline {
            color: var(--ink);
            font-size: clamp(1.12rem, 2vw, 1.38rem);
            font-weight: 700;
            margin-bottom: 0.55rem;
            max-width: 840px;
        }

        .intro {
            color: var(--muted);
            font-size: 1.05rem;
            line-height: 1.65;
            max-width: 790px;
            margin-bottom: 1rem;
            text-wrap: pretty;
        }

        .hero-strip {
            align-items: center;
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
            margin: 0.2rem 0 1.25rem;
        }

        .hero-pill {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 999px;
            color: var(--soft);
            font-size: 0.82rem;
            font-weight: 650;
            padding: 0.34rem 0.65rem;
            box-shadow: 0 6px 20px rgba(24, 24, 27, 0.04);
        }

        .hero-pill strong {
            color: var(--ink);
            font-weight: 750;
        }

        label,
        div[data-testid="stTextArea"] label p,
        div[data-testid="stTextInput"] label p,
        div[data-testid="stSelectbox"] label p {
            color: var(--ink) !important;
        }

        div[data-testid="stTextArea"] textarea,
        div[data-testid="stTextInput"] input {
            border-radius: 10px;
            border: 1px solid var(--line);
            background: var(--surface);
            color: var(--ink);
            box-shadow: inset 0 0 0 1px transparent;
            transition: border-color 140ms ease, box-shadow 140ms ease, background-color 140ms ease;
        }

        div[data-testid="stTextArea"] textarea::placeholder,
        div[data-testid="stTextInput"] input::placeholder {
            color: var(--muted);
            opacity: 0.75;
        }

        div[data-testid="stTextArea"] textarea:focus-visible,
        div[data-testid="stTextInput"] input:focus-visible {
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 3px var(--focus) !important;
            outline: 0;
        }

        div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
            background: var(--surface);
            border-color: var(--line);
            color: var(--ink);
            border-radius: 10px;
        }

        div[data-testid="stSelectbox"] [data-baseweb="select"]:focus-within > div {
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 3px var(--focus) !important;
        }

        div[data-testid="stSelectbox"] [data-baseweb="select"] span {
            color: var(--ink);
        }

        div[data-testid="stTabs"] [role="tablist"] {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 12px;
            gap: 0.15rem;
            margin: 1.2rem 0 0.6rem;
            overflow-x: auto;
            padding: 0.28rem;
            box-shadow: 0 10px 30px rgba(24, 24, 27, 0.05);
        }

        div[data-testid="stTabs"] button[role="tab"] {
            border-radius: 9px;
            color: var(--muted);
            min-height: 2.45rem;
            padding: 0.35rem 0.7rem;
            transition: background-color 140ms ease, color 140ms ease;
        }

        div[data-testid="stTabs"] button[role="tab"]:hover {
            background: var(--surface-raised);
            color: var(--ink);
        }

        div[data-testid="stTabs"] button[role="tab"]:focus-visible {
            box-shadow: 0 0 0 3px var(--focus);
            outline: 0;
        }

        div[data-testid="stTabs"] button[aria-selected="true"] {
            background: var(--ink);
            color: var(--ink) !important;
        }

        div[data-testid="stTabs"] button[aria-selected="true"] p {
            color: #ffffff !important;
            font-weight: 750;
        }

        div[data-testid="stButton"] button {
            background: var(--surface-raised);
            border-radius: 10px;
            border: 1px solid var(--line);
            color: var(--ink);
            font-weight: 700;
            min-height: 2.55rem;
            touch-action: manipulation;
            transition: background-color 140ms ease, border-color 140ms ease, color 140ms ease, transform 140ms ease;
        }

        div[data-testid="stButton"] button:hover {
            background: var(--card-hover);
            border-color: var(--accent) !important;
            color: var(--accent) !important;
        }

        div[data-testid="stButton"] button:active {
            transform: translateY(1px);
        }

        div[data-testid="stButton"] button:focus-visible {
            box-shadow: 0 0 0 3px var(--focus);
            outline: 0;
        }

        div[data-testid="stButton"] button p,
        div[data-testid="stButton"] button span {
            color: inherit;
        }

        div[data-testid="stButton"] button[kind="primary"] {
            background: var(--ink);
            border-color: var(--ink);
            color: #ffffff;
        }

        div[data-testid="stButton"] button[kind="primary"]:hover {
            background: var(--accent);
            border-color: var(--accent) !important;
            color: #ffffff !important;
        }

        .section-kicker {
            color: var(--muted);
            font-size: 0.76rem;
            font-weight: 780;
            letter-spacing: 0.06em;
            margin: 1rem 0 0.55rem;
            text-transform: uppercase;
        }

        .result-card {
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 14px;
            box-shadow: var(--shadow);
            height: 100%;
            min-height: 168px;
            padding: 1.15rem 1.2rem;
            transition: background-color 140ms ease, border-color 140ms ease, transform 140ms ease;
            word-break: break-word;
            overflow-wrap: anywhere;
        }

        .result-card:hover {
            background: var(--card-hover);
            border-color: var(--line-strong);
            transform: translateY(-1px);
        }

        .result-card h3 {
            color: var(--ink);
            font-size: 0.92rem;
            font-weight: 760;
            letter-spacing: 0 !important;
            margin: 0 0 0.55rem;
        }

        .result-card p {
            color: var(--soft);
            font-size: 0.98rem;
            line-height: 1.58;
            margin: 0;
            white-space: pre-wrap;
            overflow-wrap: anywhere;
        }

        .results-grid {
            align-items: stretch;
            display: grid;
            gap: 1rem;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            margin-top: 0.15rem;
            width: 100%;
        }

        .results-grid .result-card {
            min-width: 0;
        }

        .share-card {
            background: linear-gradient(180deg, #ffffff 0%, #f3f8ff 100%);
            border: 1px solid rgba(0, 112, 243, 0.22);
            border-radius: 14px;
            color: var(--ink);
            padding: 1.15rem 1.2rem;
            margin-top: 1rem;
            box-shadow: var(--shadow);
        }

        .share-card h3 {
            color: var(--accent);
            font-size: 1rem;
            margin: 0 0 0.45rem;
        }

        .share-card p {
            color: var(--ink);
            line-height: 1.5;
            margin: 0;
            white-space: pre-wrap;
            overflow-wrap: anywhere;
        }

        .mode-note {
            background: var(--surface);
            border: 1px solid var(--line);
            border-left: 3px solid var(--accent);
            border-radius: 12px;
            color: var(--soft);
            margin: 0.65rem 0 1.15rem;
            padding: 0.85rem 0.95rem;
            box-shadow: 0 10px 30px rgba(24, 24, 27, 0.04);
            text-wrap: pretty;
        }

        .model-status {
            align-items: center;
            border: 1px solid var(--line);
            border-radius: 999px;
            color: var(--soft);
            display: inline-flex;
            font-size: 0.82rem;
            font-weight: 650;
            gap: 0.45rem;
            margin: 0.1rem 0 0.9rem;
            padding: 0.32rem 0.62rem;
        }

        .model-status::before {
            border-radius: 999px;
            content: "";
            display: inline-block;
            height: 0.48rem;
            width: 0.48rem;
        }

        .model-status.live {
            background: #f0fdf4;
            border-color: #bbf7d0;
        }

        .model-status.live::before {
            background: #3fb950;
        }

        .model-status.fallback {
            background: #fffbeb;
            border-color: #fde68a;
        }

        .model-status.fallback::before {
            background: var(--warm);
        }

        label, .stSelectbox label, .stTextInput label, .stTextArea label {
            color: var(--muted) !important;
        }

        div[data-testid="column"] {
            min-width: 0;
        }

        * {
            scrollbar-color: var(--line-strong) var(--surface);
        }

        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                transition-duration: 0.01ms !important;
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                scroll-behavior: auto !important;
            }
        }

        @media (max-width: 640px) {
            .block-container {
                padding-top: 1.6rem;
            }

            h1 {
                font-size: 2.25rem !important;
            }

            .result-card {
                min-height: auto;
            }

            .results-grid {
                grid-template-columns: minmax(0, 1fr);
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def card_html(title: str, body: str) -> str:
    safe_body = body.strip() or "No content returned."
    return f"""
        <div class="result-card">
            <h3>{escape(title)}</h3>
            <p>{escape(safe_body)}</p>
        </div>
    """


def render_card(title: str, body: str) -> None:
    st.markdown(card_html(title, body), unsafe_allow_html=True)


def render_copy_panel(title: str, text: str, _key: str) -> None:
    if not text:
        return
    st.markdown(f'<div class="section-kicker">{escape(title)}</div>', unsafe_allow_html=True)
    st.code(text, language=None)


def render_results(fields: FieldList, response: Dict[str, str], share_key: str = "") -> None:
    if "model_status" in st.session_state:
        status = st.session_state.model_status
        status_kind = "live" if status.startswith("Using live model") else "fallback"
        st.markdown(
            f'<div class="model-status {status_kind}">{escape(status)}</div>',
            unsafe_allow_html=True,
        )

    cards = "\n".join(card_html(title, response.get(key, "")) for key, title in fields)
    st.markdown(
        f"""
        <div class="results-grid">
            {cards}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if share_key and response.get(share_key):
        st.markdown(
            f"""
            <div class="share-card">
                <h3>Ready to use</h3>
                <p>{escape(response[share_key])}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_copy_panel("Copy-ready text", response[share_key], share_key)


def add_to_archive(mode: str, title: str, response: Dict[str, str]) -> None:
    ensure_archive_loaded()
    st.session_state.archive_items.insert(
        0,
        {
            "saved_at": datetime.now().isoformat(timespec="seconds"),
            "mode": mode,
            "title": title or mode,
            "response": response,
        },
    )
    persist_archive_items(st.session_state.archive_items)


def archive_download() -> str:
    return json.dumps(st.session_state.get("archive_items", []), indent=2)


def archive_entry_preview(item: Dict[str, object]) -> Tuple[str, str]:
    response = item.get("response")
    if not isinstance(response, dict):
        response = {}

    title = str(item.get("title") or "Untitled entry")
    mode = str(item.get("mode") or "Archive")
    body = (
        response.get("how_to_explain_it")
        or response.get("say_it_out_loud")
        or response.get("best_version")
        or next((str(value) for value in response.values() if value), "")
    )
    return f"{title} - {mode}", str(body)


def set_defaults(defaults: Dict[str, str]) -> None:
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def render_preset_buttons(
    presets: List[Dict[str, str]],
    key_prefix: str,
    field_map: Dict[str, str],
) -> None:
    st.markdown('<div class="section-kicker">Quick starts</div>', unsafe_allow_html=True)
    cols = st.columns(min(4, len(presets)))
    for index, preset in enumerate(presets):
        with cols[index % len(cols)]:
            label = preset["label"]
            if st.button(label, key=f"{key_prefix}_preset_{index}", use_container_width=True):
                for preset_key, state_key in field_map.items():
                    st.session_state[state_key] = preset[preset_key]
                st.rerun()


def common_context(prefix: str = "") -> Tuple[str, str, str]:
    background = st.text_input(
        "My background",
        key=f"{prefix}background",
    )
    audience = st.text_input(
        "Target audience",
        key=f"{prefix}audience",
    )
    tone = st.selectbox(
        "Tone",
        [
            "Friend explaining to friend",
            "Warm and thoughtful",
            "Funny but respectful",
            "Grandparent storytelling style",
            "First-gen kid explaining it to coworkers",
            "Professional but personal",
            "Text message, natural",
        ],
        key=f"{prefix}tone",
    )
    return background, audience, tone


def translator_mode() -> None:
    set_defaults(
        {
            "concept": EXAMPLES[0],
            "translator_background": "Nepali / South Asian",
            "translator_audience": "American coworkers or friends",
            "translator_tone": "Friend explaining to friend",
        }
    )
    render_preset_buttons(
        TRANSLATOR_PRESETS,
        "translator",
        {
            "concept": "concept",
            "background": "translator_background",
            "audience": "translator_audience",
            "tone": "translator_tone",
        },
    )

    left, right = st.columns([1.1, 0.9], gap="large")
    with left:
        concept = st.text_area(
            "Cultural phrase or concept",
            key="concept",
            height=150,
            placeholder="Example: Why Nepali parents ask \"khana khayau?\" instead of saying \"I love you\"...",
        )
    with right:
        background, audience, tone = common_context("translator_")

    if st.button("Translate Context", type="primary", use_container_width=True):
        final_concept = clean_concept(concept)
        with st.spinner("Translating context..."):
            response = build_translator_response(final_concept, background, audience, tone)
        st.session_state.translator_response = response
        st.session_state.translator_title = final_concept
        add_to_archive("Context Translator", final_concept, response)

    if "translator_response" in st.session_state:
        st.markdown('<div class="section-kicker">Context translation</div>', unsafe_allow_html=True)
        render_results(TRANSLATOR_FIELDS, st.session_state.translator_response, "say_it_out_loud")


def copilot_mode() -> None:
    set_defaults(
        {
            "copilot_task": "Workplace time-off note",
            "copilot_context": "I want to explain why Dashain matters to me when I ask for time off.",
            "copilot_background": "Nepali / South Asian",
            "copilot_audience": "American coworkers or friends",
            "copilot_tone": "Professional but personal",
        }
    )
    render_preset_buttons(
        COPILOT_PRESETS,
        "copilot",
        {
            "task": "copilot_task",
            "context": "copilot_context",
            "background": "copilot_background",
            "audience": "copilot_audience",
            "tone": "copilot_tone",
        },
    )
    left, right = st.columns([1.05, 0.95], gap="large")
    with left:
        task = st.selectbox(
            "Message Type",
            [
                "Slack or Teams message",
                "Email",
                "Speech or toast",
                "Social caption",
                "Classroom explanation",
                "Workplace time-off note",
            ],
            key="copilot_task",
        )
        context = st.text_area(
            "What cultural meaning do you need to communicate?",
            placeholder="Example: I want to explain why Dashain matters to me when I ask for time off...",
            height=160,
            key="copilot_context",
        )
    with right:
        background, audience, tone = common_context("copilot_")

    if st.button("Draft Message", type="primary", use_container_width=True):
        with st.spinner("Writing versions..."):
            response = build_copilot_response(task, context, background, audience, tone)
        st.session_state.copilot_response = response
        add_to_archive("Cultural Copilot", task, response)

    if "copilot_response" in st.session_state:
        st.markdown('<div class="section-kicker">Cultural copilot</div>', unsafe_allow_html=True)
        render_results(COPILOT_FIELDS, st.session_state.copilot_response, "best_version")


def misunderstanding_mode() -> None:
    set_defaults(
        {
            "mis_concept": "Auntie culture",
            "mis_misunderstanding": "My coworker thought auntie culture just meant gossip.",
            "mis_background": "South Asian",
            "mis_audience": "Coworker",
            "mis_outcome": "Correct them kindly",
        }
    )
    render_preset_buttons(
        MISUNDERSTANDING_PRESETS,
        "misunderstanding",
        {
            "concept": "mis_concept",
            "misunderstanding": "mis_misunderstanding",
            "background": "mis_background",
            "audience": "mis_audience",
            "outcome": "mis_outcome",
        },
    )
    left, right = st.columns([1.05, 0.95], gap="large")
    with left:
        concept = st.text_input("Cultural phrase or practice", key="mis_concept")
        misunderstanding = st.text_area(
            "What did they misunderstand?",
            placeholder="Example: My coworker thought auntie culture just meant gossip...",
            height=140,
            key="mis_misunderstanding",
        )
    with right:
        background = st.text_input("My background", key="mis_background")
        audience = st.text_input("Who misunderstood it?", key="mis_audience")
        desired_outcome = st.selectbox(
            "Desired Outcome",
            [
                "Correct them kindly",
                "Explain without making it awkward",
                "Set a boundary",
                "Make it funny but respectful",
            ],
            key="mis_outcome",
        )

    if st.button("Repair Misunderstanding", type="primary", use_container_width=True):
        with st.spinner("Building repair response..."):
            response = build_misunderstanding_response(
                concept, misunderstanding, background, audience, desired_outcome
            )
        st.session_state.misunderstanding_response = response
        add_to_archive("Misunderstanding Resolver", concept, response)

    if "misunderstanding_response" in st.session_state:
        st.markdown('<div class="section-kicker">Misunderstanding repair</div>', unsafe_allow_html=True)
        render_results(MISUNDERSTANDING_FIELDS, st.session_state.misunderstanding_response, "respectful_reply")


def family_mode() -> None:
    set_defaults(
        {
            "family_situation": "My mom keeps asking if I ate. I know she cares, but sometimes it feels like pressure.",
            "family_older_side": "She is trying to show care through food and checking in.",
            "family_younger_side": "I want to feel trusted and not monitored.",
            "family_background": "Nepali / South Asian",
            "family_goal": "Set a soft boundary",
        }
    )
    render_preset_buttons(
        FAMILY_PRESETS,
        "family",
        {
            "situation": "family_situation",
            "older_side": "family_older_side",
            "younger_side": "family_younger_side",
            "background": "family_background",
            "goal": "family_goal",
        },
    )
    left, right = st.columns([1.05, 0.95], gap="large")
    with left:
        situation = st.text_area(
            "Family situation",
            placeholder="Example: My mom keeps asking if I ate, and I know she cares, but it feels like pressure...",
            height=145,
            key="family_situation",
        )
        older_side = st.text_area(
            "Older generation or first person's side",
            placeholder="Example: She is trying to show care through food and checking in...",
            height=110,
            key="family_older_side",
        )
    with right:
        younger_side = st.text_area(
            "Younger generation or second person's side",
            placeholder="Example: I want to feel trusted and not monitored...",
            height=110,
            key="family_younger_side",
        )
        background = st.text_input("Family background", key="family_background")
        goal = st.selectbox(
            "Conversation Goal",
            [
                "Explain both sides",
                "Respond kindly",
                "Set a soft boundary",
                "Prepare for a hard conversation",
            ],
            key="family_goal",
        )

    if st.button("Translate Family Meaning", type="primary", use_container_width=True):
        with st.spinner("Translating both sides..."):
            response = build_family_response(situation, older_side, younger_side, background, goal)
        st.session_state.family_response = response
        add_to_archive("Family Translator", "Family translation", response)

    if "family_response" in st.session_state:
        st.markdown('<div class="section-kicker">Family translation</div>', unsafe_allow_html=True)
        render_results(FAMILY_FIELDS, st.session_state.family_response, "bridge_sentence")


def compare_mode() -> None:
    set_defaults(
        {
            "compare_concept": "Dashain tika",
            "compare_familiarity": "They understand Thanksgiving, Christmas family gatherings, and receiving blessings at major life events.",
            "compare_source": "Nepali",
            "compare_target": "American",
        }
    )
    render_preset_buttons(
        COMPARE_PRESETS,
        "compare",
        {
            "concept": "compare_concept",
            "source": "compare_source",
            "target": "compare_target",
            "familiarity": "compare_familiarity",
        },
    )
    left, right = st.columns([1.05, 0.95], gap="large")
    with left:
        concept = st.text_input("Concept to explain", key="compare_concept")
        target_familiarity = st.text_area(
            "What might the target audience already understand?",
            placeholder="Example: They understand Thanksgiving, Christmas family gatherings, and receiving blessings...",
            height=135,
            key="compare_familiarity",
        )
    with right:
        source_culture = st.text_input("Source culture", key="compare_source")
        target_culture = st.text_input("Target culture", key="compare_target")

    if st.button("Compare Cultures", type="primary", use_container_width=True):
        with st.spinner("Finding bridges and differences..."):
            response = build_compare_response(concept, source_culture, target_culture, target_familiarity)
        st.session_state.compare_response = response
        add_to_archive("Compare Cultures", concept, response)

    if "compare_response" in st.session_state:
        st.markdown('<div class="section-kicker">Culture comparison</div>', unsafe_allow_html=True)
        render_results(COMPARE_FIELDS, st.session_state.compare_response, "explanation_for_target")


def archive_mode() -> None:
    ensure_archive_loaded()
    set_defaults(
        {
            "archive_title": "Khana khayau?",
            "archive_memory": "My parents ask if I ate whenever they call, even when they do not say emotional things directly.",
            "archive_meaning": "It is a way of checking if I am okay and showing care through food.",
            "archive_background": "Nepali / South Asian",
        }
    )
    render_preset_buttons(
        ARCHIVE_PRESETS,
        "archive",
        {
            "title": "archive_title",
            "memory": "archive_memory",
            "meaning": "archive_meaning",
            "background": "archive_background",
        },
    )

    left, right = st.columns([1.05, 0.95], gap="large")
    with left:
        title = st.text_input("Archive title", key="archive_title")
        memory = st.text_area(
            "Memory, ritual, saying, food, or tradition",
            placeholder="Example: My parents ask if I ate whenever they call...",
            height=145,
            key="archive_memory",
        )
    with right:
        meaning = st.text_area(
            "Meaning you want preserved",
            placeholder="Example: It is a way of checking if I am okay and showing care through food...",
            height=110,
            key="archive_meaning",
        )
        background = st.text_input("Family or cultural background", key="archive_background")

    if st.button("Create Archive Entry", type="primary", use_container_width=True):
        with st.spinner("Preserving memory..."):
            response = build_archive_response(title, memory, meaning, background)
        st.session_state.archive_response = response
        add_to_archive("Personal Archive", response.get("archive_title", title), response)

    if "archive_response" in st.session_state:
        st.markdown('<div class="section-kicker">New archive entry</div>', unsafe_allow_html=True)
        render_results(ARCHIVE_FIELDS, st.session_state.archive_response, "how_to_explain_it")

    st.markdown('<div class="section-kicker">Saved archive</div>', unsafe_allow_html=True)
    if st.session_state.archive_items:
        st.download_button(
            "Download archive JSON",
            data=archive_download(),
            file_name="culture-remix-archive.json",
            mime="application/json",
            use_container_width=True,
        )
        for item in st.session_state.archive_items[:8]:
            title_text, body = archive_entry_preview(item)
            render_card(title_text, body)
    else:
        render_card("No saved entries yet", "Translate, draft, repair, compare, or create an archive entry to save it here during this session.")


def render_mode_note(mode: str) -> None:
    st.markdown(
        f'<div class="mode-note">{escape(MODE_INTROS[mode])}</div>',
        unsafe_allow_html=True,
    )


def main() -> None:
    if load_dotenv is not None:
        load_dotenv()

    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="CT",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    inject_styles()

    st.markdown('<a class="skip-link" href="#main-content">Skip to Main Content</a>', unsafe_allow_html=True)
    st.markdown('<main id="main-content">', unsafe_allow_html=True)
    st.title(APP_TITLE)
    st.markdown(f'<div class="tagline">{TAGLINE}</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="intro">A cultural communication assistant for explaining meaning, repairing misunderstandings, comparing contexts, and preserving family memory.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="hero-strip">
            <span class="hero-pill"><strong>6</strong> communication modes</span>
            <span class="hero-pill">Live model with fallback</span>
            <span class="hero-pill">Session archive export</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    mode_names = list(MODE_INTROS.keys())
    tabs = st.tabs(mode_names)

    with tabs[0]:
        render_mode_note("Context Translator")
        translator_mode()
    with tabs[1]:
        render_mode_note("Cultural Copilot")
        copilot_mode()
    with tabs[2]:
        render_mode_note("Misunderstanding Resolver")
        misunderstanding_mode()
    with tabs[3]:
        render_mode_note("Family Translator")
        family_mode()
    with tabs[4]:
        render_mode_note("Compare Cultures")
        compare_mode()
    with tabs[5]:
        render_mode_note("Personal Archive")
        archive_mode()
    st.markdown("</main>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
