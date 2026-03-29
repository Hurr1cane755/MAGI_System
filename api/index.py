import os
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from magi import Balthasar, Caspar, Melchior

print(f"[MAGI BOOT] GOOGLE_API_KEY set={bool(os.environ.get('GOOGLE_API_KEY'))}")

app = FastAPI(title="MAGI-Link API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    question: str


def extract_verdict(casper_output: str) -> str:
    for line in casper_output.splitlines():
        if "否决" in line or "否定" in line:
            return "否定"
        if "全体一致通过" in line or "二比一通过" in line:
            return "承認"
    return "否定"


def run_agent(agent, question: str) -> str:
    """运行 agent，出错时打印完整异常并 fallback 到 mock"""
    name = agent.__class__.__name__
    try:
        return agent.analyze(question)
    except Exception as e:
        print(f"[ERROR] {name} failed: {type(e).__name__}: {e}")
        print(traceback.format_exc())
        return agent.mock_response(question)


@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")

    google_key = os.environ.get("GOOGLE_API_KEY")
    mock = not bool(google_key)
    prefix = google_key[:8] if google_key else "NOT_SET"
    print(f"[MAGI REQUEST] mock={mock} key_prefix={prefix} question={req.question[:40]!r}")

    melchior = Melchior(api_key=google_key, mock_mode=mock)
    balthasar = Balthasar(api_key=google_key, mock_mode=mock)
    casper    = Caspar(api_key=google_key, mock_mode=mock)

    results: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(run_agent, melchior, req.question): "melchior",
            executor.submit(run_agent, balthasar, req.question): "balthasar",
        }
        for fut in as_completed(futures):
            key = futures[fut]
            try:
                results[key] = fut.result()
            except Exception as e:
                print(f"[ERROR] future {key}: {type(e).__name__}: {e}")
                print(traceback.format_exc())
                results[key] = f"（获取结果失败：{e}）"

    try:
        casper_output = casper.analyze_with_context(
            req.question,
            results.get("melchior", ""),
            results.get("balthasar", ""),
        )
    except Exception as e:
        print(f"[ERROR] Casper analyze_with_context: {type(e).__name__}: {e}")
        print(traceback.format_exc())
        casper_output = casper.mock_response(req.question)

    print(f"[MAGI DONE] verdict={extract_verdict(casper_output)} mock={mock}")

    return JSONResponse({
        "melchior": results.get("melchior", ""),
        "balthasar": results.get("balthasar", ""),
        "casper": casper_output,
        "verdict": extract_verdict(casper_output),
        "debug_mode": "mock" if mock else "real",
        "debug_key_set": bool(google_key),
    })


@app.get("/api/health")
async def health():
    google_key = os.environ.get("GOOGLE_API_KEY")
    return {
        "status": "online",
        "mock_mode": not bool(google_key),
        "key_set": bool(google_key),
        "key_prefix": google_key[:8] if google_key else "not set",
        "env_keys": [k for k in os.environ if "KEY" in k or "API" in k],
    }
