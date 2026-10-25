# 🛡️ Kitakaró AI – Automatikus Képcenzúrázó Alkalmazás

Egy Python-alapú webalkalmazás, amely a Hugging Face előre betanított mesterséges intelligencia modelljeit felhasználva automatikusan detektálja és kitakarja a képeken szereplő érzékeny adatokat (személyek arcát, teljes alakját vagy gépjárművek rendszámtábláit).

---

## ✨ Főbb funkciók

* **Kétmodelles AI detektálás:** Külön neurális hálózat felel a személyek és a rendszámtáblák pontos lokalizációjáért.
* **Választható célpontok:**
  * **Csak arc:** Adaptív oldalarány-számítással (portré, félalakos vagy egész alakos kép) automatikusan a fejrészre szűkíti a kitakarást.
  * **Teljes test:** A detektált személyek teljes befoglaló dobozát maszkolja.
  * **Rendszám:** Kifejezetten a járművek rendszámtábláit keresi és takarja ki.
* **3 cenzúrázási stílus (dinamikus skálázással):**
  * **Pixeles (Mozaik):** A felismert terület méretéhez igazodó mozaikos pixelizálás.
  * **Elmosás (Blur):** Dinamikus sugarú Gauss-elmosás.
  * **Fekete sáv:** Teljes kitakarás tömör fekete téglalappal.
* **Modern webes felület:** Reszponzív, chat-jellegű felület világos/sötét témával, Drag & Drop és vágólapról történő képbeillesztési támogatással.

---

## 🧠 Technológiai Stack és AI Modellek

* **Mesterséges Intelligencia (`transformers`, `torch`, `timm`):**
  * Személyek detektálása: [`facebook/detr-resnet-50`](https://huggingface.co/facebook/detr-resnet-50) (DEtection TRansformer)
  * Rendszámtáblák detektálása: [`nickmuchi/yolos-small-finetuned-license-plate-detection`](https://huggingface.co/nickmuchi/yolos-small-finetuned-license-plate-detection) (YOLOS alapú modell)
* **Képfeldolgozás (`Pillow` / `PIL`):** Bounding box koordináta-transzformációk és képszűrők alkalmazása.
* **Backend (`Flask`, `flask-cors`):** REST API végpont (`POST /censor`) a képek memóriabeli fogadására és Base64 formátumú visszaküldésére.
* **Frontend:** HTML5, CSS3, Vanilla JavaScript.

---

## 📁 A projekt felépítése

```text
├── detector.py        # AI modellek betöltése és az érzékeny koordináták kinyerése
├── censor.py          # Képfeldolgozási logika, fejrész-szűkítés és maszkolási effektusok
├── app.py             # Flask webszerver és API végpont a frontend kiszolgálásához
├── index.html         # Webes felhasználói felület
└── requirements.txt   # Szükséges Python csomagok listája