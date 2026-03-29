import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# 确保能 import 根目录下的 magi/ 包
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from magi import Balthasar, Caspar, Melchior

print(f"[MAGI BOOT] mock_mode={config.mock_mode} key_set={bool(config.google_api_key)}")

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
    """从 CASPER-3 输出中提取最终裁决，返回 '承認' 或 '否定'"""
    for line in casper_output.splitlines():
        if "否决" in line or "否定" in line:
            return "否定"
        if "全体一致通过" in line or "二比一通过" in line:
            return "承認"
    return "否定"


@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")

    # 每次请求时重新读取，防止 Vercel 模块缓存导致 config 过早固化
    google_key = os.environ.get("GOOGLE_API_KEY")
    mock = not bool(google_key)
    print(f"[MAGI REQUEST] mock={mock} key_set={bool(google_key)} key_prefix={google_key[:8] if google_key else 'None'}")

    melchior = Melchior(api_key=google_key, mock_mode=mock)
    balthasar = Balthasar(api_key=google_key, mock_mode=mock)
    casper = Caspar(api_key=google_key, mock_mode=mock)

    results: dict[str, str] = {}

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(melchior.analyze, req.question): "melchior",
            executor.submit(balthasar.analyze, req.question): "balthasar",
        }
        for fut in as_completed(futures):
            key = futures[fut]
            try:
                results[key] = fut.result()
            except Exception as e:
                results[key] = f"（分析失败：{e}）"

    try:
        casper_output = casper.analyze_with_context(
            req.question,
            results.get("melchior", ""),
            results.get("balthasar", ""),
        )
    except Exception as e:
        casper_output = f"（裁决失败：{e}）"

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
