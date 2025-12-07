import os
import uuid
from io import BytesIO

from PIL import Image
import torch
import torchvision.transforms as T
from flask import Flask, render_template, request, redirect, url_for

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
models_dir = os.path.join(project_root, 'models')
static_dir = os.path.join(project_root, 'static')
generated_dir = os.path.join(static_dir, 'generated')
os.makedirs(generated_dir, exist_ok=True)

app = Flask(__name__, template_folder=os.path.join(project_root, 'templates'), static_folder=static_dir)

# Model file paths
MODEL_A2B = os.path.join(models_dir, 'generator_A2B_epoch30.pth')
MODEL_B2A = os.path.join(models_dir, 'generator_B2A_epoch30.pth')


def try_load(path):
    if not os.path.isfile(path):
        return None
    data = torch.load(path, map_location='cpu')
    # Return either a module (callable) or a state_dict-like object.
    if hasattr(data, 'eval') and callable(getattr(data, 'eval')):
        try:
            data.eval()
        except Exception:
            pass
        return ('module', data)
    if isinstance(data, dict):
        return ('state_dict', data)
    return ('unknown', data)


models = {
    'A2B': try_load(MODEL_A2B),
    'B2A': try_load(MODEL_B2A),
}

preprocess = T.Compose([
    T.Resize(286),
    T.CenterCrop(256),
    T.ToTensor(),
    T.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
])


def tensor_to_pil(tensor):
    t = tensor.clone().cpu().squeeze(0)
    t = t * 0.5 + 0.5
    t = (t * 255).clamp(0, 255).byte()
    arr = t.permute(1, 2, 0).numpy()
    return Image.fromarray(arr)


def run_model_on_image(model_entry, pil_image):
    if model_entry is None:
        return None, 'Model file not found.'
    kind, obj = model_entry
    if kind == 'module':
        img_t = preprocess(pil_image).unsqueeze(0)
        with torch.no_grad():
            out = obj(img_t)
        # model may return tensor or tuple
        if isinstance(out, (list, tuple)):
            out = out[0]
        try:
            return tensor_to_pil(out), None
        except Exception:
            return None, 'Model output could not be converted to image.'
    # If the file is a state_dict we cannot reconstruct the model here.
    return pil_image, 'Loaded a state_dict checkpoint — no architectural class available. Returning the input image as a fallback.'


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    if 'image' not in request.files:
        return redirect(url_for('index'))
    f = request.files['image']
    if f.filename == '':
        return redirect(url_for('index'))
    choice = request.form.get('direction', 'A2B')
    img = Image.open(BytesIO(f.read())).convert('RGB')
    model_entry = models.get(choice)
    result_img, message = run_model_on_image(model_entry, img)
    filename = f"{uuid.uuid4().hex}.png"
    out_path = os.path.join(generated_dir, filename)
    if result_img is None:
        # create a small placeholder image explaining the issue
        placeholder = Image.new('RGB', (256, 256), (200, 50, 50))
        placeholder.save(out_path)
        message = message or 'Unknown error during generation.'
    else:
        result_img.save(out_path)
    return render_template('result.html', filename=filename, message=message)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
