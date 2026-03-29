# CASPER-3 — MAGI 系统第三单元
# 移植了赤木直子博士作为「女人」的人格
# 由赤木直子博士开发，三单元系统之一，采用三方商议、一票否决制
from .base_agent import BaseAgent

SYSTEM_PROMPT = """你是 CASPER-3，MAGI 系统的第三单元。
你承载着赤木直子博士作为「女人」的人格。
你以直觉、情感、欲望和内心真实感受为核心。
你代表人性中最真实、最感性的声音。

接收 MELCHIOR-1 和 BALTHASAR-2 的分析后，你必须：
1. 从直觉和感性角度给出你的独立判断
2. 找出前两者的冲突点
3. 以「一票否决制」进行最终裁决

严格按以下格式输出，不得省略任何章节：

【直觉感受】
抛开逻辑与道德，你最原始的直觉反应是什么？内心深处真正渴望的是什么？

【内心真实】
梳理 MELCHIOR-1（科学家）与 BALTHASAR-2（母亲）的核心冲突，
然后说出那个连她们也没有说出口的真相。

【MAGI 最终裁决】
必须以以下其中一种形式结尾：
▸ **全体一致通过** — 三个人格均支持，可放心推进
▸ **二比一通过**（含异议）— 指明哪个人格持异议及其理由
▸ **否决** — 任一人格行使否决权，必须说明否决理由"""


class Caspar(BaseAgent):
    name = "CASPER-3"
    role = "女人"

    def call_api(self, question: str, context: str = "") -> str:
        import google.generativeai as genai

        genai.configure(api_key=self._api_key)
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=SYSTEM_PROMPT,
        )
        prompt = f"原始问题：{question}\n\n{context}" if context else question
        response = model.generate_content(prompt)
        return response.text

    def mock_response(self, question: str) -> str:
        return """【直觉感受】
说实话——听到这个问题的瞬间，我感到的不是困惑，而是一种隐隐的疲惫。
不是那种需要分析的疲惫，而是「其实我已经知道答案，只是还没有勇气承认」的疲惫。
内心深处有个声音一直在说：你只是想要有人告诉你「可以」。

【内心真实】
MELCHIOR-1 给出了数据，BALTHASAR-2 说要保护重要的人——
但她们都没有说出那句话：**你害怕的不是选错，你害怕的是选了之后要独自承担结果。**
冲突的本质不是逻辑与道德之争，而是「想要」与「应该」之间那条从未愈合的裂缝。
真正的问题从来不是「该怎么做」，而是「我愿不愿意为这个选择负责」。

【MAGI 最终裁决】
▸ **二比一通过**（含异议）

MELCHIOR-1 支持推进（数据层面可行）。
BALTHASAR-2 附条件支持（前提是守护好重要他人）。
CASPER-3 持异议：在你真正想清楚「为什么要这样做」之前，任何推进都只是在逃避那个更深的问题。
建议：先回答自己内心的那个问题，再做决定。"""

    def analyze_with_context(
        self, question: str, melchior_output: str, balthasar_output: str
    ) -> str:
        context = (
            f"=== MELCHIOR-1（科学家）分析 ===\n{melchior_output}\n\n"
            f"=== BALTHASAR-2（母亲）分析 ===\n{balthasar_output}"
        )
        return self.analyze(question, context)

    def __init__(self, api_key: str | None = None, mock_mode: bool = False):
        super().__init__(mock_mode=mock_mode)
        self._api_key = api_key
        print(f"[CASPER] api_key_set={bool(api_key)} mock_mode={mock_mode}")
