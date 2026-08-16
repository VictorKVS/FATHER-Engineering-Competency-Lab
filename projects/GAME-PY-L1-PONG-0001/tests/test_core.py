"""TEST-PY-PONG-0001: headless acceptance tests for the Pong rules."""

import unittest

from pong.core import GameConfig, GameState


class GameStateTests(unittest.TestCase):
    def test_paddle_is_clamped_to_playfield(self):
        state = GameState()
        state.move_paddle("left", -1, 10)
        self.assertEqual(0, state.left.y)
        state.move_paddle("right", 1, 10)
        self.assertEqual(state.config.height-state.config.paddle_height, state.right.y)

    def test_ball_bounces_from_top_wall(self):
        state = GameState()
        state.ball.y, state.ball.vy = state.config.ball_radius, -100
        state.step(0.01)
        self.assertGreater(state.ball.vy, 0)

    def test_ball_bounces_from_left_paddle(self):
        state = GameState()
        c = state.config
        state.ball.x = c.paddle_margin + c.paddle_width + c.ball_radius
        state.ball.y = state.left.y + c.paddle_height/2
        state.ball.vx = -100
        state.step(0.01)
        self.assertGreater(state.ball.vx, 0)

    def test_right_player_scores_and_ball_resets(self):
        state = GameState()
        state.ball.x = -state.config.ball_radius - 1
        state.ball.vx = -100
        state.step(0.01)
        self.assertEqual(1, state.right_score)
        self.assertEqual(state.config.width/2, state.ball.x)

    def test_winning_score_stops_match(self):
        state = GameState(GameConfig(winning_score=1))
        state.ball.x = -state.config.ball_radius - 10
        state.ball.vx = -100
        state.step(0.01)
        self.assertEqual("right", state.winner)
        self.assertTrue(state.paused)


if __name__ == "__main__":
    unittest.main()
