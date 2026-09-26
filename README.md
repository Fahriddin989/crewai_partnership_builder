# CrewAI Partnership Builder

Step-by-step vibe coding for a University Partnership Management System.

## Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set your OpenAI key:

```env
OPENAI_API_KEY=sk-...
MODEL=openai/gpt-5.6-terra
```

Run the first iteration:

```powershell
python run.py --file prompts/01_backend_foundation.md
```

Generated project files will appear in `workspace/`.
