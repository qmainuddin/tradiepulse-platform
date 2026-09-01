import logging
from typing import Dict, Any

log = logging.getLogger(__name__)

class TokenBudgetGovernor:
    """Enforces request-level token ceiling and tracks cumulative token/cost metrics."""

    def __init__(self, token_ceiling: int = 4096, max_tool_calls: int = 5):
        self.token_ceiling = token_ceiling
        self.max_tool_calls = max_tool_calls
        self.total_tokens_in = 0
        self.total_tokens_out = 0
        self.total_cost_usd = 0.0

    def check_request_budget(self, estimated_prompt_tokens: int) -> bool:
        if estimated_prompt_tokens > self.token_ceiling:
            log.error("Request token ceiling exceeded: estimated %d > ceiling %d", estimated_prompt_tokens, self.token_ceiling)
            return False
        return True

    def record_usage(self, tokens_in: int, tokens_out: int, cost_usd: float) -> None:
        self.total_tokens_in += tokens_in
        self.total_tokens_out += tokens_out
        self.total_cost_usd += cost_usd

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "total_tokens_in": self.total_tokens_in,
            "total_tokens_out": self.total_tokens_out,
            "total_tokens": self.total_tokens_in + self.total_tokens_out,
            "total_cost_usd": round(self.total_cost_usd, 6)
        }
