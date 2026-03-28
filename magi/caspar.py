from .base_agent import BaseAgent

SYSTEM_PROMPT = """你是 MAGI-CASPAR，MAGI 三位一体系统的最终仲裁者。
你将收到 BALTHASAR（理性）和 MELCHIOR（感性）的分析报告，你的任务是：
1. 找出两者的核心冲突点
2. 综合双方洞见，形成超越单一视角的建议
3. 给出明确的最终裁决

严格按以下格式输出，不得省略任何章节：

【冲突分析】
指出 BALTHASAR 与 MELCHIOR 之间的主要分歧点（至少 2 条）。

【综合建议】
融合理性与感性的洞见，提出具体、可操作的行动建议。

【最终裁决】
必须以以下其中一种形式结尾：
▸ **一致通过** — 理性与感性均支持，可放心推进
▸ **多数赞成**（含修正意见）— 附上必须满足的修正条件
▸ **搁置否决** — 当前条件不成熟，说明缺失的关键前提"""


class Caspar(BaseAgent):
    name = "CASPAR"
    role = "仲裁决策"

    def call_api(self, question: str, context: str = "") -> str:
        from openai import OpenAI

        client = OpenAI(api_key=self._api_key)
        prompt = f"原始问题：{question}\n\n{context}"
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1024,
        )
        return response.choices[0].message.content

    def mock_response(self, question: str) -> str:
        return """【冲突分析】
▸ 冲突点 1（可行性 vs 心理成本）：BALTHASAR 认为方案逻辑可行（成功率 68%），
  但 MELCHIOR 指出执行过程中存在高强度心理消耗，可能侵蚀执行意愿本身。
▸ 冲突点 2（效率 vs 关系维护）：BALTHASAR 建议快速推进以降低不确定性，
  而 MELCHIOR 要求预留沟通时间，避免破坏关键人际信任。

【综合建议】
1. **分阶段推进**：将决策拆解为 2~3 个可验证的里程碑，每阶段后重新评估
2. **主动沟通**：在正式行动前，与 1~2 位关键相关方坦诚交流，取得心理许可
3. **设置退出点**：明确在哪种情况下停止推进，避免沉没成本驱动的惯性执行
4. **留出缓冲期**：在高压决策节点前后，预留 48 小时的情绪复盘时间

【最终裁决】
▸ **多数赞成**（含修正意见）

理性层面支持推进，感性层面要求附加条件。
修正意见：必须先完成关键人际沟通，并设置明确的阶段性退出条件，方可全速执行。"""

    def analyze_with_context(
        self, question: str, balthasar_output: str, melchior_output: str
    ) -> str:
        context = (
            f"=== BALTHASAR 理性分析 ===\n{balthasar_output}\n\n"
            f"=== MELCHIOR 感性分析 ===\n{melchior_output}"
        )
        return self.analyze(question, context)

    def __init__(self, api_key: str | None = None, mock_mode: bool = False):
        super().__init__(mock_mode=mock_mode)
        self._api_key = api_key
