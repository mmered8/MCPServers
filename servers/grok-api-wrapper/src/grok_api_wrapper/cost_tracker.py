"""Per-request cost tracking with usage summaries."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from grok_api_wrapper.grok_client import PRICING


@dataclass
class UsageRecord:
    timestamp: str
    tool: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0


class CostTracker:
    """Track API costs per request with summary reporting."""

    def __init__(self):
        self._records: list[UsageRecord] = []

    def record(
        self,
        tool: str,
        model: str = "",
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost_override: Optional[float] = None,
    ) -> None:
        """Record a single API call's cost."""
        if cost_override is not None:
            cost = cost_override
        elif model in PRICING:
            prices = PRICING[model]
            cost = (input_tokens * prices["input"] + output_tokens * prices["output"]) / 1_000_000
        else:
            cost = 0.0

        self._records.append(UsageRecord(
            timestamp=datetime.now().isoformat(timespec="seconds"),
            tool=tool,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
        ))

    def summary(self) -> str:
        """Return a formatted usage summary."""
        if not self._records:
            return "No API usage recorded yet."

        total_cost = sum(r.cost_usd for r in self._records)
        total_requests = len(self._records)

        # Per-tool breakdown
        by_tool: dict[str, dict] = {}
        for r in self._records:
            if r.tool not in by_tool:
                by_tool[r.tool] = {"requests": 0, "cost": 0.0, "input_tokens": 0, "output_tokens": 0}
            by_tool[r.tool]["requests"] += 1
            by_tool[r.tool]["cost"] += r.cost_usd
            by_tool[r.tool]["input_tokens"] += r.input_tokens
            by_tool[r.tool]["output_tokens"] += r.output_tokens

        lines = [
            f"## Grok API Usage Summary",
            f"",
            f"**Total cost**: ${total_cost:.6f}",
            f"**Total requests**: {total_requests}",
            f"",
            f"### Per-Tool Breakdown",
            f"",
        ]
        for tool, stats in sorted(by_tool.items()):
            lines.append(f"- **{tool}**: {stats['requests']} requests, ${stats['cost']:.6f}")
            lines.append(f"  Input: {stats['input_tokens']} tokens, Output: {stats['output_tokens']} tokens")

        return "\n".join(lines)

    def reset(self) -> int:
        """Reset tracker, return number of records cleared."""
        count = len(self._records)
        self._records.clear()
        return count
