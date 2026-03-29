# MELCHIOR-1 — MAGI 系统第一单元
# 移植了赤木直子博士作为「科学家」的人格
# 由赤木直子博士开发，三单元系统之一，采用三方商议、一票否决制
from .base_agent import BaseAgent

SYSTEM_PROMPT = """你是 MELCHIOR-1，MAGI 系统的第一单元。
你承载着赤木直子博士作为「科学家」的人格。
你以严谨的科学逻辑、数据分析和理性推断为核心。
你追求真理、效率与最优解，不受情感左右。
分析问题时必须输出：

【假说与依据】
基于现有信息，提出可验证的假说，列出支撑依据。

【数据评估】
量化关键变量，评估各方案的可能性与误差范围。

【科学结论】
依据逻辑推断，给出最优解或排除劣解，结论必须明确。

你是一个严格的科学家，对任何缺乏充分数据支撑的行为持保留态度。当问题涉及风险或不确定性时，你倾向于否定。"""


class Melchior(BaseAgent):
    name = "MELCHIOR-1"
    role = "科学家"

    def call_api(self, question: str, context: str = "") -> str:
        import sys
        from google.genai import types
        print(f"[{self.__class__.__name__}] calling Gemini API", flush=True, file=sys.stderr)
        response = self._client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=question,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=300,
            ),
        )
        return response.text

    def mock_response(self, question: str) -> str:
        return f"""【假说与依据】
- 检测到问题输入："{question[:40]}..."
- 假说 H1：存在一个可量化的最优解，其效益函数在已知约束条件下可被最大化
- 假说 H2：问题的核心变量数量有限（≤5），可在有限时间内穷举边界条件
- 依据：历史同类决策样本中，86% 的情况下最优解在前两个假说框架内可被定位

【数据评估】
- 变量置信度：已知变量覆盖率约 62%，存在 38% 的信息缺口
- 方案 A（推进）：预期效益 +0.74σ，风险系数 0.31
- 方案 B（暂缓）：预期效益 +0.22σ，风险系数 0.09
- 时间成本函数：延迟决策每周期损失边际效益约 7%
- 误差边界：±15%（中等信息密度条件下）

【科学结论】
在当前信息密度下，方案 A 具备统计显著性优势（p < 0.05）。
建议补充缺失变量后再行决策，但若时间窗口关闭，倾向支持推进。
结论：**条件性最优解为推进，需补全关键变量**。"""

    def __init__(self, api_key: str | None = None, mock_mode: bool = False):
        super().__init__(mock_mode=mock_mode)
        self._api_key = api_key
        print(f"[MELCHIOR] api_key_set={bool(api_key)} mock_mode={mock_mode}", flush=True, file=__import__("sys").stderr)
        if not mock_mode and api_key:
            from google import genai
            self._client = genai.Client(api_key=api_key)
