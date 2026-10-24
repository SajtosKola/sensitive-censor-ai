from detector import detect_sensitive_areas
from PIL import Image, ImageDraw, ImageFilter


def apply_censor_to_boxes(
    image,
    sensitive_boxes,
    target="arc",
    censor_mode="blur",
    blur_radius=25,
):
    """
    A kapott PIL Image objektumon cenzúrázza a megadott koordinátájú területeket.
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

        # Szűrés a választott célpont (target) alapján
        if target in ("arc", "test") and obj_type != "person":
            continue
        if target == "rendszam" and obj_type != "license_plate":
            continue

        xmin = int(box["xmin"])
        ymin = int(box["ymin"])
        xmax = int(box["xmax"])
        ymax = int(box["ymax"])

        # Személyeknél a doboz dinamikus szűkítése a fejrészre az oldalarány alapján
        if obj_type == "person" and target == "arc":
          height = ymax - ymin
          width = xmax - xmin
          aspect_ratio = height / max(1, width)

          if aspect_ratio < 1.35:
            # Közeli portré / szelfi (a doboz nagy része maga a fej és a váll)
            head_ratio = 0.65
            side_margin = 0.10
          elif aspect_ratio < 2.0:
            # Félalakos (deréktól vagy mellkastól felfelé látszó) kép
            head_ratio = 0.40
            side_margin = 0.12
          else:
            # Egész alakos álló személy
            head_ratio = 0.25
            side_margin = 0.15

          ymax = ymin + int(height * head_ratio)
          xmin = xmin + int(width * side_margin)
          xmax = xmax - int(width * side_margin)
        if xmax > xmin and ymax > ymin:
          crop_box = (xmin, ymin, xmax, ymax)

          if censor_mode == "blur":
            # Dinamikus Gauss-elmosás: nagy/közeli arcoknál a doboz méretével arányosan nő a sugár
            region = censored_image.crop(crop_box)
            w, h = region.size
            dynamic_blur = max(blur_radius, int(max(w, h) * 0.18))
            blurred_region = region.filter(
              ImageFilter.GaussianBlur(radius=dynamic_blur)
            )
            censored_image.paste(blurred_region, crop_box)

          elif censor_mode == "pixelate":
            # Dinamikus mozaikolás: közeli arcoknál is legfeljebb 6-7 darab óriási tömbre osztja a területet
            region = censored_image.crop(crop_box)
            w, h = region.size
            block_size = max(16, int(min(w, h) / 6))
            small_w = max(1, w // block_size)
            small_h = max(1, h // block_size)
            temp = region.resize((small_w, small_h), Image.NEAREST)
            pixelated_region = temp.resize((w, h), Image.NEAREST)
            censored_image.paste(pixelated_region, crop_box)

          elif censor_mode == "black":
            # Teljesen fekete kitakarás
            draw.rectangle([xmin, ymin, xmax, ymax], fill="black")

    return censored_image


def process_image(
    input_image_path,
    output_image_path=None,
    confidence_threshold=0.4,
    target="arc",
    censor_mode="blur",
    blur_radius=25,
):
    """Fő vezérlőfüggvény a webes felület számára."""
    detections = detect_sensitive_areas(
        input_image_path, confidence_threshold=confidence_threshold
    )
    original_image = Image.open(input_image_path).convert("RGB")

    result_image = apply_censor_to_boxes(
        original_image,
        detections,
        target=target,
        censor_mode=censor_mode,
        blur_radius=blur_radius,
    )

    if output_image_path:
        result_image.save(output_image_path)

    wanted_type = "license_plate" if target == "rendszam" else "person"
    filtered_detections = [
        d for d in detections if d.get("type") == wanted_type
    ]

    return result_image, filtered_detections


# --- Tesztelési rész ---
if __name__ == "__main__":
    bemenet = "teszt3.jpg"
    valasztott_mod = "black"
    valasztott_cel = "rendszam"  # 'arc', 'test', vagy 'rendszam'
    kimenet = f"teszt_{valasztott_cel}_{valasztott_mod}.jpg"

    try:
        print(f"Kép feldolgozása ({valasztott_cel}, {valasztott_mod}): {bemenet}...")
        kesz_kep, talalatok = process_image(
            bemenet, kimenet, target=valasztott_cel, censor_mode=valasztott_mod
        )
        print(f"Sikeres cenzúrázás! Kitakart elemek száma: {len(talalatok)}")
        print(f"Eredmény elmentve ide: {kimenet}")
    except FileNotFoundError:
        print(f"Hiba: Nem található a '{bemenet}' fájl a mappában!")