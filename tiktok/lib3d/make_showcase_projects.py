#!/usr/bin/env python3
"""Creates tiktok/sc_<id>/ projects (spec.json, scene.py, comp.py, assets/product.png) for the showcase v2 videos."""
import json, os, shutil
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
IMG = os.path.join(ROOT, "live_studio", "img")
SUP = "Nahrungsergänzungsmittel. Kein Ersatz für eine ausgewogene, abwechslungsreiche Ernährung."
M = dict(ZAYN="XcorKvP1KdIM2TL5vtZ1", FIETE="kHfXYCwbOq00KgBegten", KERMIN="ucRSf046SQyHREQLH4JR", ALEX="JuAR5aASfomx0YTiNRiF",
         VALENA="prhcTCMZO2tEReVq7XuJ", LOLA="gSZiss4v1BGsE1cTgoWF", JENNA="mPoK2MnknRxMK1ue0VTP")
MAN = lambda shirt, tee=(0.93, 0.92, 0.88), hair="short", beard="stubble", hc=(0.15, 0.09, 0.05), skin=(0.82, 0.6, 0.47): dict(
    female=False, hair=hair, beard=beard, tee=tee, shirt=shirt, hair_col=hc, skin=skin, open_shirt=True)
WOMAN = lambda top, hc=(0.55, 0.38, 0.2), skin=(0.86, 0.66, 0.54): dict(
    female=True, hair="long", beard=None, tee=top, shirt=top, shirt2=tuple(c * 0.8 for c in top), hair_col=hc, skin=skin, open_shirt=False)

P = [
 dict(id="ninja", n=17, title="NINJA DUALZONE", badge="NINJA · DUALZONE HEISSLUFTFRITTEUSE", voice_id=M["KERMIN"],
      voice="[excited] Ninja DualZone Heißluftfritteuse! [annoyed] Pommes oder Hähnchen? Ich kann mich nie entscheiden. [excited] Warum nicht beides? Zwei Körbe, zwei Gerichte, alles gleichzeitig fertig! Black Friday: 20 Prozent günstiger, nur 139,99 Euro! Tipp unten links!",
      kw=dict(problem="Pommes", use="Warum", price="Black", cta="Tipp"), room="kitchen", mood="annoyed", action="show", container="plate",
      accent="#e8473c", h=0.24, thick=0.24, round=0.2, price="139,99 €", pct="-20 %", deal="BLACK FRIDAY -20 %", char=MAN((0.85, 0.3, 0.25)),
      pills=[["Pommes", "POMMES ODER HÄHNCHEN?", "#333333"], ["Zwei", "2 KÖRBE · 2 GERICHTE", "#e8473c"]],
      card_lines=["2 Körbe · 2 Gerichte gleichzeitig", "Black Friday: 139,99 € (-20 %)"], end_sub="BLACK FRIDAY: 139,99 € · -20 %"),
 dict(id="chunky", n=18, title="CHUNKY FLAVOUR", badge="MORE NUTRITION · STEVIA CHUNKY FLAVOUR", voice_id=M["JENNA"],
      voice="[excited] More Stevia Chunky Flavour! [sighs] Mein Quark schmeckt nach... nichts. [excited] Ein Löffel Chunky drüber, und plötzlich schmeckt er nach Dessert! Die Sorte kannst du wählen. Gerade nur 11,39 Euro statt 11,99! Tipp unten links!",
      kw=dict(problem="Mein", use="Ein", price="Gerade", cta="Tipp"), room="kitchen", mood="sad", action="pour", container="bowl", liquid="#f5f1e8", particle="#e05a6a",
      accent="#e0506a", h=0.2, price="11,39 €", old="11,99 €", pct="-5 %", char=WOMAN((0.95, 0.75, 0.3)),
      pills=[["nichts", "LANGWEILIG…", "#555555"], ["Dessert", "SCHMECKT NACH DESSERT", "#e0506a"], ["Sorte", "SORTE WÄHLBAR", "#333333"]],
      card_lines=["Topping für Quark & Joghurt", "Jetzt 11,39 € statt 11,99 €"], end_sub="NUR 11,39 € STATT 11,99 €"),
 dict(id="creatin", n=19, title="PROFUEL CREATIN", badge="PROFUEL · CREATIN MONOHYDRAT", voice_id=M["ZAYN"],
      voice="[excited] ProFuel Creatin Monohydrat! [sighs] Montag, Push Day, und mein Shaker ist leer. [excited] Also: ein Löffel in den Shaker, schütteln, trinken. Kreatin erhöht die körperliche Leistung bei Schnellkrafttraining. Ab 10,46 Euro! Tipp unten links!",
      kw=dict(problem="Montag", use="Also", price="Kreatin", cta="Tipp"), room="gym", mood="sad", action="pour_drink", container="shaker", liquid="#eeeeee", particle="#ffffff",
      accent="#2f7de1", h=0.26, price="ab 10,46 €", char=MAN((0.12, 0.12, 0.14), tee=(0.2, 0.45, 0.85)),
      notice="Kreatin erhöht die körperliche Leistung bei Schnellkrafttraining (ab 3 g täglich). " + SUP,
      pills=[["Push", "PUSH DAY", "#2f7de1"], ["Shaker,", "AB IN DEN SHAKER", "#222222"]],
      card_lines=["Kreatin-Pulver · Black-Friday-Deal", "ab 10,46 €"], end_sub="BLACK FRIDAY: AB 10,46 €"),
 dict(id="rocka", n=20, title="ROCKA PROTEIN SHAKE", badge="ROCKA NUTRITION · PROTEIN SHAKE", voice_id=M["VALENA"],
      voice="[excited] Rocka Protein Shake, Chai Latte! [sighs] Ich wollte ins Café, aber mein Konto sagt nein. [excited] Also: Shake mixen, trinken, schmeckt wie im Café! Gerade ab 12,74 Euro statt 14,24! Tipp unten links!",
      kw=dict(problem="Ich", use="Also", price="Gerade", cta="Tipp"), room="cafe", mood="sad", action="pour_drink", container="glass", liquid="#d9b48a", particle="#c79a6a",
      accent="#c9772b", h=0.26, price="ab 12,74 €", old="14,24 €", pct="-11 %", char=WOMAN((0.35, 0.55, 0.45)),
      pills=[["Konto", "KONTO SAGT NEIN", "#444444"], ["schmeckt", "WIE IM CAFÉ", "#c9772b"]],
      card_lines=["z. B. Chai Latte", "ab 12,74 € statt 14,24 €"], end_sub="AB 12,74 € STATT 14,24 €"),
 dict(id="snackxl", n=21, title="SNACKBOX XL", badge="WEIHNACHTS-SNACKBOX XL · 23 SNACKS", voice_id=M["ALEX"],
      voice="[excited] Die Weihnachts-Snackbox XL! 23 verschiedene Snacks und Schokoladen. [laughs] Eigentlich wollte ich sie verschenken. Dann hab ich probiert. [excited] Jetzt ist sie halb leer! Nur 19,89 Euro! Tipp unten links!",
      kw=dict(problem="Eigentlich", use="Dann", price="Nur", cta="Tipp"), room="xmas", mood="excited", action="show",
      accent="#d63a3a", h=0.3, thick=0.16, round=0.15, price="19,89 €", char=MAN((0.2, 0.45, 0.3), tee=(0.85, 0.2, 0.2)),
      pills=[["verschenken", "ZUM VERSCHENKEN…", "#2f7a4a"], ["halb", "…HALB LEER!", "#d63a3a"]],
      card_lines=["23 Snacks & Schokoladen", "nur 19,89 €"], end_sub="NUR 19,89 €"),
 dict(id="bourbon", n=22, title="BOURBON-VANILLE HONIG", badge="IMKERMEISTER KRÜGER · HONIG", voice_id=M["LOLA"],
      voice="[softly] Honig mit echter Bourbon-Vanille. [sighs] Mein Tee war immer so langweilig. [excited] Ein Löffel rein, und plötzlich schmeckt er wie ein Dessert! Nur 8 Euro, und bei zwei Gläsern sparst du 5 Prozent. Tipp unten links!",
      kw=dict(problem="Mein", use="Ein", price="Nur", cta="Tipp"), room="kitchen", mood="sad", action="pour", container="mug", liquid="#c8894a", particle="#e0a020",
      accent="#e0a020", h=0.2, price="8,00 €", pct="2× -5 %", char=WOMAN((0.6, 0.75, 0.9)),
      pills=[["Tee", "LANGWEILIGER TEE", "#555555"], ["Dessert", "WIE EIN DESSERT", "#e0a020"]],
      card_lines=["Honig mit Bourbon-Vanille", "8 € · Kauf 2, spar 5 %"], end_sub="8 € · KAUF 2, SPAR 5 %"),
 dict(id="geschmack", n=23, title="GESCHMACKSBOMBE", badge="GESCHMACKSBOMBE · BANANENSPLIT", voice_id=M["ZAYN"],
      voice="[excited] Die Geschmacksbombe, Bananensplit! [sighs] Mein Quark war einfach traurig. [excited] Ein Löffel Geschmacksbombe rein, und er schmeckt wie Eisdiele! Gerade nur 11,40 Euro. Tipp unten links!",
      kw=dict(problem="Mein", use="Ein", price="Gerade", cta="Tipp"), room="kitchen", mood="sad", action="pour", container="bowl", liquid="#f3efe6", particle="#f0d060",
      accent="#f0b020", h=0.18, price="11,40 €", char=MAN((0.25, 0.3, 0.55)),
      pills=[["traurig", "TRAURIGER QUARK", "#555555"], ["Eisdiele", "WIE EISDIELE!", "#f0b020"]],
      card_lines=["Geschmackspulver, z. B. Bananensplit", "nur 11,40 €"], end_sub="NUR 11,40 €"),
 dict(id="kissen", n=24, title="NACKENKISSEN", badge="ONLYSELL · ERGONOMISCHES NACKENKISSEN", voice_id=M["ALEX"],
      voice="[excited] Das ergonomische Nackenkissen von ONLYSELL! [groans] Mein Nacken, jeden Morgen: Aua. [excited] Jetzt schlaf ich wie ein Baby: geformt für Rücken- und Seitenschläfer. Gerade nur 19,25 Euro! Tipp unten links!",
      kw=dict(problem="Mein", use="Jetzt", price="Gerade", cta="Tipp"), room="bedroom", mood="pain", action="hug",
      accent="#5b6ee8", h=0.3, thick=0.1, round=0.6, price="19,25 €", char=MAN((0.45, 0.5, 0.75), tee=(0.85, 0.88, 0.95), hair="messy"),
      pills=[["Aua", "AUA!", "#d33333"], ["Rücken", "RÜCKEN- & SEITENSCHLÄFER", "#5b6ee8"]],
      card_lines=["Für Rücken- & Seitenschläfer", "nur 19,25 €"], end_sub="NUR 19,25 €"),
 dict(id="elusa384", n=25, title="ELUSA 384", badge="ELUSA · 384 EXTRAIT DE PARFUM", voice_id=M["VALENA"],
      voice="[softly] Elusa 384, Extrait de Parfum. [sighs] Mein alter Duft? Einfach nur langweilig. [excited] Ein Sprüher: Honig, Gewürze, warm wie eine Umarmung! Gerade 20 Prozent günstiger, ab 23,70 Euro! Tipp unten links!",
      kw=dict(problem="Mein", use="Ein", price="Gerade", cta="Tipp"), room="dressing", mood="sad", action="spray", particle="#f5efe0",
      accent="#c08a3a", h=0.26, thick=0.06, round=0.2, price="ab 23,70 €", pct="-20 %", char=WOMAN((0.12, 0.1, 0.12), hc=(0.25, 0.15, 0.1)),
      pills=[["langweilig", "LANGWEILIG…", "#555555"], ["Honig", "HONIG & GEWÜRZE", "#c08a3a"]],
      card_lines=["Extrait de Parfum", "ab 23,70 € (-20 %)"], end_sub="AB 23,70 € · -20 %"),
 dict(id="mexican", n=26, title="CHILI-ADVENTSKALENDER", badge="MEXICAN TEARS · CHILISAUCEN-ADVENTSKALENDER", voice_id=M["ZAYN"],
      voice="[excited] Ein Adventskalender, aber mit Chilisaucen: Mexican Tears! [laughs] Jeden Tag eine neue Sauce. Tür eins: noch okay. Tür zwei: Feuer! [excited] Für 79,90 Euro. Tipp unten links!",
      kw=dict(problem="Jeden", use="Tür", price="Für", cta="Tipp"), room="kitchen", mood="excited", action="fire", particle="#dddddd",
      accent="#e2261c", h=0.32, thick=0.1, round=0.15, price="79,90 €", char=MAN((0.15, 0.15, 0.18), tee=(0.9, 0.85, 0.75), beard="full"),
      pills=[["eins", "TÜR 1: OKAY", "#333333"], ["Feuer", "TÜR 2: FEUER!", "#e2261c"]],
      card_lines=["Jeden Tag eine neue Sauce", "79,90 €"], end_sub="79,90 €"),
 dict(id="zerosauce", n=27, title="INLEAD ZERO SAUCEN", badge="INLEAD · ZERO SAUCEN", voice_id=M["JENNA"],
      voice="[excited] Inlead Zero Saucen! [shocked] Pommes ohne Sauce? Niemals! [excited] Hier: verschiedene Sorten, alle mit zero Zucker. Einfach dippen und genießen. Im Set ab 16,99 Euro! Tipp unten links!",
      kw=dict(problem="Pommes", use="Hier", price="Im", cta="Tipp"), room="kitchen", mood="annoyed", action="show", container="plate",
      accent="#18a6e0", h=0.26, thick=0.08, round=0.15, price="ab 16,99 €", char=WOMAN((0.9, 0.45, 0.35)),
      pills=[["Niemals", "NIEMALS!", "#d33333"], ["zero", "ZERO ZUCKER", "#18a6e0"]],
      card_lines=["Verschiedene Sorten · zero Zucker", "im Set ab 16,99 €"], end_sub="IM SET AB 16,99 €"),
 dict(id="wraps", n=28, title="HIGH PROTEIN WRAPS", badge="INLEAD · HIGH PROTEIN WRAPS", voice_id=M["KERMIN"],
      voice="[excited] Inlead High Protein Wraps! [sighs] Mittagspause, aber nur zehn Minuten Zeit? [excited] Sechs vegane Wraps, 21 Gramm Protein: füllen, rollen, reinbeißen! Und das für nur 4,99 Euro! Tipp unten links!",
      kw=dict(problem="Mittagspause", use="6", price="Und", cta="Tipp"), room="office", mood="tired", action="show",
      accent="#1aa39a", h=0.28, thick=0.05, round=0.3, price="4,99 €", char=MAN((0.3, 0.35, 0.45), tee=(0.95, 0.95, 0.95)),
      pills=[["10", "NUR 10 MINUTEN?", "#555555"], ["Protein", "21 G PROTEIN · VEGAN", "#1aa39a"]],
      card_lines=["6 vegane Wraps · 21 g Protein", "nur 4,99 €"], end_sub="NUR 4,99 €"),
 dict(id="hair", n=29, title="HAIR SERUM", badge="HAIR SERUM · BIOTIN & ROSMARIN", voice_id=M["ALEX"],
      voice="[excited] Das Hair Serum mit Biotin! [sighs] Meine Kopfhaut fühlt sich an wie Wüste. [excited] Also: Rosmarin- und Ginseng-Extrakt, Kollagen und Vitamin B6, einfach einmassieren. Für Männer und Frauen. Gerade nur 19,95 Euro! Tipp unten links!",
      kw=dict(problem="Meine", use="Also", price="Gerade", cta="Tipp"), room="bath", mood="sad", action="apply", particle="#dff0ff",
      accent="#2c9c6a", h=0.28, thick=0.05, round=0.3, price="19,95 €", char=MAN((0.25, 0.5, 0.4)),
      pills=[["Wüste", "KOPFHAUT = WÜSTE", "#c98a3a"], ["Rosmarin", "BIOTIN · ROSMARIN · GINSENG", "#2c9c6a"]],
      card_lines=["Biotin · Rosmarin · Ginseng", "nur 19,95 €"], end_sub="NUR 19,95 €"),
 dict(id="flavourup", n=30, title="FLAVOUR UP", badge="PROFUEL · FLAVOUR UP CHOCO MILKY", voice_id=M["LOLA"],
      voice="[excited] ProFuel Flavour Up, Choco Milky! [sighs] Joghurt pur? Ehrlich, langweilig. [excited] Ein Löffel Flavour Up rein, und es schmeckt nach Kindheit! Ab 12,88 Euro statt 13,56! Tipp unten links!",
      kw=dict(problem="Joghurt", use="Ein", price="Ab", cta="Tipp"), room="kitchen", mood="sad", action="pour", container="bowl", liquid="#f5f2ea", particle="#6b3d22",
      accent="#8a5230", h=0.22, thick=0.12, round=0.3, price="ab 12,88 €", old="13,56 €", pct="-5 %", char=WOMAN((0.55, 0.4, 0.75)),
      pills=[["langweilig", "LANGWEILIG…", "#555555"], ["Kindheit", "SCHMECKT NACH KINDHEIT", "#8a5230"]],
      card_lines=["Geschmackspulver, z. B. Choco Milky", "ab 12,88 € statt 13,56 €"], end_sub="AB 12,88 € STATT 13,56 €"),
 dict(id="pizza", n=31, title="PROTEIN-PIZZABODEN", badge="MORE TASTE · HIGH-PROTEIN PIZZABODEN", voice_id=M["KERMIN"],
      voice="[excited] Pizza-Abend, aber mit Protein! [sighs] Normale Pizza, und danach direkt Sofa-Koma. [excited] Der High-Protein Pizzaboden von More Taste: belegen, backen, fertig! Gerade nur 14,99 Euro statt 16,19! Tipp unten links!",
      kw=dict(problem="Normale", use="Der", price="Gerade", cta="Tipp"), room="kitchen", mood="tired", action="show", container="pizza",
      accent="#7b4fd0", h=0.28, thick=0.04, round=0.3, price="14,99 €", old="16,19 €", pct="-7 %", char=MAN((0.55, 0.3, 0.7)),
      pills=[["Koma", "SOFA-KOMA", "#555555"], ["belegen", "BELEGEN · BACKEN · FERTIG", "#7b4fd0"]],
      card_lines=["High-Protein Pizzaboden", "14,99 € statt 16,19 €"], end_sub="14,99 € STATT 16,19 €"),
 dict(id="wabe", n=32, title="WABENHONIG", badge="DEUTSCHER WABENHONIG", voice_id=M["VALENA"],
      voice="[softly] Echter deutscher Wabenhonig, direkt in der Wabe! [sighs] Ich wusste nicht, was ich verschenken soll. [excited] Jetzt weiß ich's: Honig, so wie die Bienen ihn machen! Für 22 Euro. Tipp unten links!",
      kw=dict(problem="Ich", use="Jetzt", price="Für", cta="Tipp"), room="kitchen", mood="sad", action="show",
      accent="#e8a317", h=0.28, thick=0.08, round=0.2, price="22,00 €", char=WOMAN((0.3, 0.5, 0.35), hc=(0.75, 0.55, 0.3)),
      pills=[["verschenken", "GESCHENK-IDEE?", "#555555"], ["Bienen", "WIE VON DEN BIENEN", "#e8a317"]],
      card_lines=["Honig direkt in der Wabe", "22,00 €"], end_sub="22,00 €"),
 dict(id="richcreamy", n=33, title="RICH & CREAMY", badge="MORE NUTRITION · RICH & CREAMY", voice_id=M["JENNA"],
      voice="[excited] More Rich and Creamy, Dark Chocolate! [sighs] Mein Kaffee? Wässrig und traurig. [excited] Jetzt: noch cremiger, noch schokoladiger! Mein Barista ist offiziell eifersüchtig. Gerade 20 Prozent günstiger: 35,99 Euro! Tipp unten links!",
      kw=dict(problem="Mein", use="Jetzt", price="Gerade", cta="Tipp"), room="cafe", mood="sad", action="pour_drink", container="glass", liquid="#6b4430", particle="#4a2c1c",
      accent="#b04a7a", h=0.26, price="35,99 €", pct="-20 %", char=WOMAN((0.95, 0.9, 0.85)),
      pills=[["Wässrig", "WÄSSRIG & TRAURIG", "#555555"], ["Barista", "BARISTA: EIFERSÜCHTIG", "#b04a7a"]],
      card_lines=["Protein Iced Coffee, z. B. Dark Chocolate", "35,99 € (-20 %)"], end_sub="35,99 € · -20 %"),
 dict(id="zerupcoffee", n=34, title="ZERUP FÜR KAFFEE", badge="MORE NUTRITION · ZERUP COFFEE", voice_id=M["FIETE"],
      voice="[excited] More Zerup für Kaffee! [sighs] Mein Bürokaffee schmeckt nach Pappe. [excited] Ein Spritzer Zerup Cinnamon, und er schmeckt wie im Coffeeshop! Null Zucker. Gerade nur 6,15 Euro statt 6,99! Tipp unten links!",
      kw=dict(problem="Mein", use="Ein", price="Gerade", cta="Tipp"), room="office", mood="tired", action="pour_drink", container="mug", liquid="#5a3a24", particle="#b07040",
      accent="#c0603a", h=0.26, price="6,15 €", old="6,99 €", pct="-12 %", char=MAN((0.35, 0.4, 0.5), tee=(0.95, 0.95, 0.95)),
      pills=[["Pappe", "SCHMECKT NACH PAPPE", "#555555"], ["Null", "0 ZUCKER", "#c0603a"]],
      card_lines=["z. B. Cinnamon · 0 Zucker", "6,15 € statt 6,99 €"], end_sub="6,15 € STATT 6,99 €"),
 dict(id="gofit", n=35, title="ZERO SYRUP", badge="GOFITNESS · ZERO SYRUP 65 ML", voice_id=M["LOLA"],
      voice="[excited] GoFitness Zero Syrup! [sighs] Wasser trinken? Ja, aber es ist so langweilig. [excited] Ein Spritzer, und es schmeckt nach Wassermelone! Null Zucker, null Kalorien, vegan. Nur 5,19 Euro, bei drei Flaschen 5 Prozent sparen! Tipp unten links!",
      kw=dict(problem="Wasser", use="Ein", price="Nur", cta="Tipp"), room="gym", mood="sad", action="pour_drink", container="glass", liquid="#ff8a96", particle="#ff4060",
      accent="#ff4060", h=0.24, thick=0.06, round=0.3, price="5,19 €", pct="3× -5 %", char=WOMAN((0.15, 0.6, 0.6)),
      pills=[["langweilig", "LANGWEILIG…", "#555555"], ["Null", "0 ZUCKER · 0 KCAL · VEGAN", "#ff4060"]],
      card_lines=["0 Zucker · 0 Kalorien · vegan", "5,19 € · Kauf 3, spar 5 %"], end_sub="5,19 € · KAUF 3, SPAR 5 %"),
]

SCENE = '''import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "lib3d"))
import showcase; showcase.main(HERE)
'''
COMP = '''import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "lib3d"))
import showcase_comp; showcase_comp.main(HERE)
'''
if __name__ == "__main__":
    for p in P:
        d = os.path.join(ROOT, "sc_" + p["id"]); os.makedirs(os.path.join(d, "assets"), exist_ok=True)
        spec = dict(p); spec["out"] = f'{p["n"]}_{p["id"]}_3d.mp4'; spec["card_title"] = p["title"]
        spec.setdefault("deal", "BLACK FRIDAY DEAL")
        old = os.path.join(d, "spec.json")
        if os.path.exists(old):
            prev = json.load(open(old))
            for k in ("frames", "captions"):
                if k in prev: spec[k] = prev[k]
        json.dump(spec, open(old, "w"), ensure_ascii=False, indent=1)
        open(os.path.join(d, "scene.py"), "w").write(SCENE); open(os.path.join(d, "comp.py"), "w").write(COMP)
        shutil.copy(os.path.join(IMG, p["id"] + ".png"), os.path.join(d, "assets", "product.png"))
        open(os.path.join(d, ".gitignore"), "w").write("out/frames/\nout/test/\nout/sfx.wav\nout/ctest_*\nout/*.log\nout/.done\n__pycache__/\n")
    print(len(P), "projects")
