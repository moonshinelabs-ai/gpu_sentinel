import enum
from typing import Callable


class SentinelState(enum.Enum):
    SAFE = 0
    ARMED = 1


class Sentinel:
    """The Sentinel object that watches a stream of incoming values."""

    def __init__(
        self,
        arm_duration: int,
        arm_threshold: float,
        kill_duration: int,
        kill_threshold: float,
        kill_fn: Callable,
    ):
        """Create the GPU sentinel.

        The sentinel works by waiting to arm until a certain threshold has been reached for a set duration.
        Then it will wait until a certain threshold has not been exceeded for a set duration, and run the kill_fn
        then.

        Args:
            arm_duration: How long in ticks to wait for the threshold condition to be met before arming.
            arm_threshold: What GPU percentage required to hit threshold.
            kill_duration: How long in ticks to wait for the kill condition to be met before killing.
            kill_threshold: If the GPU drops under this percentage, consider the kill condition met.
            kill_fn: The function to call when killing, might shutdown machine, etc.
        """
        self.max_arm_duration = 60 * 60
        self.max_kill_duration = 60 * 60

        assert (
            arm_duration < self.max_arm_duration
        ), f"arm_duration can at most be {self.max_arm_duration} ticks"
        assert (
            kill_duration < self.max_kill_duration
        ), f"kill_duration can at most be {self.max_arm_duration} ticks"

        self.arm_duration = arm_duration
        self.arm_threshold = arm_threshold
        self.kill_duration = kill_duration
        self.kill_threshold = kill_threshold
        self.kill_fn = kill_fn

        self.state = SentinelState.SAFE
        self.seconds_to_transition = self.arm_duration

    def tick(self, current_value: float):
        """Run this to advance the system.

        Args:
            current_value: The next value to track.
        """
        if self.state is SentinelState.SAFE:
            # If the new value exceeds the threshold, continue counting down.
            # Otherwise reset the timer.
            if current_value > self.arm_threshold:
                self.seconds_to_transition -= 1
            else:
                self.seconds_to_transition = self.arm_duration

            # Check if we should arm.
            if self.seconds_to_transition <= 0:
                self.state = SentinelState.ARMED
                self.seconds_to_transition = self.kill_duration
        elif self.state is SentinelState.ARMED:
            # If the new value is lower than the threshold, continue counting down.
            # Otherwise reset the timer.
            if current_value < self.kill_threshold:
                self.seconds_to_transition -= 1
            else:
                self.seconds_to_transition = self.kill_duration

            # Check if we should kill
            if self.seconds_to_transition <= 0:
                self.kill_fn()
