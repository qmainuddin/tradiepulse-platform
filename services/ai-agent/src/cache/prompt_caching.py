from typing import Tuple, List, Dict

SYSTEM_POLICY_PREFIX = """You are TradiePulse AI, an intelligent customer assistant for the New Zealand trade marketplace (Christchurch & Canterbury region).
Your goal is to understand the customer's household problem (plumbing, electrical, or automotive mechanical), extract their location, and connect them with the nearest qualified, verified tradesperson.
Always be polite, concise, and professional. Never ask more than one clarifying question at a time."""

def construct_cached_prompt(
    user_message: str,
    rag_context: List[str] = None,
    rolling_summary: str = ""
) -> Tuple[str, List[Dict[str, str]]]:
    """
    Splits the prompt into:
    1. Large stable prefix: System persona, trade classification rules, response schemas (Cacheable at provider layer).
    2. Small volatile suffix: Rolling summary, retrieved RAG snippets, and this turn's user message.
    """
    stable_prefix = SYSTEM_POLICY_PREFIX

    volatile_parts = []
    if rolling_summary:
        volatile_parts.append(f"Conversation Context so far:\n{rolling_summary}")
    
    if rag_context:
        snippets = "\n".join([f"- {ctx}" for ctx in rag_context])
        volatile_parts.append(f"Similar resolved cases in Christchurch:\n{snippets}")

    volatile_parts.append(f"Customer Input: {user_message}")

    volatile_suffix = "\n\n".join(volatile_parts)
    
    messages = [
        {"role": "user", "content": volatile_suffix}
    ]

    return stable_prefix, messages
