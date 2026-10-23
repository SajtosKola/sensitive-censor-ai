from detector import detect_sensitive_areas
from PIL import Image, ImageFilter


def apply_blur_to_boxes(
    image, sensitive_boxes, blur_radius=25, only_head_for_person=True
):
  """A kapott PIL Image objektumon elhomályosítja a megadott koordinátájú területeket.
  Ha only_head_for_person=True, akkor a személyeknél csak a felső fejrészt
  maszkolja.
  """
  censored_image = image.copy()

  for item in sensitive_boxes:
    box = item["box"]
    obj_type = item["type"]

    xmin = int(box["xmin"])
    ymin = int(box["ymin"])
    xmax = int(box["xmax"])
    ymax = int(box["ymax"])

    # Ha személyt találtunk, a teljes test helyett csak a fejrészre szűkítjük a dobozt
    if obj_type == "person" and only_head_for_person:
      height = ymax - ymin
      width = xmax - xmin

      # A magasság felső 25%-a (fejrész)
      ymax = ymin + int(height * 0.25)

      # Oldalról 15-15% szűkítés, hogy a vállakat ne homályosítsa feleslegesen
      xmin = xmin + int(width * 0.15)
      xmax = xmax - int(width * 0.15)

    # Biztonsági ellenőrzés: csak akkor vágunk, ha érvényes a téglalap mérete
    if xmax > xmin and ymax > ymin:
      crop_box = (xmin, ymin, xmax, ymax)
      region = censored_image.crop(crop_box)
      blurred_region = region.filter(
          ImageFilter.GaussianBlur(radius=blur_radius)
      )
      censored_image.paste(blurred_region, crop_box)

  return censored_image


def process_image(
    input_image_path,
    output_image_path=None,
    confidence_threshold=0.7,
    blur_radius=25,
    only_head_for_person=True,
):
  """Fő vezérlőfüggvény (ezt hívja majd meg a webes felület is).
  Összeköti az AI detektálást és a képmaszkolást.
  """
  detections = detect_sensitive_areas(
      input_image_path, confidence_threshold=confidence_threshold
  )
  original_image = Image.open(input_image_path).convert("RGB")

  result_image = apply_blur_to_boxes(
      original_image,
      detections,
      blur_radius=blur_radius,
      only_head_for_person=only_head_for_person,
  )

  if output_image_path:
    result_image.save(output_image_path)

  return result_image, detections


# --- Tesztelési rész ---
if __name__ == "__main__":
  bemenet = "teszt2.jpg"
  kimenet = "teszt_cenzurazott.jpg"

  try:
    print(f"Kép feldolgozása (csak fejrész és rendszám): {bemenet}...")
    kesz_kep, talalatok = process_image(bemenet, kimenet)
    print(f"Sikeres cenzúrázás! Kitakart elemek száma: {len(talalatok)}")
    print(f"Eredmény elmentve ide: {kimenet}")
  except FileNotFoundError:
    print(f"Hiba: Nem található a '{bemenet}' fájl a mappában!")