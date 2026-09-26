from __future__ import annotations
import os
from crewai import Agent, Crew, LLM, Process, Task
from tools import environment_info, list_files, read_file, run_command, write_file


def build_crew(user_request: str) -> Crew:
    model = os.getenv("MODEL", "openai/gpt-5.6-terra")
    llm = LLM(model=model, reasoning_effort="low", max_completion_tokens=6000)
    developer = Agent(
        role="Senior Full-Stack Engineer",
        goal=("Implement exactly the requested iteration with the smallest safe set of changes. "
              "Inspect the existing repository first, preserve working code, run local checks, and stop when scope passes."),
        backstory=("You maintain a real University Partnership Management System. Prefer minimal patches over rewrites. "
                   "Inspect environment_info before shell commands."),
        llm=llm,
        tools=[environment_info, list_files, read_file, write_file, run_command],
        verbose=True,
        allow_delegation=False,
        reasoning=False,
        max_iter=12,
    )
    implementation = Task(
        description=f'''CURRENT ITERATION\n\n{user_request}\n\nRULES\n1. Inspect current workspace first.\n2. Use environment_info before shell commands.\n3. Existing repository: do not regenerate working parts.\n4. Make the minimum changes required.\n5. Never delete db.sqlite3, migrations, uploads, or working features unless explicitly requested.\n6. Do not add unrelated future features.\n7. Run requested checks.\n8. If a check fails, make a focused fix and rerun it.\n9. Stop when scope passes.\n10. Final answer: CHANGED FILES, CHECKS RUN, REMAINING BLOCKERS, ITERATION STATUS: COMPLETE/INCOMPLETE.''',
        expected_output="Minimal working patch with explicit COMPLETE/INCOMPLETE status.",
        agent=developer,
    )
    return Crew(
        agents=[developer], tasks=[implementation], process=Process.sequential,
        verbose=True, planning=False, memory=False, cache=True,
        output_log_file="workspace/crew_log.json",
    )
