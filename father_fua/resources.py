from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Budget:
    token_limit: int
    money_limit: float
    tokens_used: int = 0
    money_used: float = 0.0

    def consume(self, *, tokens: int = 0, money: float = 0.0) -> None:
        if self.tokens_used + tokens > self.token_limit:
            raise RuntimeError("token budget exceeded")
        if self.money_used + money > self.money_limit:
            raise RuntimeError("money budget exceeded")
        self.tokens_used += tokens
        self.money_used += money
