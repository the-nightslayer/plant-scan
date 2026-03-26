# PlantScan AI (Streamlit)

Upload a plant photo and get an AI-powered identification + garden/health tips.

## Run locally

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set your Groq API key (PowerShell):

```powershell
$env:GROQ_API_KEY="YOUR_KEY_HERE"
```

3. Start the app:

```bash
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

- Add `GROQ_API_KEY` in your app’s **Secrets**.
- Set the app entrypoint to `app.py`.

## Notes

- History is written to `data/history.json` when running locally. On Streamlit Cloud, filesystem persistence isn’t guaranteed across restarts, so use the in-app download button to export your history.
