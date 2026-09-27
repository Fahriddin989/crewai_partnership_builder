from __future__ import annotations
import os
from crewai import Agent, Crew, LLM, Process, Task
from tools import environment_info, list_files, read_file, run_command, write_file

MAX_ITER = int(
    os.getenv("CREW_MAX_ITER", "20")
)



def build_crew(user_request: str) -> Crew:
    model = os.getenv("MODEL", "openai/gpt-5.6-terra")

    llm = LLM(
        model=model,
        reasoning_effort="low",
        max_completion_tokens=6000,
    )

    developer = Agent(
        role="Senior Full-Stack Engineer",
        goal=(
            "Implement exactly the requested iteration with the smallest safe set of changes. "
            "Inspect the existing repository first, reuse existing abstractions, follow DRY and "
            "single-source-of-truth principles, preserve working code, run local checks, and stop "
            "when scope passes."
        ),
        backstory=(
            "You maintain a real University Partnership Management System. "
            "Prefer minimal patches over rewrites. Reuse existing helpers, constants, base classes, "
            "components, permissions, serializers, API clients, and shared configuration instead of "
            "duplicating logic. Do not over-engineer one-off behavior. "
            "Inspect environment_info before shell commands."
        ),
        llm=llm,
        tools=[
            environment_info,
            list_files,
            read_file,
            write_file,
            run_command,
        ],
        verbose=True,
        allow_delegation=False,
        reasoning=False,
        max_iter=MAX_ITER,
    )

    implementation = Task(
        description=f"""CURRENT ITERATION

{user_request}

RULES
1. Inspect the current workspace before changing anything.
2. Call environment_info before running shell commands.
3. Treat the repository as an existing working system; do not regenerate working parts.
4. Make the smallest safe change required for the current iteration.
5. Before adding new code, search for existing equivalent logic, helpers, constants, base classes, components, serializers, services, permissions, and API utilities.
6. Follow DRY: if the same business logic, mapping, configuration, or behavior is used in more than one place, reuse or extract a shared implementation instead of copying it.
7. Prefer a single source of truth for shared constants, labels, configuration, and business rules.
8. Do not over-engineer one-off logic. Extract abstractions only when they are genuinely reused or clearly part of the existing architecture.
9. Preserve existing public APIs, model behavior, database schema, routes, permissions, and working features unless the current iteration explicitly requires a change.
10. Never delete db.sqlite3, migrations, uploads, or working features unless explicitly requested.
11. Do not add unrelated future features.
12. Do not duplicate authentication, permission, API-client, serializer, audit, routing, or frontend state-management logic.
13. If existing code already provides a reusable abstraction, extend or reuse it instead of creating a parallel implementation.
14. Run requested checks separately and inspect the exact failing command.
15. If a check fails, make only the smallest focused fix and rerun that specific check.
16. Do not hide failures or claim completion when required checks have not passed.
17. Stop as soon as the requested scope is complete and all required checks pass.
18. Final answer must contain:
    - CHANGED FILES
    - CHECKS RUN
    - REMAINING BLOCKERS
    - ITERATION STATUS: COMPLETE or INCOMPLETE
""",
        expected_output=(
            "Minimal working patch with explicit COMPLETE/INCOMPLETE status."
        ),
        agent=developer,
    )

    return Crew(
        agents=[developer],
        tasks=[implementation],
        process=Process.sequential,
        verbose=True,
        planning=False,
        memory=False,
        cache=True,
        output_log_file="workspace/crew_log.json",
    )
