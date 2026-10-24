import base64
import io
import os
import tempfile

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from PIL import Image

from censor import process_image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
CORS(app)

STYLE_MAP = {"pixel": "pixelate", "blur": "blur", "bar": "black"}
VALID_TARGETS = {"arc", "test", "rendszam"}


@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/censor", methods=["POST"])
def censor():
    # --- Bemenet ellenőrzése ---
    file = request.files.get("image")
    if file is None or file.filename == "":
        return jsonify({"error": "Hiányzik a kép (image mező)."}), 400

    target = request.form.get("target", "arc")
    style = request.form.get("style", "pixel")

    if target not in VALID_TARGETS:
        return jsonify({"error": f"Ismeretlen target: {target}"}), 400
    if style not in STYLE_MAP:
        return jsonify({"error": f"Ismeretlen style: {style}"}), 400

    censor_mode = STYLE_MAP[style]

    # --- Kép beolvasása memóriából ---
    try:
        original = Image.open(io.BytesIO(file.read()))
        original.load()
        original = original.convert("RGB")
    except Exception:
        return jsonify({"error": "A feltöltött fájl nem érvényes kép."}), 400

    # Ideiglenes fájlba mentés és feldolgozás
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name
        original.save(tmp_path, format="PNG")

        result_img, detections = process_image(
            tmp_path,
            output_image_path=None,
            confidence_threshold=0.4,
            target=target,
            censor_mode=censor_mode,
            blur_radius=25,
        )
    except Exception as e:
        return jsonify({"error": f"Feldolgozási hiba: {e}"}), 500
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

    # --- Base64 PNG válasz előállítása ---
    result_img = result_img.convert("RGB")
    buf = io.BytesIO()
    result_img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    return jsonify({"image": b64, "detections": len(detections)})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)