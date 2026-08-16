"""Deterministic, display-independent Pong rules.

Artifact: CODE-PY-PONG-0001. Decision context: docs/CYCLE_PASSPORT.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class GameConfig:
    width: float = 800
    height: float = 450
    paddle_width: float = 14
    paddle_height: float = 90
    paddle_margin: float = 30
    paddle_speed: float = 330
    ball_radius: float = 9
    ball_speed_x: float = 280
    ball_speed_y: float = 180
    winning_score: int = 5


@dataclass(slots=True)
class Paddle:
    y: float


@dataclass(slots=True)
class Ball:
    x: float
    y: float
    vx: float
    vy: float


@dataclass(slots=True)
class GameState:
    config: GameConfig = field(default_factory=GameConfig)
    left: Paddle = field(init=False)
    right: Paddle = field(init=False)
    ball: Ball = field(init=False)
    left_score: int = 0
    right_score: int = 0
    paused: bool = False
    winner: str | None = None

    def __post_init__(self) -> None:
        middle = (self.config.height - self.config.paddle_height) / 2
        self.left = Paddle(middle)
        self.right = Paddle(middle)
        self.ball = Ball(0, 0, 0, 0)
        self.reset_ball(direction=1)

    def reset_ball(self, direction: int) -> None:
        c = self.config
        self.ball = Ball(c.width / 2, c.height / 2, abs(c.ball_speed_x) * direction, c.ball_speed_y)

    def reset_match(self) -> None:
        self.left_score = self.right_score = 0
        self.winner = None
        self.paused = False
        self.reset_ball(direction=1)

    def move_paddle(self, side: str, direction: float, dt: float) -> None:
        paddle = self.left if side == "left" else self.right
        maximum = self.config.height - self.config.paddle_height
        paddle.y = min(maximum, max(0.0, paddle.y + direction * self.config.paddle_speed * dt))

    def step(self, dt: float) -> None:
        if self.paused or self.winner or dt <= 0:
            return
        dt = min(dt, 0.05)  # Limit a delayed frame; prevents tunnelling after window stalls.
        c, b = self.config, self.ball
        b.x += b.vx * dt
        b.y += b.vy * dt

        if b.y - c.ball_radius <= 0 and b.vy < 0:
            b.y = c.ball_radius
            b.vy *= -1
        elif b.y + c.ball_radius >= c.height and b.vy > 0:
            b.y = c.height - c.ball_radius
            b.vy *= -1

        left_x = c.paddle_margin + c.paddle_width
        right_x = c.width - c.paddle_margin - c.paddle_width
        if b.vx < 0 and b.x - c.ball_radius <= left_x and b.x >= c.paddle_margin:
            if self.left.y <= b.y <= self.left.y + c.paddle_height:
                b.x = left_x + c.ball_radius
                b.vx = abs(b.vx)
        elif b.vx > 0 and b.x + c.ball_radius >= right_x and b.x <= c.width - c.paddle_margin:
            if self.right.y <= b.y <= self.right.y + c.paddle_height:
                b.x = right_x - c.ball_radius
                b.vx = -abs(b.vx)

        if b.x + c.ball_radius < 0:
            self.right_score += 1
            self._after_score("right", direction=-1)
        elif b.x - c.ball_radius > c.width:
            self.left_score += 1
            self._after_score("left", direction=1)

    def _after_score(self, scorer: str, direction: int) -> None:
        score = self.left_score if scorer == "left" else self.right_score
        if score >= self.config.winning_score:
            self.winner = scorer
            self.paused = True
        else:
            self.reset_ball(direction)

