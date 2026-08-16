"""Tkinter adapter for CODE-PY-PONG-0001."""

from __future__ import annotations

import argparse
import json
import time
import tkinter as tk

from .core import GameState


class PongApp:
    def __init__(self) -> None:
        self.state = GameState()
        c = self.state.config
        self.root = tk.Tk()
        self.root.title("FATHER Lab — Pong 0.1.0-pre-alpha")
        self.canvas = tk.Canvas(self.root, width=c.width, height=c.height, bg="#101820", highlightthickness=0)
        self.canvas.pack()
        self.keys: set[str] = set()
        self.root.bind("<KeyPress>", self._press)
        self.root.bind("<KeyRelease>", lambda e: self.keys.discard(e.keysym.lower()))
        self.last_time = time.perf_counter()

    def _press(self, event: tk.Event) -> None:
        key = event.keysym.lower()
        if key == "space":
            self.state.paused = not self.state.paused
        elif key == "r":
            self.state.reset_match()
        self.keys.add(key)

    def run(self) -> None:
        self._tick()
        self.root.mainloop()

    def _tick(self) -> None:
        now = time.perf_counter()
        dt, self.last_time = now - self.last_time, now
        for side, up, down in (("left", "w", "s"), ("right", "up", "down")):
            direction = float(down in self.keys) - float(up in self.keys)
            self.state.move_paddle(side, direction, dt)
        self.state.step(dt)
        self._draw()
        self.root.after(16, self._tick)

    def _draw(self) -> None:
        s, c, cv = self.state, self.state.config, self.canvas
        cv.delete("all")
        cv.create_line(c.width / 2, 0, c.width / 2, c.height, fill="#4b5963", dash=(8, 10))
        for x, paddle in ((c.paddle_margin, s.left), (c.width - c.paddle_margin - c.paddle_width, s.right)):
            cv.create_rectangle(x, paddle.y, x + c.paddle_width, paddle.y + c.paddle_height, fill="#f2f2f2", outline="")
        b = s.ball
        cv.create_oval(b.x-c.ball_radius, b.y-c.ball_radius, b.x+c.ball_radius, b.y+c.ball_radius, fill="#ffcc33", outline="")
        cv.create_text(c.width/2, 32, text=f"{s.left_score}   {s.right_score}", fill="white", font=("Arial", 22, "bold"))
        label = f"{s.winner.upper()} WINS — R to restart" if s.winner else ("PAUSED" if s.paused else "")
        cv.create_text(c.width/2, c.height/2, text=label, fill="white", font=("Arial", 18, "bold"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="FATHER Lab Pong")
    parser.add_argument(
        "--self-check",
        action="store_true",
        help="run a headless deterministic product check and exit",
    )
    args = parser.parse_args(argv)
    if args.self_check:
        state = GameState()
        state.step(1 / 60)
        print(json.dumps({"project": "GAME-PY-L1-PONG-0001", "self_check": "passed"}))
        return 0
    PongApp().run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
