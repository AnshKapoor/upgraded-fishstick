import serial
import time
from contextlib import suppress


def console(port="COM4", baudrate=19200, timeout=500, line_end="\n"):
    timeout /= 1000
    ser = serial.Serial(
        port=port,
        baudrate=baudrate,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        xonxoff=True,
        dsrdtr=False,
        rtscts=False,
        timeout=0
    )
    with suppress(Exception):
        print(" trying Opening serial port \n")
        ser.close()
        ser.open()
    ser.isOpen()

    while True:
        cmd = input("> ")
        cmd += line_end
        ser.write(cmd.encode('utf-8'))
        start = time.time()

        if cmd.find("?") >= 0:
            out = bytes()

            while time.time() - start < timeout and ser.inWaiting() == 0:
                time.sleep(.001)

            if ser.inWaiting() > 0:
                while ser.inWaiting() > 0 or (time.time() - start < timeout):  # and out[-1] != 10
                    out += ser.read()
                    # print("bit")
            else:
                out = ''

            with suppress(Exception):
                print(out[-2])
                print(out[-1])
                out = out.decode()[-1]

            print(out)


console()
