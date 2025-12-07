Flask demo

A lightweight Flask front-end is included at `src/app.py`. It will attempt to load the files in `models/` and serve a simple upload UI.

Run locally from the repository root (PowerShell):

```powershell
# (optional) create and activate a venv
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# run the Flask app
python src\app.py
```

Open your browser at `http://127.0.0.1:5000/` and upload an image. If the repository contains only raw state_dict checkpoints (typical for PyTorch), the server will return the input image as a fallback because the model class definition is not present in the repo.
