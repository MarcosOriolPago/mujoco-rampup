# MuJoCo ramp-up: Shadow Hand

A small, practical starting point for [MuJoCo](https://mujoco.org). It contains:

1. **A tutorial notebook** (`tutorial/mujoco_rampup.ipynb`) that teaches the basics step by step:
   starting a simulation, reading data from it, and actuating it. It goes from a pendulum to the Shadow Hand.
2. **A working simulator** (`src/`): the Shadow Hand running in a web viewer and controlled over UDP.
   It's a template for driving a MuJoCo model from an external program or device.

```
            ┌──────────────┐
  XML ───▶  │   MjModel    │  (constant: bodies, joints, actuators...)
            └──────┬───────┘
                   │
  data.ctrl ──▶ mj_step(model, data) ──▶ data.qpos, data.qvel, data.sensordata, ...
  (you write)                             (you read)
```

## Setup

Requires Python ≥ 3.10.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The Shadow Hand model is downloaded automatically by `mujoco-menagerie` the first time it is loaded.

## Learning path

### 1. Tutorial notebook (start here)

```bash
jupyter lab tutorial/mujoco_rampup.ipynb
```

| Section | You learn to… |
|---|---|
| 0. Three things to know | tell `MjModel` (description), `MjData` (state) and `mj_step` apart |
| 1. Starting a simulation | write a model in XML, load it, set an initial state, step it |
| 2. Reading data | read `qpos`/`qvel`, body and site positions, and sensors by name; know when you need `mj_forward` |
| 3. Rendering | get images and videos with `mujoco.Renderer` |
| 4. Actuating | use `motor` vs `position` actuators and write your own control loop |
| 5. The Shadow Hand | load a real robot from Menagerie, explore its actuators, make it grasp, send normalized commands |
| 6. Going interactive | use the viewers and run this repo's simulator |
| 7–8. Cheat sheet & links | find the API in one place and where to learn more |

Every section ends with small 🧪 **Try it** exercises.

### 2. Run the live simulator

From the project root (the modules use relative imports, and the specs file path is relative to the working directory):

```bash
python -m src.sim          # start the simulator + viewer at http://localhost:8080
python -m src.controller   # in another terminal, send test controls
```

Then try the final exercise in the notebook: write your own controller client.

## The simulator in `src/`

```
controller.py  ──UDP :5005 (20 × float32)──▶  sim.py  ──▶  MuJoCo + web viewer (:8080)
```

### `src/sim.py`: simulator

- Loads the model named in `src/config.py` (`shadow_hand`) from `mujoco_menagerie`.
- Reads each actuator's control range from `shadow_hand_specs.json`.
- Listens (non-blocking) for UDP packets on `0.0.0.0:5005`. Each packet is
  20 little-endian `float32` values (`struct` format `"20f"`), one per actuator,
  in the model's actuator order.
- Values are **normalized to `[0, 1]`**: they are clipped to that range and
  mapped linearly to each actuator's `[min, max]` before being written to
  `data.ctrl`.
- If no packet arrived, the last controls are kept and physics keeps stepping.
- Serves an interactive viewer (`mjviser`) on port 8080.

### `src/controller.py`: example client

A test client that sends a control packet to `127.0.0.1:5005` at ~100 Hz.
All actuators start at the middle of their range (`0.5`). Each tick it picks a random actuator and
sets it to `0.5 + 0.5·sin(2t)`. Change `HOST` to the simulator machine's IP when sending from another device.

### `src/save_joint_ranges.py`

Regenerates `shadow_hand_specs.json` (joint and actuator ranges) from the model:

```bash
python -m src.save_joint_ranges
```

### Actuator order

| # | Actuator | # | Actuator | # | Actuator | # | Actuator |
|---|---|---|---|---|---|---|---|
| 0 | `lh_A_WRJ2` | 5 | `lh_A_THJ2` | 10 | `lh_A_MFJ4` | 15 | `lh_A_RFJ0` |
| 1 | `lh_A_WRJ1` | 6 | `lh_A_THJ1` | 11 | `lh_A_MFJ3` | 16 | `lh_A_LFJ5` |
| 2 | `lh_A_THJ5` | 7 | `lh_A_FFJ4` | 12 | `lh_A_MFJ0` | 17 | `lh_A_LFJ4` |
| 3 | `lh_A_THJ4` | 8 | `lh_A_FFJ3` | 13 | `lh_A_RFJ4` | 18 | `lh_A_LFJ3` |
| 4 | `lh_A_THJ3` | 9 | `lh_A_FFJ0` | 14 | `lh_A_RFJ3` | 19 | `lh_A_LFJ0` |

WR = wrist, TH = thumb, FF/MF/RF/LF = first/middle/ring/little finger.
`*J0` actuators drive a tendon that flexes the finger's last two joints together.

## Troubleshooting

**The Jupyter kernel dies when rendering (Linux).** MuJoCo's default rendering backend (GLFW) can crash
in some environments. VS Code installed as a **snap** is one of them: it injects its own GNOME settings
and the kernel aborts. The notebook avoids this by selecting the headless EGL backend before
importing `mujoco`:

```python
import os
os.environ.setdefault("MUJOCO_GL", "egl")  # must run before `import mujoco`
import mujoco
```

Use the same lines in your own scripts that use `mujoco.Renderer`. If EGL isn't available, try `osmesa`
(slow, CPU only). You can also install VS Code from the `.deb` package instead of the snap.

## Further resources

- [MuJoCo documentation](https://mujoco.readthedocs.io)
- [MJCF XML reference](https://mujoco.readthedocs.io/en/stable/XMLreference.html)
- [Official MuJoCo tutorial notebook](https://github.com/google-deepmind/mujoco/blob/main/python/tutorial.ipynb)
- [MuJoCo Menagerie](https://github.com/google-deepmind/mujoco_menagerie): robot models
