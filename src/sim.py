import mujoco
from mjviser import Viewer
import mujoco_menagerie as mm
import socket
import struct
from .config import MODEL

# Load the model
model = mm.load('shadow_hand') 
data = mujoco.MjData(model)

# Setup UDP Socket for the Zynq board
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 5005))
sock.setblocking(False)
payload_size = struct.calcsize("20f")

# Define a custom step function to intercept UDP before advancing physics
def custom_step_fn(m, d):
    try:
        packet, addr = sock.recvfrom(payload_size)
        controls = struct.unpack("20f", packet)
        d.ctrl[:20] = controls
    except BlockingIOError:
        pass # Proceed with simulation if no new packet arrived
    
    # Advance the physics simulation
    mujoco.mj_step(m, d)

# Launch the web viewer
# This blocks the main thread, manages real-time syncing, and hosts the UI on port 8080
Viewer(model, data, step_fn=custom_step_fn).run()