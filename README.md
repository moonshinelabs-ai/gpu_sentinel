# GPU Sentinel

### A Moonshine Labs tool

If you're automating training your large models in the cloud, cost control is critial. How many times have you accidentally left an expensive GPU instance running when the underlying job had crashed, costing you money or capacity with no benefit?

*GPU Sentinel* is a simple tool that will watch your instance and automatically trigger when GPU utilization drops below a certain amount for a period of time. GPU Sentinel can automatically shutdown or reboot the instance, or simply end its own process so you can do an action yourself.

Constraints:

* To shutdown/reboot the machine, GPU Sentinel requires sudo permissions.
* Currently only working on Linux, Windows support coming soon.