from PIL import Image
import warnings
import torch
import timm
from transformers import logging, pipeline

# 0. Felesleges Hugging Face és Python figyelmeztetések elnémítása
logging.set_verbosity_error()
warnings.filterwarnings("ignore")

# 1. Modellek betöltése globálisan
print("AI modellek betöltése folyamatban...")

# Általános modell személyek detektálásához
person_detector = pipeline("object-detection", model="facebook/detr-resnet-50")

# Specifikus modell rendszámtáblák detektálásához
plate_detector = pipeline(
    "object-detection",
    model="nickmuchi/yolos-small-finetuned-license-plate-detection",
)

print("Modellek sikeresen betöltve!")


def detect_sensitive_areas(image_path, confidence_threshold=0.7):
  """Kielemez egy képet mindkét modellel, és visszaadja a cenzúrázandó területek
  koordinátáit egy egységes listában.
  """
  # Kép megnyitása Pillow segítségével
  image = Image.open(image_path).convert("RGB")

  sensitive_boxes = []

  # --- 1. Modell futtatása: Személyek keresése ---
  person_results = person_detector(image)
  for item in person_results:
    # Csak a 'person' címkéket keressük, amelyek elérik a megbízhatósági küszöböt
    if item["label"] == "person" and item["score"] >= confidence_threshold:
      sensitive_boxes.append({
          "type": "person",
          "score": round(item["score"], 2),
          "box": item["box"],  # Formátum: {'xmin': ..., 'ymin': ..., 'xmax': ..., 'ymax': ...}
      })

  # --- 2. Modell futtatása: Rendszámok keresése ---
  plate_results = plate_detector(image)
  for item in plate_results:
    if item["score"] >= confidence_threshold:
      sensitive_boxes.append({
          "type": "license_plate",
          "score": round(item["score"], 2),
          "box": item["box"],
      })

  return sensitive_boxes


# --- Tesztelési rész ---
if __name__ == "__main__":
  teszt_kep = "teszt.jpg"
  try:
    talalatok = detect_sensitive_areas(teszt_kep)
    print(f"\nÖsszesen {len(talalatok)} érzékeny területet találtam:")
    for t in talalatok:
      print(
          f"- Típus: {t['type']} | Biztonság: {t['score']} | Koordináták:"
          f" {t['box']}"
      )
  except FileNotFoundError:
    print(
        f"Hiba: A '{teszt_kep}' nem található."
    )