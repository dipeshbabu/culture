# Culture Remix Translator

Culture Remix Translator is a Streamlit hackathon MVP for explaining cultural phrases, traditions, foods, slang, and family habits with context and nuance.

Tagline: Most translation apps translate words. This translates context.

## Run locally

```powershell
pip install -r requirements.txt
streamlit run app.py
```

The app works without an API key by using deterministic demo fallbacks for the built-in examples.

## Optional live model

Copy `.env.example` to `.env` and set:

```text
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

## Demo flow

1. Open with: "Most translation tools tell you what words mean. This tells you what they mean emotionally."
2. Click: `Why Nepali parents ask "khana khayau?" instead of saying "I love you"`
3. Set target audience to `American coworkers`
4. Set tone to `First-gen kid explaining it to coworkers`
5. Click `Translate the context`
6. Point out the literal meaning, deeper cultural meaning, misunderstanding, modern analogy, and say-it-out-loud version.
7. End with: "The point is not to make culture simpler. It is to make it easier to share without losing the feeling."
