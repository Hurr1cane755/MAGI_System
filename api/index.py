import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 确保能 import 根目录下的 magi/ 包
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from magi import Balthasar, Caspar, Melchior

app = FastAPI(title="MAGI-Link API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    question: str


class AnalyzeResponse(BaseModel):
    melchior: str
    balthasar: str
    casper: str
    verdict: str


def extract_verdict(casper_output: str) -> str:
    """从 CASPER-3 输出中提取最终裁决行"""
    for line in casper_output.splitlines():
        if "全体一致通过" in line or "二比一通过" in line or "否决" in line:
            return line.strip().lstrip("▸").strip()
    return "裁决结果解析失败"


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")

    melchior = Melchior(api_key=config.google_api_key, mock_mode=config.mock_mode)
    balthasar = Balthasar(api_key=config.anthropic_api_key, mock_mode=config.mock_mode)
    casper = Caspar(api_key=config.openai_api_key, mock_mode=config.mock_mode)

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

    return AnalyzeResponse(
        melchior=results.get("melchior", ""),
        balthasar=results.get("balthasar", ""),
        casper=casper_output,
        verdict=extract_verdict(casper_output),
    )


@app.get("/api/health")
async def health():
    return {"status": "online", "mock_mode": config.mock_mode}
