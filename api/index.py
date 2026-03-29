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

def log(*args):
    print(*args, flush=True, file=sys.stderr)

log(f"[MAGI BOOT] GOOGLE_API_KEY set={bool(os.environ.get('GOOGLE_API_KEY'))}")

app = FastAPI(title="MAGI-Link API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    question: str


def extract_first_word(text: str) -> str:
    lines = text.strip().splitlines()
    return lines[0].strip() if lines else ""


def run_agent(agent, question: str) -> str:
    name = agent.__class__.__name__
    log(f"[RUN_AGENT] {name} starting")
    try:
        return agent.analyze(question)
    except Exception as e:
        log(f"[ERROR] {name} failed: {type(e).__name__}: {e}")
        log(traceback.format_exc())
        return agent.mock_response(question)


@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest):
    log(f"[ANALYZE START] question={req.question[:20]!r}")

    if not req.question.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")

    google_key = os.environ.get("GOOGLE_API_KEY")
    mock = not bool(google_key)
    prefix = google_key[:8] if google_key else "NOT_SET"
    log(f"[MAGI REQUEST] mock={mock} key_prefix={prefix}")

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
                log(f"[ERROR] future {key}: {type(e).__name__}: {e}")
                log(traceback.format_exc())
                results[key] = f"（获取结果失败：{e}）"

    try:
        casper_output = casper.analyze_with_context(
            req.question,
            results.get("melchior", ""),
            results.get("balthasar", ""),
        )
    except Exception as e:
        log(f"[ERROR] Casper analyze_with_context: {type(e).__name__}: {e}")
        log(traceback.format_exc())
        casper_output = casper.mock_response(req.question)

    m_out = results.get("melchior", "")
    b_out = results.get("balthasar", "")

    melchior_vote = extract_first_word(m_out)
    balthasar_vote = extract_first_word(b_out)
    casper_vote = extract_first_word(casper_output)

    votes = [melchior_vote, balthasar_vote, casper_vote]
    reject_count = votes.count("拒绝")
    verdict = "否定" if reject_count >= 2 else "承認"

    log(f"[RESPONSE] melchior={m_out[:80]!r}")
    log(f"[RESPONSE] balthasar={b_out[:80]!r}")
    log(f"[RESPONSE] casper={casper_output[:80]!r}")
    log(f"[VOTES] melchior={melchior_vote!r} balthasar={balthasar_vote!r} casper={casper_vote!r}")
    log(f"[MAGI DONE] verdict={verdict} reject_count={reject_count} mock={mock}")

    return JSONResponse({
        "melchior": m_out,
        "balthasar": b_out,
        "casper": casper_output,
        "melchior_vote": melchior_vote,
        "balthasar_vote": balthasar_vote,
        "casper_vote": casper_vote,
        "verdict": verdict,
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
