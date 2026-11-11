**Mesterséges Intelligencia Használatának Dokumentációja**

A projekt megvalósítása során generatív mesterséges intelligencia eszközök segítségét vettük igénybe a tervezési, kódolási és hibakeresési fázisokban.

**Alkalmazott MI-eszközök**

Google Gemini: Backend architektúra megtervezése, modellintegráció (`transformers`), képmanipulációs algoritmusok (`Pillow`) kidolgozása, Flask integráció refaktorálása.

Claude Code: A kezdeti egyoldalas webes kezelőfelület (HTML, CSS, kliensoldali JavaScript) vázlatának elkészítése.

**Feladatok, amelyekhez az MI-t igénybe vettük:**

Megfelelő, nyílt forráskódú Hugging Face objektumdetektáló modellek felkutatása és kiválasztása.
A két különálló modell (`facebook/detr-resnet-50` és `nickmuchi/yolos-small-finetuned-license-plate-detection`) közös futtatási logikájának megírása.
Részleges képcenzúrázási eljárások (Gauss-elmosás, mozaikos pixelizálás, fekete kitakarás) implementálása.
Képarány-alapú adaptív fejrész-szűkítés és dinamikus szűrőerősség-számítás.
Frontend-backend integrációs hibák (duplikált képfeldolgozás, hiányzó paraméterátadások, memóriaszivárgások) feltárása és javítása.

**Fontosabb promptok, kapott eredmények és módosítások**

**Kétmodelles AI detektáló modul (`detector.py`)**

Prompt:

> „Készíts egy moduláris Python komponenst (`detector.py`), amely két különböző Hugging Face modellt integrál a `transformers` könyvtár `pipeline` felületén keresztül: a `facebook/detr-resnet-50` modellt személyek (`person`), valamint a `nickmuchi/yolos-small-finetuned-license-plate-detection` modellt rendszámtáblák detektálására. Írj egy `detect_sensitive_areas(image_path, confidence_threshold)` függvényt, amely beolvas egy képet Pillow segítségével, lefuttatja mindkét modellt, és egy egységes adatszerkezetben (típus, konfidencia, `xmin, ymin, xmax, ymax` koordináták) adja vissza az érzékeny területek listáját.”

Kapott eredmény: 

Egy működő Python szkript, amely egymás után hívja meg a két modellt és egységes dict-listába gyűjti a detektált bounding boxokat.

Ellenőrzés és módosítás:

-Telepítési környezeti ütközések és PATH hibák elhárítása a virtuális környezetben (`requirements.txt`).

-A Hugging Face és a `transformers` felesleges konzolfigyelmeztetéseinek (warningok) elnémítása a tiszta terminálkimenet érdekében.

**Képmanipuláció és geometriai maszkolás (`censor.py`)**

Prompt:

> „Fejlessz egy képszerkesztő modult (`censor.py`) a Pillow (PIL) könyvtár használatával, amely a kapott befoglaló dobozok (`bounding box`) helyén elvégzi a kitakarást. Támogasson háromféle cenzúrázási módot: Gauss-elmosást (`blur`), mozaikos pixelizálást (`pixelate`) és fekete sávos kitakarást (`black`). Személyek esetén valósíts meg benne egy olyan geometriai logikát, amely a megtalált doboz magasság-szélesség arányából megkülönbözteti a közeli portrét, a félalakos és az egész alakos képet, és arc kitakarása esetén adaptívan a fejrészre szűkíti a koordinátákat.”

Kapott eredmény:  

A koordináták kivágását, szűrését és visszaragasztását végző függvények, valamint a képarány-alapú vágási logika.

Ellenőrzés és módosítás:

-Tesztelés során kiderült, hogy nagy felbontású, közeli portréknál a fix blokkméret miatt az arc kivehető maradt. Emiatt az elmosás sugarát és a pixelizálás kockaméretét a kivágott doboz méretéhez arányos dinamikus képlettel egészítettük ki.

-Kijavítottunk egy behúzási hibát, ami miatt kimeneti útvonal nélkül futtatva a szűrt lista nem jött létre (`UnboundLocalError`).

**Rendszerintegráció és API vezérlés (`app.py` és frontend)**

Prompt:

> „Optimalizáld a `censor.py` modul `process_image` vezérlőfüggvényét a webes bekötéshez: egészítsd ki célpont szerinti szűréssel (`target`: 'arc', 'test', 'rendszam'), hogy csak a kiválasztott objektumtípusokat maszkolja, a többit hagyja élesen. Távolítsd el a Flask szerverből a redundáns kép-visszaállítási logikát.”

Kapott eredmény:  

Egyszerűsített `POST /censor` végpont és célpont alapú szűrés a ciklusban (`continue` ágak).

Ellenőrzés és módosítás:

-Észrevettük, hogy az ideiglenes fájl törlése után a kód duplán hívta meg a feldolgozást, ami `FileNotFoundError`-t okozott; ezt megszüntettük.

-Az `index.html`-ben kivezettük a felesleges demó módot, és javítottuk a felület „Mégse” gombjának CSS hibáját (`[hidden]{ display: none !important; }`).

**Felelősségteljes AI használat**

A generált forráskódokat lépésről lépésre átnéztük, működésüket értjük:

-Tisztában vagyunk a `transformers` pipeline-ok és a tensor-műveletek működésével.

-Átlátjuk a Pillow `crop`, `filter` és `paste` metódusainak koordináta-kezelését.

-Ismerjük a Flask REST API működését, a többkomponensű űrlapadatok (`multipart/form-data`) kezelését és a Base64 kódolású képtovábbítást.
