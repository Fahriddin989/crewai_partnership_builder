from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "workspace" / "backend"


def run(command: list[str], timeout: int = 60) -> bool:
    print(f"> {' '.join(command)}", flush=True)

    try:
        proc = subprocess.run(
            command,
            cwd=BACKEND,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        print(f"[FAIL] Command timed out after {timeout}s", flush=True)
        return False

    if proc.stdout.strip():
        print(proc.stdout.strip(), flush=True)

    if proc.stderr.strip():
        print(proc.stderr.strip(), flush=True)

    return proc.returncode == 0


def main():
    failures = []

    if not (BACKEND / "manage.py").exists():
        print(f"[FAIL] manage.py missing: {BACKEND}")
        return 1

    print("\n1) Django system check", flush=True)

    if run([
        sys.executable,
        "manage.py",
        "check",
    ]):
        print("[PASS] Django check")
    else:
        failures.append("Django check")

    print("\n2) Migration consistency", flush=True)

    if run([
        sys.executable,
        "manage.py",
        "makemigrations",
        "--check",
        "--dry-run",
        "--noinput",
    ]):
        print("[PASS] No migration drift")
    else:
        print("[FAIL] Model changes are not fully migrated")
        failures.append("Migration drift")

    print("\n3) Django setup", flush=True)

    sys.path.insert(0, str(BACKEND))
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "config.settings",
    )

    try:
        import django

        django.setup()

        from django.test import Client

        from partnerships.models import (
            Organization,
            Agreement,
            Contact,
            AgreementContact,
            Document,
            Activity,
        )

        print("[PASS] Django app imports correctly")

    except Exception as exc:
        print(f"[FAIL] Django setup/import error: {exc}")
        failures.append("Django setup")

        print("\nSTATUS: INCOMPLETE")
        print("FAILURES:", ", ".join(failures))
        return 1

    print("\n4) Required model schema", flush=True)

    required = {
        Organization: {
            "name",
            "organization_type",
            "country",
            "website",
            "description",
            "is_public",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        },

        Agreement: {
            "organization",
            "title",
            "agreement_type",
            "status",
            "description",
            "signed_date",
            "start_date",
            "expiration_date",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        },

        Contact: {
            "full_name",
            "organization",
            "position",
            "email",
            "phone",
            "notes",
            "created_at",
            "updated_at",
        },

        AgreementContact: {
            "agreement",
            "contact",
            "side",
            "role",
            "is_primary",
        },

        Document: {
            "agreement",
            "title",
            "document_type",
            "file",
            "description",
            "uploaded_by",
            "uploaded_at",
        },

        Activity: {
            "agreement",
            "title",
            "activity_date",
            "description",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        },
    }

    for model, expected in required.items():

        actual = {
            field.name
            for field in model._meta.fields
        }

        missing = sorted(expected - actual)

        if missing:
            print(
                f"[FAIL] {model.__name__} missing fields: "
                f"{', '.join(missing)}"
            )
            failures.append(f"{model.__name__} schema")

        else:
            print(
                f"[PASS] {model.__name__} schema"
            )

    print("\n5) API permissions", flush=True)

    client = Client(HTTP_HOST="localhost")

    try:
        response = client.get(
            "/api/public/organizations/"
        )

        if response.status_code == 200:
            print(
                "[PASS] Public organizations endpoint"
            )
        else:
            print(
                f"[FAIL] Public endpoint returned "
                f"{response.status_code}"
            )
            failures.append("Public endpoint")

    except Exception as exc:
        print(
            f"[FAIL] Public endpoint exception: {exc}"
        )
        failures.append("Public endpoint")

    try:
        response = client.get(
            "/api/organizations/"
        )

        if response.status_code in (401, 403):
            print(
                "[PASS] Internal API blocks anonymous user"
            )
        else:
            print(
                f"[FAIL] Internal API returned "
                f"{response.status_code}"
            )
            failures.append(
                "Internal permissions"
            )

    except Exception as exc:
        print(
            f"[FAIL] Internal endpoint exception: {exc}"
        )
        failures.append(
            "Internal permissions"
        )

    print(
        "\n6) Public serializer safety",
        flush=True,
    )

    try:

        from partnerships.serializers import (
            PublicOrganizationSerializer,
        )

        actual = set(
            PublicOrganizationSerializer.Meta.fields
        )

        allowed = {
            "id",
            "name",
            "organization_type",
            "country",
            "website",
        }

        if actual == allowed:

            print(
                "[PASS] Public serializer exposes "
                "only safe fields"
            )

        else:

            print(
                "[FAIL] Public serializer fields:"
            )

            print(sorted(actual))

            print(
                "Expected:"
            )

            print(sorted(allowed))

            failures.append(
                "Public serializer"
            )

    except Exception as exc:

        print(
            f"[FAIL] Public serializer error: {exc}"
        )

        failures.append(
            "Public serializer"
        )

    print(
        "\n========== VERIFICATION SUMMARY =========="
    )

    if failures:

        print("\nSTATUS: INCOMPLETE")

        print("\nProblems:")

        for problem in failures:
            print(f" - {problem}")

        return 1

    print("\nSTATUS: COMPLETE")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())