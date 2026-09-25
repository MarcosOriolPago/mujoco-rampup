import mujoco
import mujoco.viewer
import mujoco_menagerie as mm
import time
import socket
import struct


model = mm.load('wonik_allegro') 
data = mujoco.MjData(model)
print(data.ctrl)


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 5005))
sock.setblocking(False)

# The Allegro hand has 16 actuators. We expect 16 floats from the ZCU104.
payload_size = struct.calcsize("16f") 

with mujoco.viewer.launch_passive(model, data) as viewer:
    while viewer.is_running():
        step_start = time.time()
        
        try:
            # 3. Receive 16-DoF command from the NeoCorAl SNN UDP stream
            packet, addr = sock.recvfrom(payload_size)
            controls = struct.unpack("16f", packet)
            
            # Apply to the 16 Allegro actuators
            data.ctrl[:16] = controls
            
        except BlockingIOError:
            pass # Proceed with simulation if no new packet arrived
            
        mujoco.mj_step(model, data)
        viewer.sync()
        
        # 4. Extract state (16 joint angles) and send back to Zynq for RL reward evaluation
        # current_positions = data.qpos[:16]
        # state_packet = struct.pack("16f", *current_positions)
        # sock.sendto(state_packet, addr)

        # Enforce simulation step time
        time_until_next_step = model.opt.timestep - (time.time() - step_start)
        if time_until_next_step > 0:
            time.sleep(time_until_next_step)
