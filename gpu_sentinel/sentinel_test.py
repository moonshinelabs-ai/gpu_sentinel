import unittest
from unittest.mock import Mock

from .sentinel import Sentinel, SentinelState


class TestSentinel(unittest.TestCase):
    def test_arm(self):
        kill_fn = Mock()
        sentinel = Sentinel(
            arm_duration=5,
            arm_threshold=0.8,
            kill_duration=4,
            kill_threshold=0.7,
            kill_fn=kill_fn,
        )

        # When we start, state should be SAFE
        self.assertEqual(sentinel.state, SentinelState.SAFE)

        # We tick for 10 without hitting the threshold
        for _ in range(10):
            sentinel.tick(0.2)
        self.assertEqual(sentinel.state, SentinelState.SAFE)

        # Do we arm correctly?
        for _ in range(4):
            sentinel.tick(0.9)
        self.assertEqual(sentinel.state, SentinelState.SAFE)
        sentinel.tick(0.9)
        self.assertEqual(sentinel.state, SentinelState.ARMED)
        kill_fn.assert_not_called()

    def test_doesnt_arm(self):
        kill_fn = Mock()
        sentinel = Sentinel(
            arm_duration=5,
            arm_threshold=0.8,
            kill_duration=4,
            kill_threshold=0.7,
            kill_fn=kill_fn,
        )

        # When we start, state should be SAFE
        self.assertEqual(sentinel.state, SentinelState.SAFE)

        # Almost arm
        for _ in range(4):
            sentinel.tick(0.9)
        self.assertEqual(sentinel.state, SentinelState.SAFE)

        # Go back to safed
        for _ in range(4):
            sentinel.tick(0.2)
        self.assertEqual(sentinel.state, SentinelState.SAFE)

        # Go back to armed
        for _ in range(5):
            sentinel.tick(0.9)
        self.assertEqual(sentinel.state, SentinelState.ARMED)
        kill_fn.assert_not_called()

    def test_kill(self):
        kill_fn = Mock()
        sentinel = Sentinel(
            arm_duration=5,
            arm_threshold=0.8,
            kill_duration=4,
            kill_threshold=0.7,
            kill_fn=kill_fn,
        )

        # When we start, state should be SAFE
        self.assertEqual(sentinel.state, SentinelState.SAFE)

        # Arm
        for _ in range(5):
            sentinel.tick(0.9)
        self.assertEqual(sentinel.state, SentinelState.ARMED)

        # Tick for 10 without hitting
        for _ in range(10):
            sentinel.tick(0.9)
        self.assertEqual(sentinel.state, SentinelState.ARMED)

        # Tick for 4 and kill
        for _ in range(4):
            sentinel.tick(0.3)
        kill_fn.assert_called_once()


if __name__ == "__main__":
    unittest.main()
