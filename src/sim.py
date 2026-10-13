import mujoco
from mjviser import Viewer
import mujoco_menagerie as mm
import socket
import struct
import json
import numpy as np
from .config import MODEL

# Load the model
model = mm.load(MODEL)
data = mujoco.MjData(model)

# Load actuator ranges from the specs file, ordered as the model's actuators
SPECS_PATH = "shadow_hand_specs.json"
with open(SPECS_PATH) as f:
    actuator_specs = json.load(f)["actuators"]
actuator_names = [model.actuator(i).name for i in range(model.nu)]
ctrl_min = np.array([actuator_specs[n]["min"] for n in actuator_names])
ctrl_max = np.array([actuator_specs[n]["max"] for n in actuator_names])

def decode_controls(normalized):
    """Map normalized [0, 1] controls to each actuator's real range."""
    normalized = np.clip(np.asarray(normalized), 0.0, 1.0)
    return ctrl_min + normalized * (ctrl_max - ctrl_min)

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
        d.ctrl[:20] = decode_controls(controls)
    except BlockingIOError:
        pass # Proceed with simulation if no new packet arrived
    
    # Advance the physics simulation
    mujoco.mj_step(m, d)

# Launch the web viewer
# This blocks the main thread, manages real-time syncing, and hosts the UI on port 8080
Viewer(model, data, step_fn=custom_step_fn).run()