import json
import os
from datetime import datetime
from html import escape
from typing import Dict, Iterable, List, Tuple

import streamlit as st

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dependency may be absent in fallback demos
    load_dotenv = None


APP_TITLE = "Culture Remix Translator"
TAGLINE = "Most translation apps translate words. This translates context."
DEFAULT_PORTKEY_MODEL = "@vertexai/anthropic.claude-opus-4-6"

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
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=get_portkey_max_tokens(),
            temperature=0.7,
            timeout=get_portkey_timeout(),
        )
        content = response.choices[0].message.content or "{}"
        parsed = parse_json_response(content, fields)
        set_model_status(f"Using live model: {model}")
        return parsed
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
            --accent: #e8845c;
            --ink: #f0e8e0;
            --muted: #b2a49c;
            --surface: #1e1a18;
            --card: #252120;
            --line: #3a3330;
            --bg-top: #141210;
            --bg-bot: #1a1614;
        }

        .stApp {
            background: linear-gradient(180deg, var(--bg-top) 0%, var(--bg-bot) 100%);
            color: var(--ink);
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
            max-width: 1120px;
            padding-top: 2.4rem;
            padding-bottom: 3rem;
        }

        h1 {
            color: var(--ink);
            font-size: 3rem !important;
            line-height: 1.05 !important;
            letter-spacing: 0 !important;
            margin-bottom: 0.35rem !important;
        }

        .tagline {
            color: var(--accent);
            font-size: 1.28rem;
            font-weight: 700;
            margin-bottom: 0.4rem;
        }

        .intro {
            color: var(--muted);
            font-size: 1.02rem;
            max-width: 780px;
            margin-bottom: 1.2rem;
        }

        label,
        div[data-testid="stTextArea"] label p,
        div[data-testid="stTextInput"] label p,
        div[data-testid="stSelectbox"] label p,
        div[data-testid="stRadio"] label p {
            color: var(--ink) !important;
        }

        div[data-testid="stTextArea"] textarea,
        div[data-testid="stTextInput"] input {
            border-radius: 8px;
            border-color: var(--line);
            background: var(--surface);
            color: var(--ink);
        }

        div[data-testid="stTextArea"] textarea::placeholder,
        div[data-testid="stTextInput"] input::placeholder {
            color: var(--muted);
            opacity: 0.75;
        }

        div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
            background: var(--surface);
            border-color: var(--line);
            color: var(--ink);
        }

        div[data-testid="stSelectbox"] [data-baseweb="select"] span {
            color: var(--ink);
        }

        div[data-testid="stButton"] button {
            background: var(--card);
            border-radius: 8px;
            border: 1px solid var(--line);
            color: var(--ink);
            font-weight: 700;
        }

        div[data-testid="stButton"] button:hover {
            background: var(--surface);
            border-color: var(--accent) !important;
            color: var(--accent) !important;
        }

        div[data-testid="stButton"] button p,
        div[data-testid="stButton"] button span {
            color: inherit;
        }

        div[data-testid="stButton"] button[kind="primary"] {
            background: var(--accent);
            border-color: var(--accent);
            color: #141210;
        }

        div[data-testid="stButton"] button[kind="primary"]:hover {
            background: #9f4e2f;
            border-color: #9f4e2f;
            color: #fff;
        }

        .section-kicker {
            color: var(--muted);
            font-size: 0.86rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            margin-top: 0.5rem;
            text-transform: uppercase;
        }

        .result-card {
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 8px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            min-height: 148px;
            padding: 1.05rem 1.1rem;
        }

        .result-card h3 {
            color: var(--accent);
            font-size: 1rem;
            letter-spacing: 0 !important;
            margin: 0 0 0.55rem;
        }

        .result-card p {
            color: var(--ink);
            font-size: 0.98rem;
            line-height: 1.5;
            margin: 0;
            white-space: pre-wrap;
        }

        .share-card {
            background: #0e0c0b;
            border: 1px solid var(--line);
            border-radius: 8px;
            color: var(--ink);
            padding: 1rem 1.15rem;
            margin-top: 0.4rem;
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
        }

        .mode-note {
            border-left: 3px solid var(--accent);
            color: var(--muted);
            margin: 0.5rem 0 1rem;
            padding-left: 0.8rem;
        }

        label, .stSelectbox label, .stTextInput label, .stTextArea label {
            color: var(--muted) !important;
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
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_card(title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="result-card">
            <h3>{escape(title)}</h3>
            <p>{escape(body)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_results(fields: FieldList, response: Dict[str, str], share_key: str = "") -> None:
    if "model_status" in st.session_state:
        st.caption(st.session_state.model_status)

    for row in range(0, len(fields), 2):
        cols = st.columns(2)
        for col, (key, title) in zip(cols, fields[row : row + 2]):
            with col:
                render_card(title, response.get(key, ""))

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


def add_to_archive(mode: str, title: str, response: Dict[str, str]) -> None:
    if "archive_items" not in st.session_state:
        st.session_state.archive_items = []
    st.session_state.archive_items.insert(
        0,
        {
            "saved_at": datetime.now().isoformat(timespec="seconds"),
            "mode": mode,
            "title": title or mode,
            "response": response,
        },
    )


def archive_download() -> str:
    return json.dumps(st.session_state.get("archive_items", []), indent=2)


def common_context(prefix: str = "") -> Tuple[str, str, str]:
    background = st.text_input(
        "My background",
        value="Nepali / South Asian",
        key=f"{prefix}background",
    )
    audience = st.text_input(
        "Target audience",
        value="American coworkers or friends",
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
        index=0,
        key=f"{prefix}tone",
    )
    return background, audience, tone


def translator_mode() -> None:
    if "concept" not in st.session_state:
        st.session_state.concept = EXAMPLES[0]

    st.markdown('<div class="section-kicker">Demo examples</div>', unsafe_allow_html=True)
    example_cols = st.columns(4)
    for col, example in zip(example_cols, EXAMPLES):
        with col:
            if st.button(example, key=f"example-{example}", use_container_width=True):
                st.session_state.concept = example

    left, right = st.columns([1.1, 0.9], gap="large")
    with left:
        concept = st.text_area(
            "Cultural phrase or concept",
            key="concept",
            height=150,
            placeholder="Example: Why Nepali parents ask \"khana khayau?\" instead of saying \"I love you\"",
        )
    with right:
        background, audience, tone = common_context("translator_")

    if st.button("Translate the context", type="primary", use_container_width=True):
        final_concept = clean_concept(concept)
        with st.spinner("Translating the context..."):
            response = build_translator_response(final_concept, background, audience, tone)
        st.session_state.translator_response = response
        st.session_state.translator_title = final_concept
        add_to_archive("Context Translator", final_concept, response)

    if "translator_response" in st.session_state:
        st.markdown('<div class="section-kicker">Context translation</div>', unsafe_allow_html=True)
        render_results(TRANSLATOR_FIELDS, st.session_state.translator_response, "say_it_out_loud")


def copilot_mode() -> None:
    left, right = st.columns([1.05, 0.95], gap="large")
    with left:
        task = st.selectbox(
            "What are you making?",
            [
                "Slack or Teams message",
                "Email",
                "Speech or toast",
                "Social caption",
                "Classroom explanation",
                "Workplace time-off note",
            ],
        )
        context = st.text_area(
            "What cultural meaning do you need to communicate?",
            value="I want to explain why Dashain matters to me when I ask for time off.",
            height=160,
        )
    with right:
        background, audience, tone = common_context("copilot_")

    if st.button("Draft the message", type="primary", use_container_width=True):
        with st.spinner("Writing versions..."):
            response = build_copilot_response(task, context, background, audience, tone)
        st.session_state.copilot_response = response
        add_to_archive("Cultural Copilot", task, response)

    if "copilot_response" in st.session_state:
        st.markdown('<div class="section-kicker">Cultural copilot</div>', unsafe_allow_html=True)
        render_results(COPILOT_FIELDS, st.session_state.copilot_response, "best_version")


def misunderstanding_mode() -> None:
    left, right = st.columns([1.05, 0.95], gap="large")
    with left:
        concept = st.text_input("Cultural phrase or practice", value="Auntie culture")
        misunderstanding = st.text_area(
            "What did they misunderstand?",
            value="My coworker thought auntie culture just meant gossip.",
            height=140,
        )
    with right:
        background = st.text_input("My background", value="South Asian", key="mis_background")
        audience = st.text_input("Who misunderstood it?", value="Coworker", key="mis_audience")
        desired_outcome = st.selectbox(
            "What do you want?",
            [
                "Correct them kindly",
                "Explain without making it awkward",
                "Set a boundary",
                "Make it funny but respectful",
            ],
        )

    if st.button("Repair the misunderstanding", type="primary", use_container_width=True):
        with st.spinner("Building a repair response..."):
            response = build_misunderstanding_response(
                concept, misunderstanding, background, audience, desired_outcome
            )
        st.session_state.misunderstanding_response = response
        add_to_archive("Misunderstanding Resolver", concept, response)

    if "misunderstanding_response" in st.session_state:
        st.markdown('<div class="section-kicker">Misunderstanding repair</div>', unsafe_allow_html=True)
        render_results(MISUNDERSTANDING_FIELDS, st.session_state.misunderstanding_response, "respectful_reply")


def family_mode() -> None:
    left, right = st.columns([1.05, 0.95], gap="large")
    with left:
        situation = st.text_area(
            "Family situation",
            value="My mom keeps asking if I ate. I know she cares, but sometimes it feels like pressure.",
            height=145,
        )
        older_side = st.text_area(
            "Older generation or first person's side",
            value="She is trying to show care through food and checking in.",
            height=110,
        )
    with right:
        younger_side = st.text_area(
            "Younger generation or second person's side",
            value="I want to feel trusted and not monitored.",
            height=110,
        )
        background = st.text_input("Family background", value="Nepali / South Asian", key="family_background")
        goal = st.selectbox(
            "Conversation goal",
            [
                "Explain both sides",
                "Respond kindly",
                "Set a soft boundary",
                "Prepare for a hard conversation",
            ],
        )

    if st.button("Translate the family meaning", type="primary", use_container_width=True):
        with st.spinner("Translating both sides..."):
            response = build_family_response(situation, older_side, younger_side, background, goal)
        st.session_state.family_response = response
        add_to_archive("Family Translator", "Family translation", response)

    if "family_response" in st.session_state:
        st.markdown('<div class="section-kicker">Family translation</div>', unsafe_allow_html=True)
        render_results(FAMILY_FIELDS, st.session_state.family_response, "bridge_sentence")


def compare_mode() -> None:
    left, right = st.columns([1.05, 0.95], gap="large")
    with left:
        concept = st.text_input("Concept to explain", value="Dashain tika")
        target_familiarity = st.text_area(
            "What might the target audience already understand?",
            value="They understand Thanksgiving, Christmas family gatherings, and receiving blessings at major life events.",
            height=135,
        )
    with right:
        source_culture = st.text_input("Source culture", value="Nepali")
        target_culture = st.text_input("Target culture", value="American")

    if st.button("Compare the cultures", type="primary", use_container_width=True):
        with st.spinner("Finding bridges and differences..."):
            response = build_compare_response(concept, source_culture, target_culture, target_familiarity)
        st.session_state.compare_response = response
        add_to_archive("Compare Cultures", concept, response)

    if "compare_response" in st.session_state:
        st.markdown('<div class="section-kicker">Culture comparison</div>', unsafe_allow_html=True)
        render_results(COMPARE_FIELDS, st.session_state.compare_response, "explanation_for_target")


def archive_mode() -> None:
    if "archive_items" not in st.session_state:
        st.session_state.archive_items = []

    left, right = st.columns([1.05, 0.95], gap="large")
    with left:
        title = st.text_input("Archive title", value="Khana khayau?")
        memory = st.text_area(
            "Memory, ritual, saying, food, or tradition",
            value="My parents ask if I ate whenever they call, even when they do not say emotional things directly.",
            height=145,
        )
    with right:
        meaning = st.text_area(
            "Meaning you want preserved",
            value="It is a way of checking if I am okay and showing care through food.",
            height=110,
        )
        background = st.text_input("Family or cultural background", value="Nepali / South Asian")

    if st.button("Create archive entry", type="primary", use_container_width=True):
        with st.spinner("Preserving the memory..."):
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
            title_text = f"{item['title']} - {item['mode']}"
            body = item["response"].get("how_to_explain_it") or item["response"].get("say_it_out_loud") or item["response"].get("best_version") or next(iter(item["response"].values()), "")
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

    st.title(APP_TITLE)
    st.markdown(f'<div class="tagline">{TAGLINE}</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="intro">A cultural communication assistant for explaining meaning, repairing misunderstandings, comparing contexts, and preserving family memory.</div>',
        unsafe_allow_html=True,
    )

    mode = st.radio(
        "Mode",
        list(MODE_INTROS.keys()),
        horizontal=True,
        label_visibility="collapsed",
    )
    render_mode_note(mode)

    if mode == "Context Translator":
        translator_mode()
    elif mode == "Cultural Copilot":
        copilot_mode()
    elif mode == "Misunderstanding Resolver":
        misunderstanding_mode()
    elif mode == "Family Translator":
        family_mode()
    elif mode == "Compare Cultures":
        compare_mode()
    elif mode == "Personal Archive":
        archive_mode()


if __name__ == "__main__":
    main()
