import os
import sys
import time
import psutil

if os.name == "nt":

    class CpuUsageProperties(object):
        """Stores the CPU usage for a Windows system.

        Attributes:\n
            idleTime (float): Time spent doing nothing.
            kernelTime (float): Time spent by processes executing in kernel mode. Also known as system time.
            userTime (float): Time spent by normal processes executing in user mode.
            processKernelTime (float): Time spent by processes in kernel space.
            processUserTime (float): Time spent by processes in user space.
        """

        def __init__(self):
            """Constructor:\n
                Initialises a CpuUsageProperties object."""
            cpuTimes = psutil.cpu_times()
            self.idleTime = cpuTimes.idle
            self.kernelTime = cpuTimes.system
            self.userTime = cpuTimes.user

            process = psutil.Process()
            processTimes = process.cpu_times()
            self.processKernelTime = processTimes.system
            self.processUserTime = processTimes.user

    def store_cpu_usage() -> CpuUsageProperties:
        """Starts recording the CPU usage, by storing the current usage. Returns the current CPU usage properties."""
        
        return CpuUsageProperties()

    def calculate_cpu_usage(startCpuProperties, endCpuProperties):
        """calculate the CPU usage for a test.

        Args:\n
            startCpuProperties (CpuUsageProperties): The original CPU usage
                properties when the test started.
            endCpuProperties (CpuUsageProperties): The final CPU usage properties
                when the test completed.
        """

        # Subtract the original total CPU figures from the final figures.
        idleTime = endCpuProperties.idleTime - startCpuProperties.idleTime
        kernelTime = endCpuProperties.kernelTime - startCpuProperties.kernelTime
        userTime = endCpuProperties.userTime - startCpuProperties.userTime

        # Calculate the total time.
        totalTime = userTime + kernelTime + idleTime

        # Calculate the total usage.
        if totalTime != 0:
            totalUsage = ((totalTime - idleTime) * 100) / totalTime
        else:
            totalUsage = 0

        # Subtract the original process CPU figures from the final figures.
        processKernelTime = endCpuProperties.processKernelTime - startCpuProperties.processKernelTime
        processUserTime = endCpuProperties.processUserTime - startCpuProperties.processUserTime

        # Calculate the process's usage.
        if totalTime != 0:
            processUsage = ((processUserTime + processKernelTime) * 100) / totalTime
        else:
            processUsage = 0
        
        return processUsage, totalUsage

else:
    class CpuUsageProperties(object):
        """Stores the CPU usage.

        Attributes:\n
            currentTime: The current time.
            userTime (float): The current user time for the system.
            systemTime (float): The current system time for the system.
            niceTime (float): The current nice time for the system.
            idleTime (float): The current idle time for the system.
            iowaitTime (float): The current I/O wait time for the system. 
        """

        def __init__(self):
            """Constructor:\n
                Initialises a CpuUsageProperties object for non-Windows OS environment."""

            times = psutil.cpu_times()

            self.currentTime = time.time()
            self.userTime = times.user
            self.systemTime = times.system
            self.niceTime = times.nice
            self.idleTime = times.idle
            self.iowaitTime = times.iowait
            
            process = psutil.Process()

            # Get the process user time
            self.processUserTime = process.cpu_times().user

            # Get the process system time
            self.processKernelTime = process.cpu_times().system

    def store_cpu_usage() -> CpuUsageProperties:
        """Starts recording the CPU usage, by storing the current usage. Returns the current CPU usage properties."""

        return CpuUsageProperties()

    def calculate_cpu_usage(startCpuProperties, endCpuProperties):
        """Prints the CPU usage for a test.

        Args:\n
            startCpuProperties (CpuUsageProperties): The original CPU usage
                properties when the test started.
            endCpuProperties (CpuUsageProperties): The final CPU usage properties
                when the test started.
        """

        # Determine the number of CPUs.
        cpuCount = psutil.cpu_count()

        # Subtract the original total CPU figures from the final figures.
        userTime = endCpuProperties.userTime - startCpuProperties.userTime
        systemTime = endCpuProperties.systemTime - startCpuProperties.systemTime
        niceTime = endCpuProperties.niceTime - startCpuProperties.niceTime
        idleTime = endCpuProperties.idleTime - startCpuProperties.idleTime
        iowaitTime = endCpuProperties.iowaitTime - startCpuProperties.iowaitTime

        # Calculate the total time.
        totalTime = userTime + systemTime + niceTime + idleTime + iowaitTime

        # Calculate the total usage.
        if totalTime > 0:
            totalUsage = ((totalTime - idleTime) * 100) / totalTime
        else:
            totalUsage = 0

        # Calculate the total process time.
        processTotalTime = endCpuProperties.currentTime - startCpuProperties.currentTime

        # Calculate the process's usage.
        if processTotalTime > 0 and cpuCount > 0:

            processUserTime = endCpuProperties.processUserTime - startCpuProperties.processUserTime

            processKernelTime = endCpuProperties.processKernelTime - startCpuProperties.processKernelTime

            processUsage = (((processUserTime + processKernelTime) * 100) / (processTotalTime * cpuCount))
        else:
            processUsage = 0

        # Note: The kernel time may not be needed, if this is included in the user
        # time (at least according to some manuals!)

        return processUsage, totalUsage