from __future__ import annotations
import os, platform, subprocess, sys
from pathlib import Path
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

WORKSPACE = Path(__file__).resolve().parent / "workspace"
WORKSPACE.mkdir(parents=True, exist_ok=True)

def safe_path(relative_path: str) -> Path:
    candidate = (WORKSPACE / relative_path).resolve()
    root = WORKSPACE.resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError("Path escapes workspace")
    return candidate

class EmptyInput(BaseModel):
    pass

class EnvironmentInfoTool(BaseTool):
    name: str = "environment_info"
    description: str = "Return OS, Python executable, workspace and shell guidance. Call before shell commands."
    args_schema: Type[BaseModel] = EmptyInput
    def _run(self) -> str:
        system = platform.system()
        note = ("Windows cmd.exe semantics: use cd, dir, &&; do not use pwd/ls/rm/touch." if system == "Windows"
                else "POSIX shell commands are available.")
        return f"OS={system}\nPYTHON={sys.executable}\nWORKSPACE={WORKSPACE}\nSHELL_GUIDANCE={note}"

class FilePathInput(BaseModel):
    path: str = Field(..., description="Relative path inside workspace/")

class ReadFileTool(BaseTool):
    name: str = "read_file"
    description: str = "Read a UTF-8 text file from workspace."
    args_schema: Type[BaseModel] = FilePathInput
    def _run(self, path: str) -> str:
        target = safe_path(path)
        if not target.exists(): return f"ERROR: {path} does not exist"
        if target.is_dir(): return f"ERROR: {path} is a directory"
        return target.read_text(encoding="utf-8", errors="replace")

class WriteFileInput(BaseModel):
    path: str
    content: str

class WriteFileTool(BaseTool):
    name: str = "write_file"
    description: str = "Create/overwrite UTF-8 file in workspace. Inspect an existing file before overwriting it."
    args_schema: Type[BaseModel] = WriteFileInput
    def _run(self, path: str, content: str) -> str:
        target = safe_path(path); target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"WROTE {path} ({len(content)} chars)"

class ListFilesInput(BaseModel):
    path: str = "."
    max_entries: int = Field(300, ge=1, le=2000)

class ListFilesTool(BaseTool):
    name: str = "list_files"
    description: str = "List files recursively in workspace."
    args_schema: Type[BaseModel] = ListFilesInput
    def _run(self, path: str = ".", max_entries: int = 300) -> str:
        base = safe_path(path)
        if not base.exists(): return f"ERROR: {path} does not exist"
        if base.is_file(): return str(base.relative_to(WORKSPACE))
        rows=[]
        for item in sorted(base.rglob("*")):
            rel=item.relative_to(WORKSPACE)
            if any(part in {".git",".venv","node_modules","__pycache__"} for part in rel.parts): continue
            rows.append(str(rel) + ("/" if item.is_dir() else ""))
            if len(rows)>=max_entries: rows.append("... truncated ..."); break
        return "\n".join(rows) if rows else "(workspace is empty)"

class CommandInput(BaseModel):
    command: str
    timeout: int = Field(180, ge=1, le=600)

class RunCommandTool(BaseTool):
    name: str = "run_command"
    description: str = f"Run local dev command from workspace on {platform.system()}. Use environment_info first."
    args_schema: Type[BaseModel] = CommandInput
    def _run(self, command: str, timeout: int = 180) -> str:
        blocked=["sudo ","rm -rf /","rm -rf ~","mkfs","shutdown","reboot","format c:","del /s /q c:\\",":(){"]
        if any(x.lower() in command.lower() for x in blocked): return "ERROR: command blocked"
        try:
            r = subprocess.run(
                command,
                cwd=WORKSPACE,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=os.environ.copy(),
                stdin=subprocess.DEVNULL,
            )
        except subprocess.TimeoutExpired:
            return f"ERROR: timed out after {timeout}s"
        return f"EXIT_CODE={r.returncode}\n--- STDOUT ---\n{(r.stdout or '')[-12000:]}\n--- STDERR ---\n{(r.stderr or '')[-12000:]}"

environment_info=EnvironmentInfoTool(); read_file=ReadFileTool(); write_file=WriteFileTool(); list_files=ListFilesTool(); run_command=RunCommandTool()
