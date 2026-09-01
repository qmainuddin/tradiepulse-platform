from typing import List, Tuple
from src.schemas.state import ChatMessage

class BoundedHistoryManager:
    """
    Maintains last-N verbatim turns and generates rolling summaries for older context.
    Prevents unbounded context window inflation and token burn.
    """

    def __init__(self, max_verbatim_turns: int = 4):
        self.max_verbatim_turns = max_verbatim_turns

    def process_history(self, messages: List[ChatMessage]) -> Tuple[List[ChatMessage], str]:
        if len(messages) <= self.max_verbatim_turns:
            return messages, ""

        verbatim_messages = messages[-self.max_verbatim_turns:]
        older_messages = messages[:-self.max_verbatim_turns]

        summary_lines = []
        for msg in older_messages:
            summary_lines.append(f"{msg.role.capitalize()}: {msg.content[:100]}...")

        rolling_summary = "Prior turns summary:\n" + "\n".join(summary_lines)
        return verbatim_messages, rolling_summary
