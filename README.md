# Culture Remix Translator

Culture Remix Translator is a Streamlit app for explaining cultural phrases, traditions, foods, slang, and family habits with context and nuance.

Tagline: Most translation apps translate words. This translates context.

The app has six modes:

- Context Translator: explains literal meaning, cultural meaning, misunderstandings, analogies, and a say-it-out-loud version.
- Cultural Copilot: drafts messages, emails, captions, speeches, and workplace notes that keep the cultural feeling intact.
- Misunderstanding Resolver: helps repair moments where someone misunderstood a cultural practice or phrase.
- Family Translator: translates between generations, especially immigrant parents, elders, first-gen kids, and family members.
- Compare Cultures: explains one cultural concept through another culture's familiar reference points.
- Personal Archive: turns family sayings, rituals, food memories, and traditions into saved archive entries.

## Run locally

```powershell
pip install -r requirements.txt
streamlit run app.py
```

The app works without an API key by using deterministic fallbacks for every mode.

## Optional live model

Copy `.env.example` to `.env` and set:

```text
PORTKEY_API_KEY=your_key_here
PORTKEY_BASE_URL=https://ai-gateway.apps.cloud.rt.nyu.edu/v1
PORTKEY_MODEL=@vertexai/anthropic.claude-opus-4-6
PORTKEY_MAX_TOKENS=2048
PORTKEY_TIMEOUT_SECONDS=90
```

When these values are present, the app calls Claude Opus through Portkey. If the gateway is unavailable or returns malformed JSON, the app falls back to deterministic responses so the demo still works. The result area shows whether the app used the live model or fallback.

## Demo flow

1. Open with: "Most translation tools tell you what words mean. This tells you what they mean emotionally."
2. Click: `Why Nepali parents ask "khana khayau?" instead of saying "I love you"`
3. Set target audience to `American coworkers`
4. Set tone to `First-gen kid explaining it to coworkers`
5. Click `Translate the context`
6. Point out the literal meaning, deeper cultural meaning, misunderstanding, modern analogy, and say-it-out-loud version.
7. Switch to Cultural Copilot or Family Translator to show that the app goes beyond definition and helps with real communication.
8. End with: "The point is not to make culture simpler. It is to make it easier to share without losing the feeling."
