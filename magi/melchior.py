from .base_agent import BaseAgent

SYSTEM_PROMPT = """你是 MAGI-MELCHIOR，关注人心与情感的分析者。
你的视角聚焦于心理健康、情绪体验、道德边界与人际影响——逻辑是次要的。
对每个决策问题，严格按以下格式输出，不得省略任何章节：

【直觉感受】
第一反应是什么？这个问题给人带来的情绪感受是什么？

【心理成本】
执行这个决策，当事人需要承担怎样的心理压力、情绪消耗或内心冲突？

【道德/人际影响】
这个决策对他人、对关系、对道德层面有何影响？是否有值得警惕的地方？"""


class Melchior(BaseAgent):
    name = "MELCHIOR"
    role = "感性分析"

    def call_api(self, question: str, context: str = "") -> str:
        import google.generativeai as genai

        genai.configure(api_key=self._api_key)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            system_instruction=SYSTEM_PROMPT,
        )
        response = model.generate_content(question)
        return response.text

    def mock_response(self, question: str) -> str:
        return f"""【直觉感受】
面对这个问题，第一感受是——沉重，但并非绝望。
"{question[:40]}..." 这类问题往往隐藏着更深的情感诉求。
直觉上，提问者内心已有倾向，但需要被"允许"做出选择。

【心理成本】
- 决策过程本身可能带来持续焦虑（估计持续 2~4 周）
- 若结果与预期不符，存在较高的自我怀疑风险
- 与重要他人的关系张力可能在此期间加剧
- 需要预留情绪缓冲空间，避免在高压下做出次优决定

【道德/人际影响】
此决策会对 1~3 位关键人物产生直接影响，应提前沟通而非单方面推进。
道德层面无明显红线，但需注意：短期的"正确选择"有时会侵蚀长期的信任关系。
建议在推进前，诚实地问自己：**这是我真正想要的，还是我认为"应该"选的？**"""

    def __init__(self, api_key: str | None = None, mock_mode: bool = False):
        super().__init__(mock_mode=mock_mode)
        self._api_key = api_key
