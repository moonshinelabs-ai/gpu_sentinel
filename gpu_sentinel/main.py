import argparse
import os
import time
from ast import parse
from statistics import mean
from typing import Callable, Optional, Sequence

import GPUtil  # type: ignore

from .sentinel import Sentinel, SentinelState

TICK_TIME_S = 1


def shutdown():
    os.system("sudo shutdown -h now")


def reboot():
    os.system("sudo reboot")


def create_kill_fn(action: str) -> Callable:
    if action == "end_process":
        return exit
    elif action == "shutdown":
        return shutdown
    elif action == "reboot":
        return reboot
    else:
        raise Exception("Unknown action")


def get_gpu_usage(device_ids: Optional[Sequence[int]]) -> float:
    """Get the avg GPU usage across devices.

    This function does not validate the GPU device ID list, so you can
    include GPUs that aren't actually present in the device ID list and
    it will still work.

    Args:
        device_ids: An optional list of device ids to average over.

    Returns:
        average_load: The mean of all the GPU loads sampled.
    """
    gpu_usage = []

    devices = GPUtil.getGPUs()
    for device in devices:
        if device_ids is None:
            gpu_usage.append(device.load)
        else:
            if device.id in device_ids:
                gpu_usage.append(device.load)

    return mean(gpu_usage)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="A monitor for your GPU")
    parser.add_argument(
        "--arm_duration",
        default=30,
        type=int,
        help="How many seconds of activity to wait before arming the sentinel.",
    )
    parser.add_argument(
        "--arm_threshold",
        default=0.8,
        type=float,
        help="What level of utilization is considered activity",
    )
    parser.add_argument(
        "--kill_duration",
        default=30,
        type=int,
        help="How many seconds of inactivity to wait before running the kill function.",
    )
    parser.add_argument(
        "--kill_threshold",
        default=0.7,
        type=float,
        help="What level of utilization is considered inactivity",
    )
    parser.add_argument(
        "--kill_action",
        choices=["end_process", "shutdown", "reboot"],
        default="end_process",
        help="What to do when the kill trigger is hit",
    )
    parser.add_argument(
        "--gpu_devices",
        nargs="+",
        required=False,
        help="Which GPU devices to average (empty for all)",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    if args.kill_action in ["shutdown", "reboot"]:
        if os.geteuid() != 0:
            print(
                "WARNING: This program requires sudo if it is going to shutdown the computer.\n"
                "If you are have not setup your environment appropriately, the shutdown\n"
                "command will request a password and may fail to shutdown your machine.\n"
                "\n"
                "We suggest configuring your machine to not require a sudo password for\n"
                "the commands you want to run. See https://askubuntu.com/a/168885\n"
            )
    print(
        f"Starting GPU Sentinel, will arm once average GPU usage is at least {args.arm_threshold:.0%} for {args.arm_duration} seconds"
    )
    if args.gpu_devices is None:
        print(f"Monitoring all GPUs on the system")
    else:
        print(f"Monitoring GPUs {args.gpu_devices} only.")
        print("These GPUs are user specified and may not exist on the system.")

    kill_fn = create_kill_fn(args.kill_action)
    sentinel = Sentinel(
        arm_duration=args.arm_duration,
        arm_threshold=args.arm_threshold,
        kill_duration=args.kill_duration,
        kill_threshold=args.kill_threshold,
        kill_fn=kill_fn,
    )
    gpu_device_ids = None
    if args.gpu_devices:
        gpu_device_ids = [int(i) for i in args.gpu_devices]

    # Run the program until it's shutdown or we kill things.
    print("Monitoring for low GPU usage! Press ctrl+C to exit")
    show_arm_warning = True
    while True:
        gpu_usage = get_gpu_usage(device_ids=gpu_device_ids)
        sentinel.tick(gpu_usage)

        if sentinel.state == SentinelState.ARMED and show_arm_warning:
            print(
                f"GPU Sentinel is armed, will '{args.kill_action}' when values drop below {args.kill_threshold:.0%} for {args.kill_duration} seconds"
            )
            show_arm_warning = False

        time.sleep(TICK_TIME_S)


if __name__ == "__main__":
    main()
