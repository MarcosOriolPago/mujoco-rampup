import math
import socket
import struct
import time
import random

# IP address of the machine running MuJoCo (use "127.0.0.1" if on the same PC)
HOST = "127.0.0.1"
PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Example: 20 joint control values (e.g., target angles in radians)
target_controls = [0.0] * 20

try:
    while True:
        # Update your target controls here
        # Example: set index 0 to oscillate over time
        i = random.randint(0,19)
        target_controls[i] = math.sin(time.time() * 2)

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