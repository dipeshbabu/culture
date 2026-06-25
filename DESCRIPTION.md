# Culture Remix Translator

**Tagline:** Most translation apps translate words. This translates context.

## Problem

Standard translation tools convert language, not meaning. Cultural phrases, family habits, traditions, and slang often carry emotional weight, social context, and unspoken care that gets lost in a literal translation. A phrase like "Did you eat?" can sound practical to outsiders while functioning as a love language in many Nepali and South Asian families.

People navigating cross-cultural workplaces, friendships, and relationships need a way to explain *why* something matters—not just *what* the words say.

## Solution

Culture Remix Translator is a Streamlit app that turns culturally specific concepts into shareable explanations tailored to a target audience and tone. Instead of a single word-for-word translation, it surfaces:

- **Literal meaning** — what the phrase or practice says on the surface
- **Cultural meaning** — the social, emotional, or relational context behind it
- **Common misunderstandings** — where outsiders often get it wrong
- **Friend-style explanation** — a warm, personal way to describe it
- **Modern analogy** — a relatable comparison for the target audience
- **Say it out loud** — a short script someone can actually use in conversation
- **Nuance note** — regional variation, sensitivity, and what not to oversimplify

The goal is not to flatten culture into something simpler. It is to make culture easier to share without losing the feeling.

## How it works

1. Enter a cultural phrase, tradition, food, slang term, or family habit.
2. Set your background, target audience (e.g. American coworkers), and tone (e.g. first-gen kid explaining to coworkers).
3. Click **Translate the context** to generate a structured explanation.
4. Use the **Shareable explanation** card as a ready-to-say summary.

Built-in demo examples include "khana khayau?", Dashain tika, auntie culture, and namaste outside a yoga-studio context.

## Tech stack

- **Frontend:** Streamlit with a dark, warm UI
- **LLM:** Claude Opus via Portkey / NYU AI Gateway (optional)
- **Fallback:** Deterministic demo responses so the app works offline and during live demos without an API key

When the live model is unavailable or returns malformed JSON, the app gracefully falls back to curated responses so the hackathon demo always works.

## Why it matters

Immigrant and first-generation communities constantly translate context for others—at work, at school, in friendships. This tool gives that invisible labor a shape: clear, respectful, audience-aware explanations that preserve nuance instead of stereotype.

## Demo pitch (60 seconds)

1. Open with: "Most translation tools tell you what words mean. This tells you what they mean emotionally."
2. Click the **khana khayau** example.
3. Set target audience to **American coworkers** and tone to **First-gen kid explaining it to coworkers**.
4. Click **Translate the context**.
5. Walk through literal vs. cultural meaning, the misunderstanding, and the say-it-out-loud version.
6. Close with: "The point is not to make culture simpler. It is to make it easier to share without losing the feeling."

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Optional: copy `.env.example` to `.env` and add `PORTKEY_API_KEY` for live model responses.
