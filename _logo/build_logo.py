# -*- coding: utf-8 -*-
"""Baut aus logo_daten.json das Lehrer-Verzeichnis und die Schülerseite.
Aufruf (im Ordner logo_Archiv):  python3 build_logo.py [--heute <Ordner Heute>]
"""
import json, os, sys, datetime, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HIER = os.path.dirname(os.path.abspath(__file__))
THEMEN = ["Schule & Bildung", "Regierung & Parlament", "Wahlen & Demokratie",
          "Protest & Beteiligung", "Europa", "Welt & Internationales",
          "Krieg & Konflikte", "Gewalt & Sicherheit", "Flucht & Migration",
          "Wirtschaft & Preise", "Verkehr & Mobilität", "Umwelt, Klima & Energie",
          "Gesellschaft & Zusammenleben", "Digitales & Medien", "Gesundheit & Ernährung",
          "Geschichte", "Natur & Wissen", "Sport", "Kultur & Feiertage"]

def lade():
    with open(os.path.join(HIER, "logo_daten.json"), encoding="utf-8") as f:
        d = json.load(f)
    s = {x["datum"]: x for x in d["sendungen"]}          # Duplikate je Datum vermeiden
    d["sendungen"] = sorted(s.values(), key=lambda x: x["datum"], reverse=True)
    for x in d["sendungen"]:
        for b in x["beitraege"]:
            b["themen"] = [t for t in b.get("themen", []) if t in THEMEN] or ["Gesellschaft & Zusammenleben"]
    return d

def de_datum(iso):
    y, m, t = iso.split("-")
    return f"{int(t)}.{int(m)}.{y}"

CSS = """
:root{--terra:#8a4b2a;--terra-hell:#faf6f2;--linie:#e2d4c6;--text:#2b2b2b;--grau:#6b5e55;--gruen:#3d8f5b;--gelb:#c99a2e;--rot:#c0554e;--karte:#fff;--bg:#fdfbf9}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--terra:#d99067;--terra-hell:#2a211c;--linie:#4a3b32;--text:#eee6df;--grau:#b8a99d;--karte:#1f1915;--bg:#161210}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font-family:"Segoe UI",Verdana,Arial,sans-serif;font-size:15px;line-height:1.4}
.wrap{max-width:980px;margin:0 auto;padding:16px}
header{border-bottom:3px solid var(--terra);padding:14px 16px 8px;max-width:980px;margin:0 auto}
header h1{margin:0;color:var(--terra);font-size:24px}
header .sub{color:var(--grau);font-size:13px}
a{color:var(--terra)}
.chip{display:inline-block;border:1.5px solid var(--terra);color:var(--terra);background:var(--karte);border-radius:14px;padding:3px 10px;margin:3px 3px 0 0;font-size:12.5px;cursor:pointer;user-select:none}
.chip.an{background:var(--terra);color:#fff}
.chip small{opacity:.75}
.tag{display:inline-block;background:var(--terra-hell);border:1px solid var(--linie);color:var(--grau);border-radius:10px;padding:0 7px;font-size:11.5px;margin:2px 3px 0 0}
.pol{display:inline-block;background:var(--terra);color:#fff;border-radius:10px;padding:0 7px;font-size:11px;margin-left:6px;vertical-align:1px}
.sendung{background:var(--karte);border:1.5px solid var(--linie);border-left:6px solid var(--terra);border-radius:8px;padding:10px 14px;margin:12px 0}
.sendung h2{margin:0 0 4px;font-size:16px;color:var(--terra);display:flex;flex-wrap:wrap;gap:8px;align-items:baseline;justify-content:space-between}
.sendung h2 a{font-size:13px;font-weight:normal}
.beitrag{padding:6px 0;border-top:1px dashed var(--linie)}
.beitrag:first-of-type{border-top:none}
.beitrag b{font-size:14.5px}
.beitrag .kurz{color:var(--grau);font-size:13.5px}
input[type=search]{width:100%;font-size:16px;padding:9px 12px;border:2px solid var(--terra);border-radius:8px;background:var(--karte);color:var(--text)}
.leiste{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin:8px 0;font-size:13.5px}
.treffer{color:var(--grau);font-size:13px}
footer{color:var(--grau);font-size:12px;margin:24px 0 8px;border-top:1px dashed var(--linie);padding-top:6px}
@media print{.leiste,input,.chips{display:none}.sendung{break-inside:avoid}body{background:#fff}}
"""

def verzeichnis(d):
    daten = json.dumps(d["sendungen"], ensure_ascii=False)
    themen = json.dumps(THEMEN, ensure_ascii=False)
    stand = datetime.date.today().strftime("%d.%m.%Y")
    return f"""<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>logo! Verzeichnis</title><style>{CSS}</style></head><body>
<header><h1>logo!-Verzeichnis</h1><div class="sub">Alle logo!-Sendungen mit Datum, Beiträgen und Themen · zum Suchen und Wiederfinden für GPG · Stand {stand}</div></header>
<div class="wrap">
<input type="search" id="q" placeholder="Suchen: z. B. Schule, Bundestag, Wahl, Preise, 03.10. …" autofocus>
<div class="leiste"><label><input type="checkbox" id="nurpol"> nur politische Beiträge</label>
<a href="#" id="reset">Filter zurücksetzen</a><span class="treffer" id="treffer"></span></div>
<div class="chips" id="chips"></div>
<div id="liste"></div>
<footer>Quelle: ZDF/KiKA, logo.de. Die Videos liegen in der ZDF-Mediathek; ältere Sendungen können dort nach einiger Zeit offline gehen. Diese Datei wird automatisch aus logo_daten.json erzeugt.</footer>
</div>
<script>
const S={daten}, T={themen};
let aktiv=new Set();
const esc=s=>String(s).replace(/[&<>"]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}})[c]);
const deD=iso=>{{const[y,m,t]=iso.split('-');return (+t)+'.'+(+m)+'.'+y}};
const deD2=iso=>{{const[y,m,t]=iso.split('-');return t+'.'+m+'.'+y}};
function zaehle(){{const z={{}};S.forEach(s=>s.beitraege.forEach(b=>b.themen.forEach(t=>z[t]=(z[t]||0)+1)));return z}}
function chips(){{const z=zaehle();document.getElementById('chips').innerHTML=T.filter(t=>z[t]).map(t=>`<span class="chip${{aktiv.has(t)?' an':''}}" data-t="${{esc(t)}}">${{esc(t)}} <small>${{z[t]}}</small></span>`).join('');
 document.querySelectorAll('.chip').forEach(c=>c.onclick=()=>{{const t=c.dataset.t;aktiv.has(t)?aktiv.delete(t):aktiv.add(t);chips();zeige()}})}}
function zeige(){{const q=document.getElementById('q').value.trim().toLowerCase(),pol=document.getElementById('nurpol').checked;let n=0,out='';
 S.forEach(s=>{{const kopf=(s.wochentag+' '+deD(s.datum)+' '+deD2(s.datum)).toLowerCase();
  const bs=s.beitraege.filter(b=>{{if(pol&&!b.politisch)return false;if(aktiv.size&&!b.themen.some(t=>aktiv.has(t)))return false;
   if(!q)return true;return (b.titel+' '+b.kurz+' '+b.themen.join(' ')+' '+kopf).toLowerCase().includes(q)}});
  if(!bs.length)return;n+=bs.length;
  out+=`<div class="sendung"><h2><span>${{esc(s.wochentag)}}, ${{deD(s.datum)}} <small style="font-weight:normal;color:var(--grau)">· ${{esc(s.zeit||'')}} Uhr</small></span><span><a href="${{esc(s.url)}}" target="_blank" rel="noopener">▶ Sendung ansehen</a>${{s.beitraege.some(b=>b.fragen)?` · <a href="Seh_Begleiter_Archiv/logo_${{s.datum}}.html" target="_blank">✎ Seh-Begleiter</a>`:''}}</span></h2>`+
  bs.map(b=>`<div class="beitrag"><b>${{esc(b.titel)}}</b>${{b.politisch?'<span class="pol">Politik</span>':''}}<div class="kurz">${{esc(b.kurz)}}${{b.link?` · <a href="${{esc(b.link)}}" target="_blank" rel="noopener">Artikel/Erklärvideo</a>`:''}}</div>${{b.themen.map(t=>`<span class="tag">${{esc(t)}}</span>`).join('')}}</div>`).join('')+`</div>`}});
 document.getElementById('liste').innerHTML=out||'<p>Keine Treffer.</p>';document.getElementById('treffer').textContent=n+' Beiträge gefunden'}}
document.getElementById('q').oninput=zeige;document.getElementById('nurpol').onchange=zeige;
document.getElementById('reset').onclick=e=>{{e.preventDefault();aktiv.clear();document.getElementById('q').value='';document.getElementById('nurpol').checked=false;chips();zeige()}};
chips();zeige();
</script></body></html>"""

def schueler(sendungen, titel_zusatz):
    karten = []
    for s in sendungen:
        bs = "".join(
            f'<div class="beitrag"><b>{html.escape(b["titel"])}</b>'
            f'{"<span class=pol>Politik</span>" if b.get("politisch") else ""}'
            f'<div class="kurz">{html.escape(b["kurz"])}'
            + (f' · <a href="{html.escape(b["link"])}" target="_blank" rel="noopener">mehr dazu</a>' if b.get("link") else "")
            + "</div></div>" for b in s["beitraege"])
        karten.append(f'<div class="sendung"><h2><span>{s["wochentag"]}, {de_datum(s["datum"])}</span>'
                      f'<a class="knopf" href="{html.escape(s["url"])}" target="_blank" rel="noopener">▶ Video ansehen</a></h2>{bs}</div>')
    extra = """.knopf{background:var(--terra);color:#fff!important;text-decoration:none;border-radius:20px;padding:6px 14px;font-size:14px!important}
.auftrag{background:var(--terra-hell);border:1.5px solid var(--terra);border-radius:8px;padding:10px 14px;margin-top:14px}
body{font-size:16px}.beitrag b{font-size:16px}.beitrag .kurz{font-size:14.5px}"""
    return f"""<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>logo! der Woche</title><style>{CSS}{extra}</style></head><body>
<header><h1>logo! – Nachrichten für dich</h1><div class="sub">{titel_zusatz} · Tippe auf „Video ansehen“, um die Sendung zu schauen. Beiträge mit dem Zeichen <span class="pol">Politik</span> haben mit Politik zu tun.</div></header>
<div class="wrap">{''.join(karten)}
<div class="auftrag"><b>Dein Auftrag:</b> Schau dir eine Sendung an. Welche Nachricht war für dich neu? Erkläre sie einem Mitschüler in zwei Sätzen.</div>
<footer>Quelle: ZDF/KiKA, logo.de · GPG Klasse 6, Mittelschule Mammendorf</footer></div></body></html>"""

def heute_pdf(s, ziel):
    """Ein-Seiten-PDF der neuesten Sendung mit anklickbaren Links (öffnet auf iPad/OneDrive/Teams direkt)."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    fd = "/usr/share/fonts/truetype/dejavu/"
    pdfmetrics.registerFont(TTFont("DV", fd + "DejaVuSans.ttf"))
    pdfmetrics.registerFont(TTFont("DVB", fd + "DejaVuSans-Bold.ttf"))
    pdfmetrics.registerFontFamily("DV", normal="DV", bold="DVB")
    terra, hell = colors.HexColor("#8a4b2a"), colors.HexColor("#faf6f2")
    st = lambda n, **k: ParagraphStyle(n, fontName=k.pop("f", "DV"), **k)
    h1 = st("h1", f="DVB", fontSize=22, leading=27, textColor=terra)
    sub = st("sub", fontSize=11, leading=14, textColor=colors.HexColor("#6b5e55"))
    tit = st("tit", f="DVB", fontSize=14, leading=18, spaceBefore=4)
    txt = st("txt", fontSize=12, leading=16)
    knopf = st("kn", f="DVB", fontSize=15, leading=19, textColor=colors.white, alignment=1)
    E = html.escape
    url = E(s["url"])
    teile = [Paragraph(f"logo! vom {s['wochentag']}, {de_datum(s['datum'])}", h1),
             Paragraph(f"Kindernachrichten von ZDF/KiKA · Sendung um {s.get('zeit','19:50')} Uhr", sub), Spacer(1, 5*mm)]
    k = Table([[Paragraph(f'<a href="{url}" color="white">▶  Hier tippen: Video ansehen</a>', knopf)]], colWidths=[120*mm])
    k.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), terra), ("TOPPADDING", (0,0), (-1,-1), 9),
                           ("BOTTOMPADDING", (0,0), (-1,-1), 9), ("ROUNDEDCORNERS", [8,8,8,8])]))
    teile += [k, Spacer(1, 6*mm)]
    for i, b in enumerate(s["beitraege"], 1):
        pol = ' <font color="#8a4b2a" size="10">[Politik]</font>' if b.get("politisch") else ""
        mehr = f' <a href="{E(b["link"])}" color="#8a4b2a"><u>mehr dazu</u></a>' if b.get("link") else ""
        zeile = Table([[Paragraph(f"{i}. {E(b['titel'])}{pol}", tit)], [Paragraph(E(b["kurz"]) + mehr, txt)]], colWidths=[170*mm])
        zeile.setStyle(TableStyle([("LINEBEFORE", (0,0), (0,-1), 3, terra), ("LEFTPADDING", (0,0), (-1,-1), 8)]))
        teile += [zeile, Spacer(1, 3*mm)]
    auftrag = Table([[Paragraph("<b>Dein Auftrag:</b> Schau dir die Sendung an. Welche Nachricht war für dich neu? "
                                "Erkläre sie einem Mitschüler in zwei Sätzen.", txt)]], colWidths=[170*mm])
    auftrag.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), hell), ("BOX", (0,0), (-1,-1), 1.2, terra),
                                 ("TOPPADDING", (0,0), (-1,-1), 7), ("BOTTOMPADDING", (0,0), (-1,-1), 7)]))
    teile += [Spacer(1, 4*mm), auftrag, Spacer(1, 6*mm),
              Paragraph(f'Quelle: ZDF/KiKA, logo.de · Link zur Sendung: <a href="{url}" color="#8a4b2a">{url}</a>', sub)]
    SimpleDocTemplate(ziel, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm, topMargin=18*mm, bottomMargin=15*mm,
                      title=f"logo! vom {de_datum(s['datum'])}", author="GPG Mittelschule Mammendorf").build(teile)

def main():
    d = lade()
    with open(os.path.join(HIER, "logo_Verzeichnis.html"), "w", encoding="utf-8") as f:
        f.write(verzeichnis(d))
    neueste = d["sendungen"][:7]
    if neueste:
        von, bis = de_datum(neueste[-1]["datum"]), de_datum(neueste[0]["datum"])
        with open(os.path.join(HIER, "logo_fuer_Schueler.html"), "w", encoding="utf-8") as f:
            f.write(schueler(neueste, f"Die letzten Sendungen vom {von} bis {bis}"))
    # Wochenausgaben (Mo–So) für Schulmanager
    os.makedirs(os.path.join(HIER, "Schueler_Wochen"), exist_ok=True)
    wochen = {}
    for s in d["sendungen"]:
        j, kw, _ = datetime.date.fromisoformat(s["datum"]).isocalendar()
        wochen.setdefault((j, kw), []).append(s)
    for (j, kw), ss in wochen.items():
        with open(os.path.join(HIER, "Schueler_Wochen", f"logo_KW{kw:02d}_{j}.html"), "w", encoding="utf-8") as f:
            f.write(schueler(ss, f"Kalenderwoche {kw} / {j}"))
    # Tages-PDF der neuesten Sendung (fester Dateiname, wird jeden Abend ersetzt)
    import sys, shutil
    if d["sendungen"]:
        import seh_begleiter
        neu_s = d["sendungen"][0]
        # Online-Seite (wird vom Artifact-Tool unter dem festen QR-Link veröffentlicht)
        with open(os.path.join(HIER, "logo_heute_artifact.html"), "w", encoding="utf-8") as f:
            f.write(seh_begleiter.artifact_html(neu_s))
        # Archiv: je Sendung mit Fragen eine interaktive HTML + druckbare PDF (für Wiederholungen)
        arch = os.path.join(HIER, "Seh_Begleiter_Archiv")
        os.makedirs(arch, exist_ok=True)
        for x in d["sendungen"]:
            if any(b.get("fragen") for b in x["beitraege"]):
                with open(os.path.join(arch, f"logo_{x['datum']}.html"), "w", encoding="utf-8") as f:
                    f.write(seh_begleiter.standalone_html(x))
                pdfp = os.path.join(arch, f"logo_{x['datum']}.pdf")
                if x is neu_s or not os.path.exists(pdfp):
                    seh_begleiter.pdf(x, pdfp)
        # Ordner "Heute": nur die interaktive HTML der neuesten Sendung (fester Name, wird ersetzt)
        if "--heute" in sys.argv:
            ziel = sys.argv[sys.argv.index("--heute") + 1]
            with open(os.path.join(ziel, "logo_heute.html"), "w", encoding="utf-8") as f:
                f.write(seh_begleiter.standalone_html(neu_s))
            print("heute:", os.path.join(ziel, "logo_heute.html"))
    print("ok:", len(d["sendungen"]), "Sendungen,", sum(len(s["beitraege"]) for s in d["sendungen"]), "Beiträge")

if __name__ == "__main__":
    main()
