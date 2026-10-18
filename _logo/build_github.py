# -*- coding: utf-8 -*-
"""Baut den logo!-Seh-Begleiter für GitHub Pages (jelle-schule.github.io/logo/).

Aufruf im Repo-Hauptordner:   python3 _logo/build_github.py
Datenquelle:                  logo/logo_daten.json   (wird vom täglichen Lauf ergänzt)
Erzeugt:
  logo/index.html             neueste Sendung (fester Link für den QR-Code)
  logo/verzeichnis.html       alle Sendungen, durchsuchbar (für die Lehrkraft)
  logo/woche.html             die letzten 7 Sendungen für Schüler
  logo/archiv/logo_JJJJ-MM-TT.html (+ .pdf)   jeder Seh-Begleiter einzeln
"""
import os, sys, json, html

HIER = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HIER)
LOGO = os.path.join(REPO, "logo")
ARCH = os.path.join(LOGO, "archiv")
sys.path.insert(0, HIER)
import build_logo as B
import seh_begleiter as S

B.HIER = LOGO  # lade() liest logo_daten.json von hier
E = html.escape

NAV_CSS = """
<style>
.navleiste{max-width:760px;margin:0 auto;padding:0 16px 28px;display:flex;flex-wrap:wrap;gap:10px;font-family:system-ui,sans-serif;font-size:15px}
.navleiste a{color:inherit;border:1.5px solid currentColor;border-radius:999px;padding:6px 14px;text-decoration:none;opacity:.8}
.navleiste a:hover{opacity:1}
</style>"""

def seite(s, nav, titel):
    body = S.artifact_html(s).replace("<title>logo! Seh-Begleiter</title>", "")
    return ('<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{E(titel)}</title><meta name="robots" content="noindex">{NAV_CSS}</head><body>'
            + body + f'<nav class="navleiste">{nav}</nav></body></html>')

def schreibe(pfad, text):
    with open(pfad, "w", encoding="utf-8") as f:
        f.write(text)

def main():
    d = B.lade()
    ss = d["sendungen"]                      # neueste zuerst
    os.makedirs(ARCH, exist_ok=True)
    mit_fragen = [x for x in ss if any(b.get("fragen") for b in x["beitraege"])]

    # Archiv: je Sendung mit Fragen eine Seite (+ PDF zum Drucken)
    pdf_ok = True
    try:
        import reportlab  # noqa
    except ImportError:
        pdf_ok = False
    for x in mit_fragen:
        nav = ('<a href="../">← Zur aktuellen Sendung</a>'
               + (f'<a href="logo_{x["datum"]}.pdf">Als PDF drucken</a>' if pdf_ok else "")
               + '<a href="../verzeichnis.html">Alle Sendungen</a>')
        schreibe(os.path.join(ARCH, f"logo_{x['datum']}.html"),
                 seite(x, nav, f"logo! vom {B.de_datum(x['datum'])} – Seh-Begleiter"))
        pdfp = os.path.join(ARCH, f"logo_{x['datum']}.pdf")
        if pdf_ok and (x is mit_fragen[0] or not os.path.exists(pdfp)):
            S.pdf(x, pdfp)

    # Hauptseite: immer die neueste Sendung (ohne eigene Fragen greifen allgemeine W-Fragen)
    neu = ss[0]
    nav = ((f'<a href="archiv/logo_{neu["datum"]}.pdf">Als PDF drucken</a>' if pdf_ok and neu in mit_fragen else "")
           + '<a href="verzeichnis.html">Ältere Sendungen</a>'
           + '<a href="woche.html">Die ganze Woche</a>'
           + '<a href="../">Zur Startseite</a>')
    schreibe(os.path.join(LOGO, "index.html"), seite(neu, nav, "logo! Seh-Begleiter"))

    # Verzeichnis (Lehrkraft) – Archiv-Links auf neuen Ordner umbiegen
    v = B.verzeichnis(d).replace("Seh_Begleiter_Archiv/logo_", "archiv/logo_")
    v = v.replace("Diese Datei wird automatisch aus logo_daten.json erzeugt.",
                  'Wird jeden Abend automatisch aktualisiert. <a href="./">Zur aktuellen Sendung</a>')
    schreibe(os.path.join(LOGO, "verzeichnis.html"), v)

    # Woche für Schüler
    w = ss[:7]
    if w:
        schreibe(os.path.join(LOGO, "woche.html"),
                 B.schueler(w, f"Die letzten Sendungen vom {B.de_datum(w[-1]['datum'])} bis {B.de_datum(w[0]['datum'])}"))

    print("ok:", len(ss), "Sendungen,", len(mit_fragen), "Seh-Begleiter, neueste:", neu["datum"], "| PDF:", pdf_ok)

if __name__ == "__main__":
    main()
