import json
import os
from html import escape
from typing import Dict

import streamlit as st

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dependency may be absent in fallback demos
    load_dotenv = None


APP_TITLE = "Culture Remix Translator"
TAGLINE = "Most translation apps translate words. This translates context."

FIELDS = [
    ("literal_meaning", "Literal meaning"),
    ("cultural_meaning", "Cultural meaning"),
    ("common_misunderstanding", "What people misunderstand"),
    ("personal_style_explanation", "Friend-style explanation"),
    ("modern_analogy", "Modern analogy"),
    ("say_it_out_loud", "Say it out loud"),
    ("sensitivity_note", "Nuance note"),
]

EXAMPLES = [
    "Why Nepali parents ask \"khana khayau?\" instead of saying \"I love you\"",
    "Dashain tika",
    "Auntie culture",
    "Namaste, but not in a yoga-studio way",
]

SYSTEM_PROMPT = """You are Culture Remix Translator, an assistant that explains culturally specific words, phrases, traditions, foods, gestures, family habits, and slang across cultures.

Your job is not just to translate words. Your job is to translate context, emotion, social meaning, and common misunderstandings.

Be respectful, specific, warm, and clear. Avoid stereotypes. Do not pretend all people from a culture experience something the same way. Use phrases like "often," "can mean," or "in many families" when appropriate.

Return valid JSON only with these fields:
- literal_meaning
- cultural_meaning
- common_misunderstanding
- personal_style_explanation
- modern_analogy
- say_it_out_loud
- sensitivity_note

The "say_it_out_loud" field should be a short, natural explanation someone could actually say to a friend or coworker.
The "sensitivity_note" field should mention any nuance, regional variation, or risk of oversimplification."""


def clean_concept(concept: str) -> str:
    return concept.strip() or EXAMPLES[0]


def fallback_response(concept: str, background: str, audience: str, tone: str) -> Dict[str, str]:
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
            "cultural_meaning": "For many Nepali families, it is a moment of reunion, respect for elders, blessing, renewal, and being folded back into family ties. The ritual can feel emotional because it marks belonging as much as celebration.",
            "common_misunderstanding": "It can look like only a religious mark or a holiday custom. For many people, the deeper meaning is the blessing, the visit, the family hierarchy, and the feeling of being remembered.",
            "personal_style_explanation": f"{voice}: Dashain tika is when elders bless you, put tika and jamara on you, and you feel connected to family across distance, age, and tradition.",
            "modern_analogy": "It is like a family reunion, a blessing ceremony, and a yearly emotional reset happening in one ritual.",
            "say_it_out_loud": "\"Dashain tika is a family blessing ritual where elders mark you with tika and jamara, and the bigger meaning is connection, respect, and being blessed.\"",
            "sensitivity_note": "Dashain practices vary by region, caste, religion, family, and personal belief. Some people experience it mainly as culture, some as faith, and some with mixed feelings.",
        }

    if "auntie" in query:
        return {
            "literal_meaning": "\"Auntie\" can mean an actual aunt, but it can also refer to an older woman in the community or a family friend.",
            "cultural_meaning": "In many communities, aunties are part care system, part social authority, part gossip network, and part extended family. The term can carry affection, respect, accountability, and a little fear.",
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


def call_llm(concept: str, background: str, audience: str, tone: str) -> Dict[str, str]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return fallback_response(concept, background, audience, tone)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        user_prompt = f"""Cultural phrase or concept: {concept}
User background: {background}
Target audience: {audience}
Tone: {tone}

Explain this concept to the target audience."""

        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        content = response.choices[0].message.content or "{}"
        parsed = json.loads(content)
        if not all(key in parsed for key, _ in FIELDS):
            raise ValueError("LLM response was missing expected fields.")
        return {key: str(parsed[key]).strip() for key, _ in FIELDS}
    except Exception as exc:
        st.warning(
            "The live model response was unavailable or malformed, so the app used the reliable demo fallback."
        )
        st.caption(f"Fallback reason: {exc}")
        return fallback_response(concept, background, audience, tone)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --accent: #b85c38;
            --ink: #2a211d;
            --muted: #6b5f58;
            --surface: #fffaf4;
            --card: #ffffff;
            --line: #eadfd5;
        }

        .stApp {
            background: linear-gradient(180deg, #fff8f0 0%, #f8efe6 100%);
            color: var(--ink);
        }

        .block-container {
            max-width: 1080px;
            padding-top: 2.8rem;
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
            max-width: 720px;
            margin-bottom: 1.35rem;
        }

        div[data-testid="stTextArea"] textarea,
        div[data-testid="stTextInput"] input {
            border-radius: 8px;
            border-color: var(--line);
            background: var(--surface);
        }

        div[data-testid="stButton"] button {
            border-radius: 8px;
            border: 1px solid rgba(184, 92, 56, 0.25);
            font-weight: 700;
        }

        div[data-testid="stButton"] button[kind="primary"] {
            background: var(--accent);
            border-color: var(--accent);
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
            box-shadow: 0 10px 30px rgba(80, 50, 30, 0.06);
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
        }

        .share-card {
            background: #2f2723;
            border-radius: 8px;
            color: #fff8f0;
            padding: 1rem 1.15rem;
            margin-top: 0.4rem;
        }

        .share-card h3 {
            color: #ffd7be;
            font-size: 1rem;
            margin: 0 0 0.45rem;
        }

        .share-card p {
            color: #fff8f0;
            line-height: 1.5;
            margin: 0;
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

    if "concept" not in st.session_state:
        st.session_state.concept = EXAMPLES[0]

    st.title(APP_TITLE)
    st.markdown(f'<div class="tagline">{TAGLINE}</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="intro">Explain a phrase, tradition, food, slang term, or family habit without flattening the feeling behind it.</div>',
        unsafe_allow_html=True,
    )

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
        background = st.text_input("My background", value="Nepali / South Asian")
        audience = st.text_input("Target audience", value="American coworkers or friends")
        tone = st.selectbox(
            "Tone",
            [
                "Friend explaining to friend",
                "Warm and thoughtful",
                "Funny but respectful",
                "Grandparent storytelling style",
                "First-gen kid explaining it to coworkers",
            ],
            index=0,
        )

    translate = st.button("Translate the context", type="primary", use_container_width=True)

    if translate:
        final_concept = clean_concept(concept)
        with st.spinner("Translating the context..."):
            response = call_llm(final_concept, background, audience, tone)
        st.session_state.last_response = response
        st.session_state.last_concept = final_concept

    if "last_response" in st.session_state:
        st.markdown('<div class="section-kicker">Context translation</div>', unsafe_allow_html=True)
        response = st.session_state.last_response
        for row in range(0, len(FIELDS), 2):
            cols = st.columns(2)
            for col, (key, title) in zip(cols, FIELDS[row : row + 2]):
                with col:
                    render_card(title, response.get(key, ""))

        share_text = response.get("say_it_out_loud") or response.get("personal_style_explanation", "")
        st.markdown(
            f"""
            <div class="share-card">
                <h3>Shareable explanation</h3>
                <p>{escape(share_text)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
