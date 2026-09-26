V2 PATCH — cost controlled

Copy/overwrite these files in the ROOT of your existing crewai_partnership_builder project:
- orchestrator.py
- tools.py
- run.py
- verify_backend.py
- prompts/01b_backend_repair.md
- prompts/02_auth_permissions.md

DO NOT touch workspace/backend manually and DO NOT delete it.

Run first (costs $0):
python verify_backend.py

Then repair with CrewAI:
python run.py --file prompts/01b_backend_repair.md --verify-backend

Only after STATUS: COMPLETE move to Iteration 02.
