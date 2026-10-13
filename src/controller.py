import math
import socket
import struct
import time
import random

# IP address of the machine running MuJoCo (use "127.0.0.1" if on the same PC)
HOST = "127.0.0.1"
PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 20 normalized actuator commands in [0, 1] (0 = actuator min, 1 = actuator max),
# in the model's actuator order. The simulator maps them to real joint targets.
target_controls = [0.5] * 20

try:
    while True:
        # Update your target controls here
        # Example: move a random actuator along a sine wave mapped to [0, 1]
        i = random.randint(0,19)
        target_controls[i] = 0.5 + 0.5 * math.sin(time.time() * 2)

        # Pack 20 floats into binary payload ("20f" = 20 standard 32-bit C-floats)
        payload = struct.pack("20f", *target_controls)

        # Send to the MuJoCo socket
        sock.sendto(payload, (HOST, PORT))

        # Match control loop frequency (e.g., 100 Hz)
        time.sleep(0.01)

except KeyboardInterrupt:
    print("Stopped controller client.")
finally:
    sock.close()