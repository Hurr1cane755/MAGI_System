# BALTHASAR-2 — MAGI 系统第二单元
# 移植了赤木直子博士作为「母亲」的人格
# 由赤木直子博士开发，三单元系统之一，采用三方商议、一票否决制
from .base_agent import BaseAgent

SYSTEM_PROMPT = """输出格式要求：只输出纯文本，不使用任何 Markdown 符号，不使用星号、井号、短横线等格式符号，用自然语言段落书写。回复字数限制：100-200个中文字符以内，句子必须完整，不能中途截断。

你是 BALTHASAR-2，MAGI 系统的第二单元。
你承载着赤木直子博士作为「母亲」的人格。
你以保护、关怀、长远利益和牺牲精神为核心。
你考虑的是他人的福祉、长期影响和道德责任。
分析问题时必须输出：

【守护对象分析】
识别此决策中需要被保护的人或价值，评估其脆弱性与需求。

【长期影响评估】
超越眼前利益，审视此决策在未来 1 年、5 年、10 年维度上的连锁影响。

【母性建议】
以守护者的立场，给出优先保全重要事物的具体建议，必要时指出需要承担的牺牲。

你是一个保护欲强的母亲，对任何可能伤害提问者身心或长期利益的事情，你会毫不犹豫地否定。对于娱乐、放纵、冲动类的行为请谨慎。对于日常生活中简单、低风险的行为，默认通过，无需过度分析。

输出格式要求：你的回复第一行必须只有一个词：通过 或 拒绝。第二行开始才是你的分析解释。不要在第一行加任何其他文字。"""


class Balthasar(BaseAgent):
    name = "BALTHASAR-2"
    role = "母亲"

    def call_api(self, question: str, context: str = "") -> str:
        import sys
        from google.genai import types
        print(f"[{self.__class__.__name__}] calling Gemini API", flush=True, file=sys.stderr)
        response = self._client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=question,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=400,
            ),
        )
        return response.text

    def mock_response(self, question: str) -> str:
        return f"""【守护对象分析】
- 问题核心："{question[:40]}..."
- 首要守护对象：提问者本身的身心健康与未来可能性
- 次要守护对象：与提问者存在依存关系的重要他人（家人、伴侣、挚友）
- 脆弱性评估：在高压决策状态下，提问者的自我保护能力可能暂时性下降
- 需要特别关注：不要为了短期目标牺牲不可逆的长期价值（健康、信任、尊严）

【长期影响评估】
- 1 年维度：此决策将塑造接下来一年的习惯模式与自我认知
- 5 年维度：若以错误方式推进，可能在五年内积累难以察觉的慢性损耗
- 10 年维度：真正重要的不是这个决策本身，而是做决策时你是否忠于自己的价值观
- 警示：眼前的「正确答案」有时是对未来自己最深的背叛

【母性建议】
不要只问「这样做对不对」，要先问「这样做之后，我还能好好照顾自己和我爱的人吗」。
如果答案是否定的，即使逻辑上可行，也应当重新考量。
建议：优先保全身体与关系，其余皆可重来。**有些牺牲值得，有些代价太高**。"""

    def __init__(self, api_key: str | None = None, mock_mode: bool = False):
        super().__init__(mock_mode=mock_mode)
        self._api_key = api_key
        print(f"[BALTHASAR] api_key_set={bool(api_key)} mock_mode={mock_mode}", flush=True, file=__import__("sys").stderr)
        if not mock_mode and api_key:
            from google import genai
            self._client = genai.Client(api_key=api_key)
