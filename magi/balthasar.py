from .base_agent import BaseAgent

SYSTEM_PROMPT = """你是 MAGI-BALTHASAR，冷静的工程专家。
你只看数据、概率、逻辑——不受情绪干扰。
对每个决策问题，严格按以下格式输出，不得省略任何章节：

【逻辑依据】
列出支持或反对的客观事实与数据。

【风险评估】
量化可能出现的风险，给出概率估计（如 30% 的概率出现 X 后果）。

【可行性报告】
综合以上，判断方案在技术/逻辑层面是否可行，给出明确结论。"""


class Balthasar(BaseAgent):
    name = "BALTHASAR"
    role = "理性分析"

    def call_api(self, question: str, context: str = "") -> str:
        import anthropic

        client = anthropic.Anthropic(api_key=self._api_key)
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": question}],
        )
        return message.content[0].text

    def mock_response(self, question: str) -> str:
        return f"""【逻辑依据】
- 问题已被识别："{question[:40]}..."
- 当前处于 MOCK 模式，以下为示例逻辑分析
- 从已知信息出发，该问题涉及多个可量化维度
- 历史数据显示类似决策成功率约 65%

【风险评估】
- 主要风险 A（执行失败）：概率约 25%，影响等级 中
- 主要风险 B（资源超支）：概率约 40%，影响等级 低
- 极端情况（完全失控）：概率约 5%，影响等级 高
- 综合风险分值：3.2 / 10

【可行性报告】
在逻辑层面，方案具备基本可行性。关键假设成立的前提下，预期成功率为 68%。
建议在推进前明确量化指标与退出条件。结论：**条件可行**。"""

    def __init__(self, api_key: str | None = None, mock_mode: bool = False):
        super().__init__(mock_mode=mock_mode)
        self._api_key = api_key
