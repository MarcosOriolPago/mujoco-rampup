import json
import mujoco_menagerie as mm
from .config import MODEL

model = mm.load('shadow_hand')

data_to_save = {
    "joints": {},
    "actuators": {}
}

for i in range(model.njnt):
    joint_name = model.joint(i).name
    if model.jnt_limited[i]:
        jnt_range = model.jnt_range[i].tolist()
        data_to_save["joints"][joint_name] = {
            "min": jnt_range[0],
            "max": jnt_range[1]
        }
    else:
        data_to_save["joints"][joint_name] = {"min": "unlimited", "max": "unlimited"}

for i in range(model.nu):
    actuator_name = model.actuator(i).name
    if model.actuator_ctrllimited[i]:
        ctrl_range = model.actuator_ctrlrange[i].tolist()
        data_to_save["actuators"][actuator_name] = {
            "min": ctrl_range[0],
            "max": ctrl_range[1]
        }
    else:
        data_to_save["actuators"][actuator_name] = {"min": "unlimited", "max": "unlimited"}

# Guardar todo en el archivo JSON
with open("shadow_hand_specs.json", "w") as f:
    json.dump(data_to_save, f, indent=4)

print("Saved.")
