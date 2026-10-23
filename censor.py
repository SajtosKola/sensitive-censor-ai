from detector import detect_sensitive_areas
from PIL import Image, ImageDraw, ImageFilter


def apply_censor_to_boxes(
    image,
    sensitive_boxes,
    censor_mode="blur",
    blur_radius=25,
    only_head_for_person=True,
):
  """
  A kapott PIL Image objektumon cenzúrázza a megadort koordinátájú területeket.
  Módok (censor_mode):
  - 'blur': Gauss-elmosás
  - 'pixelate': Mozaikos pixelizálás
  - 'black': Fekete sáv / téglalap
  """
  censored_image = image.copy()
  draw = ImageDraw.Draw(censored_image)

  for item in sensitive_boxes:
    box = item["box"]
    obj_type = item["type"]

    xmin = int(box["xmin"])
    ymin = int(box["ymin"])
    xmax = int(box["xmax"])
    ymax = int(box["ymax"])

    # Személyeknél a doboz szűkítése a fejrészre
    if obj_type == "person" and only_head_for_person:
      height = ymax - ymin
      width = xmax - xmin
      ymax = ymin + int(height * 0.25)
      xmin = xmin + int(width * 0.15)
      xmax = xmax - int(width * 0.15)

    if xmax > xmin and ymax > ymin:
      crop_box = (xmin, ymin, xmax, ymax)

      if censor_mode == "blur":
        #Gauss-elmosás
        region = censored_image.crop(crop_box)
        blurred_region = region.filter(
            ImageFilter.GaussianBlur(radius=blur_radius)
        )
        censored_image.paste(blurred_region, crop_box)

      elif censor_mode == "pixelate":
        #Mozaikos pixelizálás
        region = censored_image.crop(crop_box)
        w, h = region.size
        # Lekicsinyítés, majd visszanagyítás a legközelebbi pixel módszerrel
        small_w, small_h = max(1, w // 16), max(1, h // 16)
        temp = region.resize((small_w, small_h), Image.NEAREST)
        pixelated_region = temp.resize((w, h), Image.NEAREST)
        censored_image.paste(pixelated_region, crop_box)

      elif censor_mode == "black":
        #Teljesen fekete kitakarás
        draw.rectangle([xmin, ymin, xmax, ymax], fill="black")

  return censored_image


def process_image(
    input_image_path,
    output_image_path=None,
    confidence_threshold=0.7,
    censor_mode="blur",
    blur_radius=25,
    only_head_for_person=True,
):
  """Fő vezérlőfüggvény a webes felület számára."""
  detections = detect_sensitive_areas(
      input_image_path, confidence_threshold=confidence_threshold
  )
  original_image = Image.open(input_image_path).convert("RGB")

  result_image = apply_censor_to_boxes(
      original_image,
      detections,
      censor_mode=censor_mode,
      blur_radius=blur_radius,
      only_head_for_person=only_head_for_person,
  )

  if output_image_path:
    result_image.save(output_image_path)

  return result_image, detections


# --- Tesztelési rész ---
if __name__ == "__main__":
  bemenet = "teszt.jpg"

  # módok: 'blur', 'pixelate', 'black'
  valasztott_mod = "black"
  kimenet = f"teszt_{valasztott_mod}.jpg"

  try:
    print(
        f"Kép feldolgozása '{valasztott_mod}' módban: {bemenet}..."
    )
    kesz_kep, talalatok = process_image(
        bemenet, kimenet, censor_mode=valasztott_mod
    )
    print(f"Sikeres cenzúrázás! Kitakart elemek száma: {len(talalatok)}")
    print(f"Eredmény elmentve ide: {kimenet}")
  except FileNotFoundError:
    print(f"Hiba: Nem található a '{bemenet}' fájl a mappában!")