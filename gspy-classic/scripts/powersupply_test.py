import sys
from time import sleep

sys.path.append("../gseos_qt/hardware_modules")

# noinspection PyUnresolvedReferences
from powersupply import PowerSupply  # module can be found from PATH

print("Opening Connection")
powersupply = PowerSupply(
    channels=2,
    polling=False,
    polling_interval=300,
    port="COM4",
    baudrate=9600
)

sleep(1)

for i in range(2):
    for name, value in [("Voltage", powersupply.voltage[i]), ("Current", powersupply.intensity[i])]:
        print("%s of Channel %d: %f" % (name, i + 1, value))

sleep(1)
print("Resetting")

powersupply.send_command("*RST", expected_lines=0)

sleep(1)

for i in range(2):
    for name, value in [("Voltage", powersupply.voltage[i]), ("Current", powersupply.intensity[i])]:
        print("%s of Channel %d: %f" % (name, i + 1, value))

sleep(1)

print("Setting some values")
powersupply.send_command("range1 0", expected_lines=0)
powersupply.send_command("range2 0", expected_lines=0)
powersupply.set_voltage_to_device(0.123, channel=1)
powersupply.set_intensity_to_device(4.567, channel=1)
powersupply.set_voltage_to_device(7.654, channel=2)
powersupply.set_intensity_to_device(3.210, channel=2)

sleep(1)

print("Closing Connection")

powersupply.close()

sleep(1)
