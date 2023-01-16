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

## Current Limitations

* To shutdown/reboot the machine, GPU Sentinel requires sudo permissions or sudo-less shutdown.
* Currently only working on Linux, can add Windows support if there's interest.