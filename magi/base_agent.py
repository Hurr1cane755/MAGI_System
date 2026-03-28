from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """MAGI 系统 Agent 基类"""

    name: str = "UNKNOWN"
    role: str = "未定义角色"

    def __init__(self, mock_mode: bool = False):
        self.mock_mode = mock_mode

    def analyze(self, question: str, context: str = "") -> str:
        if self.mock_mode:
            return self.mock_response(question)
        return self.call_api(question, context)

    @abstractmethod
    def call_api(self, question: str, context: str = "") -> str:
        """调用真实 API"""

    @abstractmethod
    def mock_response(self, question: str) -> str:
        """返回 mock 示例回复"""
