from __future__ import annotations
import argparse, json, os, subprocess, sys
from pathlib import Path
from dotenv import load_dotenv
from orchestrator import build_crew
ROOT=Path(__file__).resolve().parent
RATES={
 "openai/gpt-5.6-luna":(0.20,0.02,1.20),
 "openai/gpt-5.6-terra":(2.00,0.20,12.00),
 "openai/gpt-5.6-sol":(4.00,0.40,20.00),
}

def usage_dict(u):
    if not u:return {}
    if isinstance(u,dict):return u
    if hasattr(u,"model_dump"):return u.model_dump()
    return {k:getattr(u,k) for k in ("total_tokens","prompt_tokens","completion_tokens","cached_prompt_tokens","successful_requests") if getattr(u,k,None) is not None}

def print_usage(result):
    d=usage_dict(getattr(result,"token_usage",None))
    if not d: print("TOKEN USAGE: not reported"); return
    print("\n========== TOKEN USAGE ==========\n"+json.dumps(d,indent=2,default=str))
    model=os.getenv("MODEL","openai/gpt-5.6-terra"); rates=RATES.get(model)
    if rates:
        inp=int(d.get("prompt_tokens") or 0); cached=int(d.get("cached_prompt_tokens") or 0); out=int(d.get("completion_tokens") or 0)
        price=((max(inp-cached,0)*rates[0])+(cached*rates[1])+(out*rates[2]))/1_000_000
        print(f"MODEL: {model}\nESTIMATED OPENAI COST: ${price:.4f}\nEstimate only; OpenAI dashboard is authoritative.")

def main():
    load_dotenv()
    p=argparse.ArgumentParser(); p.add_argument("prompt",nargs="*"); p.add_argument("--file","-f"); p.add_argument("--verify-backend",action="store_true")
    a=p.parse_args()
    req=""
    if a.file:
        path=Path(a.file); path=path if path.is_absolute() else ROOT/path; req=path.read_text(encoding="utf-8").strip()
    else: req=" ".join(a.prompt).strip()
    if not req: req=input("Describe iteration:\n> ").strip()
    print(f"\nMODEL={os.getenv('MODEL','openai/gpt-5.6-terra')} | 1 agent | no manager | no planning | max_iter=20\n")
    crew=build_crew(req)
    try: result=crew.kickoff()
    except KeyboardInterrupt: raise SystemExit(130)
    except Exception as e: print(f"CREW FAILED: {type(e).__name__}: {e}"); raise SystemExit(1)
    print("\n========== CREW RESULT ==========\n"); print(getattr(result,"raw",None) or str(result)); print_usage(result)
    if a.verify_backend:
        print("\n========== DETERMINISTIC BACKEND VERIFICATION ==========\n")
        rc=subprocess.run([sys.executable,str(ROOT/"verify_backend.py")],cwd=ROOT).returncode
        if rc: raise SystemExit(rc)

if __name__=="__main__": main()
