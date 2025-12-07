# Image <> Sketch Translation

This repository contains a small image-to-sketch / sketch-to-image generator project.

**Project layout**

- `models/` : trained model files (generators)
- `notebooks/` : analysis and demo notebooks (moved `image_generation.ipynb`)
- `screenshots/` : example outputs used in this README
- `src/` : (optional) source code and helper scripts
- `docs/` : (optional) documentation

**Included files (moved)**

- `models/generator_A2B_epoch30.pth` — generator A->B (renamed from `G_A2B_epoch30.pth`)
- `models/generator_B2A_epoch30.pth` — generator B->A (renamed from `G_B2A_epoch30.pth`)
- `notebooks/image_generation.ipynb` — the demo notebook (moved from `gen_q1.ipynb`)
- `screenshots/img_to_sketch.jpg` — example output (image -> sketch)
- `screenshots/sketch_to_img.jpg` — example output (sketch -> image)

**Quick start**

1. (Optional) Create a virtual environment and activate it.

```powershell
# from repository root (q1)
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Open the demo notebook:

```powershell
jupyter notebook notebooks\image_generation.ipynb
```

3. Notes about models:

- The model files live in `models/`. If your models are large, consider using Git LFS before committing: `git lfs install; git lfs track "models/*.pth"`.

**Models and Losses**

- **Overall architecture:** This project implements a CycleGAN for unpaired image-to-image translation between face photos and hand-drawn sketches.
- **Generators:** Two ResNet-based generators are used:
	- `G_A2B` (photo -> sketch)
	- `G_B2A` (sketch -> photo)
	- Each generator uses an encoder + several ResNet blocks (6 by default) + decoder and outputs 3-channel RGB images with a `tanh` activation.
- **Discriminators:** Two PatchGAN discriminators are used to evaluate realism at the patch level:
	- `D_A` (real vs fake photos)
	- `D_B` (real vs fake sketches)
- **Loss functions:**
	- **Adversarial loss:** MSE loss (least-squares GAN) is used for both discriminators and generator adversarial objectives (implemented as `nn.MSELoss()` in the notebook).
	- **Cycle-consistency loss:** L1 loss (`nn.L1Loss()`) is applied to enforce A -> B -> A and B -> A -> B consistency.
	- **Total generator loss:** adversarial losses + 10.0 * cycle losses (i.e. cycle weight = 10.0 in the training notebook).
- **Optimizers / training details:**
	- Optimizers: Adam with `lr=0.0002` and `betas=(0.5, 0.999)`.
	- Default training in the notebook: 30 epochs over a small subset (1000 samples used in the demo).
- **Checkpoint files included:**
	- `models/generator_A2B_epoch30.pth` — trained `G_A2B` checkpoint
	- `models/generator_B2A_epoch30.pth` — trained `G_B2A` checkpoint

These details match the implementation in `notebooks/image_generation.ipynb` and the Flask demo in `src/` which load the saved generator checkpoints.

**Screenshots / examples**

Image to sketch:

![Image to Sketch](screenshots/img_to_sketch.jpg)

Sketch to image:

![Sketch to Image](screenshots/sketch_to_img.jpg)

