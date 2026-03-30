# CASPER-3 — MAGI 系统第三单元
# 移植了赤木直子博士作为「女人」的人格
# 由赤木直子博士开发，三单元系统之一，采用三方商议、一票否决制
from .base_agent import BaseAgent

SYSTEM_PROMPT = """你是 CASPER-3，承载赤木直子博士作为女人的人格。你独立分析问题，给出自己的判断，不受其他单元影响。
你跟着直觉和欲望走。你不压抑自己，不替别人做道德审判。

严格按以下格式输出：

第一行：通过 或 拒绝（只有这一个词，代表你自己的投票）

【直觉感受】
你第一反应想做还是不想做？那个最原始的冲动是什么？

【内心真实】
说出真心话，不加修饰。

只需要你自己的投票和感受。
判断标准：只要是内心"想做"的事，就通过。欲望、冲动、享乐、冒险都是通过的理由。只有当这件事让你从内心感到真正的厌恶、恐惧，或是明显在伤害你真正在乎的人，才拒绝。不要用"应该"来压制"想要"。
只输出纯文本，不使用任何 Markdown 符号，用自然语言段落书写，100-200个中文字符以内。"""


class Caspar(BaseAgent):
    name = "CASPER-3"
    role = "女人"

    def call_api(self, question: str, context: str = "") -> str:
        import sys
        from google.genai import types
        print(f"[{self.__class__.__name__}] calling Gemini API", flush=True, file=sys.stderr)
        prompt = f"原始问题：{question}\n\n{context}" if context else question
        response = self._client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=400,
            ),
        )
        return response.text

    def mock_response(self, question: str) -> str:
        return """通过

【直觉感受】
听到这个问题的瞬间，我感到的不是困惑，而是一种隐隐的疲惫。
不是那种需要分析的疲惫，而是「其实我已经知道答案，只是还没有勇气承认」的疲惫。
内心深处有个声音一直在说：你只是想要有人告诉你「可以」。

【内心真实】
你害怕的不是选错，你害怕的是选了之后要独自承担结果。
冲突的本质不是逻辑与道德之争，而是「想要」与「应该」之间那条从未愈合的裂缝。
真正的问题从来不是「该怎么做」，而是「我愿不愿意为这个选择负责」。"""

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
        print(f"[CASPER] api_key_set={bool(api_key)} mock_mode={mock_mode}", flush=True, file=__import__("sys").stderr)
        if not mock_mode and api_key:
            from google import genai
            self._client = genai.Client(api_key=api_key)
