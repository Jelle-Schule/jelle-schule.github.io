# -*- coding: utf-8 -*-
"""Seh-Begleiter zur neuesten logo!-Sendung: Artifact-Seite (HTML) + druckbare PDF.
Fragen kommen aus logo_daten.json:
  beitrag["fragen"] = [{"typ":"kreuz","text":..,"optionen":[..],"mehrere":bool} | {"typ":"wort"|"satz","text":..}]
  sendung["streitfrage"] = {"text":..,"optionen":[..]}   (optional, neutral formuliert)
Fehlen Fragen, werden allgemeine W-Fragen eingesetzt."""
import html

E = html.escape
TAGE = ["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"]
MON = ["Januar","Februar","März","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember"]

def datum_lang(s):
    y, m, t = s["datum"].split("-")
    return f'{s["wochentag"]}, {int(t)}. {MON[int(m)-1]} {y}'

def fragen_von(b):
    f = b.get("fragen")
    if f:
        return f
    return [{"typ": "wort", "text": "Wo passiert das? Schreib den Ort oder das Land auf."},
            {"typ": "wort", "text": "Ein wichtiges Wort aus dem Beitrag:"}]

def streit_von(s):
    st = s.get("streitfrage")
    if st:
        return st
    return {"text": "Welche Nachricht sollten auch Erwachsene unbedingt kennen?",
            "optionen": [f'{i}. {b["titel"]}' for i, b in enumerate(s["beitraege"], 1)]}

CSS = r"""
/* Layout: ein Arbeitsblatt in einer Spalte – Kopf mit Video-Knopf, dann je Beitrag eine Station, dann "Nach dem Schauen" */
:root{
 --papier:#fbfcfd; --karte:#ffffff; --tinte:#1e2532; --leise:#5b6475; --linie:#d9dee7;
 --akzent:#8a4b2a; --akzent-hell:#f6ece6; --kreuz:#2f6f9f; --kreuz-hell:#e8f1f8; --pol:#8a4b2a;
 --display:"Baloo 2","Comic Neue",system-ui,sans-serif; --text:"Atkinson Hyperlegible",Verdana,system-ui,sans-serif;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
 --papier:#14171d; --karte:#1c2028; --tinte:#eef1f6; --leise:#a5adbb; --linie:#323947;
 --akzent:#e09a72; --akzent-hell:#2c221d; --kreuz:#7db7e3; --kreuz-hell:#1b2a37; --pol:#e09a72; color-scheme:dark}}
:root[data-theme="dark"]{
 --papier:#14171d; --karte:#1c2028; --tinte:#eef1f6; --leise:#a5adbb; --linie:#323947;
 --akzent:#e09a72; --akzent-hell:#2c221d; --kreuz:#7db7e3; --kreuz-hell:#1b2a37; --pol:#e09a72; color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--papier);color:var(--tinte);font-family:var(--text);font-size:17px;line-height:1.5;margin:0}
.blatt{max-width:760px;margin:0 auto;padding-inline:16px;padding-block:20px 40px;display:flex;flex-direction:column;gap:18px}
.kopf{display:flex;flex-direction:column;gap:6px}
.eyebrow{font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--leise)}
h1{font-family:var(--display);font-weight:700;font-size:clamp(28px,6vw,38px);line-height:1.1;margin:0;text-wrap:balance}
h1 span{color:var(--akzent)}
.video{align-self:flex-start;display:inline-flex;align-items:center;gap:10px;background:var(--akzent);color:var(--karte);text-decoration:none;
 font-family:var(--display);font-weight:600;font-size:20px;padding:10px 22px 8px;border-radius:999px;margin-top:6px}
.video:focus-visible,input:focus-visible+span{outline:3px solid var(--kreuz);outline-offset:2px}
.video svg{width:20px;height:20px;fill:currentColor}
.themen{background:var(--akzent-hell);border-radius:14px;padding:14px 16px;display:flex;flex-direction:column;gap:8px}
.themen h2,.station h2,.danach h2{font-family:var(--display);font-weight:700;margin:0;line-height:1.2}
.themen h2{font-size:20px}
.themen ol{margin:0;padding-left:1.4em;display:grid;gap:2px}
.hinweis{font-size:15px;color:var(--leise);margin:0}
.station{background:var(--karte);border:1.5px solid var(--linie);border-radius:14px;padding:14px 16px 16px;display:flex;flex-direction:column;gap:12px}
.station header{display:flex;gap:12px;align-items:flex-start}
.nr{flex:none;width:36px;height:36px;border-radius:50%;background:var(--akzent);color:var(--karte);display:grid;place-items:center;
 font-family:var(--display);font-weight:700;font-size:20px;line-height:1;padding-top:3px}
.station h2{font-size:21px;min-width:0;padding-top:3px}
.pol{display:inline-block;font-family:var(--text);font-size:12px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;
 color:var(--pol);border:1.5px solid var(--pol);border-radius:6px;padding:0 6px;margin-left:6px;vertical-align:3px}
.frage{display:flex;flex-direction:column;gap:6px}
.frage p{margin:0;font-weight:700}
.opts{display:flex;flex-wrap:wrap;gap:8px}
.opt{position:relative}
.opt input{position:absolute;opacity:0;inset:0}
.opt span{display:inline-flex;align-items:center;gap:8px;border:1.5px solid var(--linie);border-radius:10px;padding:6px 12px;cursor:pointer;background:var(--karte)}
.opt span::before{content:"";width:16px;height:16px;border:2px solid var(--kreuz);border-radius:4px;flex:none}
.opt input[type=radio]+span::before{border-radius:50%}
.opt input:checked+span{background:var(--kreuz-hell);border-color:var(--kreuz)}
.opt input:checked+span::before{background:var(--kreuz);box-shadow:inset 0 0 0 2px var(--karte)}
.zeile{width:100%;font:inherit;color:var(--tinte);background:transparent;border:none;border-bottom:2px dotted var(--leise);padding:4px 2px}
.zeile:focus{outline:none;border-bottom:2px solid var(--kreuz)}
textarea.zeile{resize:vertical;min-height:2.6em}
.danach{border-top:3px solid var(--akzent);padding-top:14px;display:flex;flex-direction:column;gap:16px}
.danach h2{font-size:24px}
.lehrer{font-size:14px;color:var(--leise);border-top:1px dashed var(--linie);padding-top:10px}
.lehrer summary{cursor:pointer}
@media (prefers-reduced-motion:no-preference){.opt span{transition:background .15s,border-color .15s}}
"""

def _frage_html(f, fid):
    t = f"<p>{E(f['text'])}</p>"
    if f["typ"] == "kreuz":
        typ = "checkbox" if f.get("mehrere") else "radio"
        hint = " <span class='hinweis'>(mehrere möglich)</span>" if f.get("mehrere") else ""
        t = f"<p>{E(f['text'])}{hint}</p>"
        opts = "".join(f'<label class="opt"><input type="{typ}" id="{fid}_{k}" name="{fid}"><span>{E(o)}</span></label>'
                       for k, o in enumerate(f["optionen"]))
        return f'<div class="frage">{t}<div class="opts">{opts}</div></div>'
    if f["typ"] == "satz":
        return f'<div class="frage"><label for="{fid}">{t}</label><textarea class="zeile" id="{fid}" rows="2"></textarea></div>'
    return f'<div class="frage"><label for="{fid}">{t}</label><input class="zeile" id="{fid}" type="text" autocomplete="off"></div>'

def artifact_html(s):
    """Seiteninhalt ohne doctype/head/body – wird vom Artifact-Tool eingerahmt."""
    bs = s["beitraege"]
    themen = "".join(f"<li>{E(b['titel'])}</li>" for b in bs)
    stationen = []
    for i, b in enumerate(bs, 1):
        pol = '<span class="pol">Politik</span>' if b.get("politisch") else ""
        fr = "".join(_frage_html(f, f"b{i}f{k}") for k, f in enumerate(fragen_von(b)))
        stationen.append(f'<section class="station" aria-labelledby="t{i}"><header><div class="nr">{i}</div>'
                         f'<h2 id="t{i}">{E(b["titel"])}{pol}</h2></header>{fr}</section>')
    nrn = [str(i) for i in range(1, len(bs) + 1)]
    st = streit_von(s)
    danach = "".join([
        _frage_html({"typ": "kreuz", "mehrere": True, "text": "Politik-Detektiv: Welche Beiträge haben mit Politik zu tun? Kreuze die Nummern an.", "optionen": nrn}, "d_pol"),
        _frage_html({"typ": "wort", "text": "Mein neues Wort heute:"}, "d_wort"),
        _frage_html({"typ": "wort", "text": "Das bedeutet:"}, "d_bed"),
        _frage_html({"typ": "kreuz", "text": st["text"], "optionen": st["optionen"]}, "d_streit"),
        _frage_html({"typ": "satz", "text": "Ich finde das, weil …"}, "d_weil"),
        _frage_html({"typ": "kreuz", "text": "Wie gut hast du die Sendung verstanden?", "optionen": ["sehr gut", "ganz gut", "nur ein bisschen"]}, "d_versteh"),
    ])
    pol_nr = ", ".join(str(i) for i, b in enumerate(bs, 1) if b.get("politisch")) or "keiner"
    return f"""<title>logo! Seh-Begleiter</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Baloo+2:wght@600;700&display=swap">
<style>{CSS}</style>
<main class="blatt">
<div class="kopf"><div class="eyebrow">Mein Seh-Begleiter · GPG</div>
<h1>logo! vom <span>{E(datum_lang(s))}</span></h1>
<a class="video" href="{E(s['url'])}" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 4.5v15l12.5-7.5z"/></svg>Video ansehen</a></div>
<section class="themen" aria-label="Die Themen"><h2>Darum geht es heute</h2><ol>{themen}</ol>
<p class="hinweis">Lies zuerst die Fragen. Dann schau das Video und beantworte sie beim Zuschauen. Du darfst auf Pause drücken.</p></section>
{''.join(stationen)}
<section class="danach" aria-label="Nach dem Schauen"><h2>Nach dem Schauen</h2>{danach}</section>
<details class="lehrer"><summary>Für die Lehrkraft</summary>
<p>Politik-Detektiv – Lösung: {pol_nr}. Die Meinungsfrage hat keine richtige Antwort (Beutelsbacher Konsens). Quelle: ZDF/KiKA, logo.de · Sendung {E(s.get('zeit','19:50'))} Uhr.</p></details>
</main>"""

def pdf(s, ziel):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    fd = "/usr/share/fonts/truetype/dejavu/"
    pdfmetrics.registerFont(TTFont("DV", fd + "DejaVuSans.ttf"))
    pdfmetrics.registerFont(TTFont("DVB", fd + "DejaVuSans-Bold.ttf"))
    pdfmetrics.registerFontFamily("DV", normal="DV", bold="DVB")
    akz, blau, grau = colors.HexColor("#8a4b2a"), colors.HexColor("#2f6f9f"), colors.HexColor("#5b6475")
    st = lambda n, **k: ParagraphStyle(n, fontName=k.pop("f", "DV"), **k)
    h1 = st("h1", f="DVB", fontSize=19, leading=23, textColor=akz)
    eb = st("eb", fontSize=8.5, leading=11, textColor=grau)
    h2 = st("h2", f="DVB", fontSize=12.5, leading=16)
    fq = st("fq", f="DVB", fontSize=10.5, leading=14)
    tx = st("tx", fontSize=10.5, leading=14)
    kl = st("kl", fontSize=8.5, leading=11, textColor=grau)
    url = E(s["url"])
    L = "_" * 62

    def frage(f):
        out = [Paragraph(E(f["text"]) + (" <font size=8 color='#5b6475'>(mehrere möglich)</font>" if f.get("mehrere") else ""), fq)]
        if f["typ"] == "kreuz":
            out.append(Paragraph("&nbsp;&nbsp;&nbsp;".join(f"☐ {E(o)}" for o in f["optionen"]), tx))
        else:
            out.append(Paragraph(f"<font color='#9aa2b1'>{L}</font>", tx))
            if f["typ"] == "satz":
                out.append(Paragraph(f"<font color='#9aa2b1'>{L}</font>", tx))
        out.append(Spacer(1, 1.5*mm))
        return out

    knopf = Table([[Paragraph(f'<a href="{url}" color="white"><b>▶  Video ansehen</b></a>', st("k", f="DVB", fontSize=12, textColor=colors.white, alignment=1))]], colWidths=[60*mm])
    knopf.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), akz), ("ROUNDEDCORNERS", [6]*4), ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5)]))
    kopf = Table([[[Paragraph("MEIN SEH-BEGLEITER · GPG", eb), Paragraph(f"logo! vom {E(datum_lang(s))}", h1),
                    Paragraph("Name: ______________________", tx)], knopf]], colWidths=[112*mm, 62*mm])
    kopf.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("LEFTPADDING", (0,0), (-1,-1), 0)]))
    teile = [kopf, Spacer(1, 3*mm),
             Paragraph("Lies zuerst die Fragen. Dann schau das Video und beantworte sie beim Zuschauen.", kl), Spacer(1, 2*mm)]
    for i, b in enumerate(s["beitraege"], 1):
        pol = " <font size=8 color='#8a4b2a'>[POLITIK]</font>" if b.get("politisch") else ""
        inhalt = [Paragraph(f"<font color='#8a4b2a'>{i}</font>  {E(b['titel'])}{pol}", h2), Spacer(1, 1*mm)]
        for f in fragen_von(b):
            inhalt += frage(f)
        t = Table([[inhalt]], colWidths=[174*mm])
        t.setStyle(TableStyle([("LINEBEFORE", (0,0), (0,-1), 2.5, akz), ("LEFTPADDING", (0,0), (-1,-1), 7), ("TOPPADDING", (0,0), (-1,-1), 2), ("BOTTOMPADDING", (0,0), (-1,-1), 1)]))
        teile += [KeepTogether(t), Spacer(1, 2*mm)]
    nrn = [str(i) for i in range(1, len(s["beitraege"]) + 1)]
    sf = streit_von(s)
    nach = [Paragraph("Nach dem Schauen", st("h2b", f="DVB", fontSize=14, leading=18, textColor=akz)), Spacer(1, 1*mm)]
    for f in [{"typ": "kreuz", "mehrere": True, "text": "Politik-Detektiv: Welche Beiträge haben mit Politik zu tun?", "optionen": nrn},
              {"typ": "wort", "text": "Mein neues Wort heute – und was es bedeutet:"},
              {"typ": "kreuz", "text": sf["text"], "optionen": sf["optionen"]},
              {"typ": "satz", "text": "Ich finde das, weil …"},
              {"typ": "kreuz", "text": "Wie gut hast du die Sendung verstanden?", "optionen": ["sehr gut", "ganz gut", "nur ein bisschen"]}]:
        nach += frage(f)
    teile += [KeepTogether(nach), Spacer(1, 2*mm),
              Paragraph(f'Quelle: ZDF/KiKA, logo.de · <a href="{url}" color="#8a4b2a">{url}</a>', kl)]
    SimpleDocTemplate(ziel, pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=13*mm, bottomMargin=12*mm,
                      title=f"logo! Seh-Begleiter {s['datum']}", author="GPG Mittelschule Mammendorf").build(teile)

def standalone_html(s):
    """Vollständige HTML-Datei (zum Öffnen auf dem Rechner/Smartboard, fürs Archiv)."""
    return ('<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1"></head><body>'
            + artifact_html(s) + '</body></html>')
