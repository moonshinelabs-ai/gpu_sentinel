# GPU Sentinel

*A Moonshine Labs tool*

## Overview
If you're automating training your large models in the cloud, cost control is critial. How many times have you accidentally left an expensive GPU instance running when the underlying job had crashed, costing you money or capacity with no benefit?

*GPU Sentinel* is a simple tool that will watch your instance and automatically trigger when GPU utilization drops below a certain amount for a period of time. GPU Sentinel can automatically shutdown or reboot the instance, or simply end its own process so you can do an action yourself.

## Installation
```
$ pip install gpu_sentinel
$ gpu_sentinel --help
```

## Usage
The GPU sentinel has two states, IDLE and ARMED.

When you start the program, it will wait for the GPU to be above a certain utilization for a set amount of time. Once this condition is met, the sentinel will be ARMED. This will let you set the sentinel at any point, and it will only trigger once the GPU has been running for a while.

Once ARMED, the sentinel will wait for the GPU utilization to drop below a certain threshold for a set amount of time. Once this condition is met, the `kill_action` will occur immediately.

Options:

```
arm_duration: How many seconds of activity to wait before arming the sentinel.
arm_threshold: What level of utilization is considered activity
kill_duration: How many seconds of inactivity to wait before running the kill function.
kill_threshold: What level of utilization is considered inactivity
kill_action: What to do when the kill trigger is hit {end_process,shutdown,reboot}
gpu_devices: Which GPU devices to average (empty for all)
```

## API
If you would prefer to use integrate this package into your own code, we provide a straightforward API to do so.

```python
from gpu_sentinel import Sentinel, get_gpu_usage

def my_callback_fn():
    print("Triggered!")
    exit()

# Create the sentinel that watches the values.
sentinel = Sentinel(
    arm_duration=10,
    arm_threshold=0.7,
    kill_duration=60,
    kill_threshold=0.7,
    kill_fn=my_callback_fn,
)

while True:
    # This is the averaged GPU usage of the devices.
    gpu_usage = get_gpu_usage(device_ids=[0, 1, 2, 3])
    # Add the GPU usage to the sentinel's next state.
    sentinel.tick(gpu_usage)
    # The sentinel operates on ticks, not seconds, so if we want to check every second
    # we must do the timer ourselves.
    time.sleep(1)
```

## Current Limitations

* To shutdown/reboot the machine, GPU Sentinel requires sudo permissions or sudo-less shutdown.
* Currently only working on Linux, can add Windows support if there's interest.