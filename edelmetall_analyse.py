#!/usr/bin/env python3
"""
Gold & Silber Elliott Wave Analyse - taeglich per E-Mail
Datenquelle: Yahoo Finance (kein API-Key noetig)
"""

import os, json, datetime, urllib.request, smtplib, html, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# =====================================================
#  KONFIGURATION
# =====================================================

ANTHROPIC_API_KEY  = os.environ["ANTHROPIC_API_KEY"]
GMAIL_ABSENDER     = os.environ["GMAIL_ABSENDER"]
GMAIL_APP_PASSWORT = os.environ["GMAIL_APP_PASSWORT"]
EMPFAENGER         = os.environ["EMPFAENGER"]

METALS = [
    {"name": "Gold",   "symbol": "GC=F",  "color": "#FFD700", "unit": "USD/oz"},
    {"name": "Silber", "symbol": "SI=F",  "color": "#C0C0C0", "unit": "USD/oz"},
]

# =====================================================

def fetch_yahoo(symbol, days=400):
    end   = int(datetime.datetime.utcnow().timestamp())
    start = int((datetime.datetime.utcnow() - datetime.timedelta(days=days)).timestamp())
    url   = (f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
             f"?interval=1d&period1={start}&period2={end}")
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.loads(r.read())

    result    = data["chart"]["result"][0]
    timestamps = result["timestamp"]
    closes    = result["indicators"]["quote"][0]["close"]

    rows = []
    for ts, close in zip(timestamps, closes):
        if close is not None and close > 0:
            rows.append({
                "date":  datetime.date.fromtimestamp(ts).isoformat(),
                "close": round(float(close), 4)
            })
    return rows

def ema(prices, period):
    k = 2/(period+1); out=[]; prev=None
    for i, p in enumerate(prices):
        if i < period-1: out.append(None); continue
        if prev is None: prev = sum(prices[:period])/period
        else: prev = p*k + prev*(1-k)
        out.append(round(prev, 4))
    return out

def rsi(prices, period=14):
    out=[None]*period; ag=al=0.0
    for i in range(1, period+1):
        d = prices[i]-prices[i-1]
        if d > 0: ag += d
        else: al -= d
    ag /= period; al /= period
    out.append(round(100 if al==0 else 100-100/(1+ag/al), 2))
    for i in range(period+1, len(prices)):
        d = prices[i]-prices[i-1]
        ag = (ag*(period-1)+max(d,0))/period
        al = (al*(period-1)+max(-d,0))/period
        out.append(round(100 if al==0 else 100-100/(1+ag/al), 2))
    return out

def macd(prices):
    e12 = ema(prices, 12); e26 = ema(prices, 26)
    ml  = [round(e12[i]-e26[i], 4) if e12[i] and e26[i] else None for i in range(len(prices))]
    st  = next(i for i,v in enumerate(ml) if v is not None)
    sr  = ema([v for v in ml if v is not None], 9)
    sig = [None if ml[i] is None else sr[i-st] for i in range(len(prices))]
    hist= [round(ml[i]-sig[i], 4) if ml[i] is not None and sig[i] is not None else None
           for i in range(len(prices))]
    return ml, sig, hist

def build(raw):
    prices = [r["close"] for r in raw]
    e50    = ema(prices, 50)
    e200   = ema(prices, 200)
    r14    = rsi(prices)
    ml, sig, hist = macd(prices)
    return [{"date": raw[i]["date"], "price": raw[i]["close"],
             "ema50": e50[i], "ema200": e200[i],
             "rsi": r14[i], "macd": ml[i], "signal": sig[i], "hist": hist[i]}
            for i in range(len(raw))]

def claude_analyse(metal, unit, data):
    last = data[-1]
    def px(v): return f"${v:,.2f}" if v else "-"
    ctx  = f"Metall: {metal}/USD ({unit}) - Daily - {last['date']}\n\nAKTUELL:\n"
    ctx += f"  Preis:   {px(last['price'])}\n  EMA 50:  {px(last['ema50'])}\n"
    ctx += f"  EMA 200: {px(last['ema200'])}\n  RSI(14): {last['rsi']}\n"
    ctx += f"  MACD:    {last['macd']}  Signal: {last['signal']}  Hist: {last['hist']}\n\nLETZTE 30 TAGE:\n"
    for d in data[-30:]:
        ctx += f"  {d['date']}: {px(d['price'])} | RSI:{d['rsi']} | MACD:{d['macd']} | Hist:{d['hist']}\n"

    payload = json.dumps({
        "model": "claude-opus-4-5",
        "max_tokens": 3000,
        "system": (
            f"Du bist ein erfahrener Edelmetall-Analyst mit Expertise in Elliott-Wellen, "
            f"RSI, MACD und EMAs. Analysiere {metal} praezise und meinungsstark auf Deutsch. "
            f"Nenne immer konkrete Preisniveaus in USD pro Unze."
        ),
        "messages": [{"role": "user", "content": (
            f"{ctx}\n\nGib eine vollstaendige technische Analyse:\n\n"
            "## 1. Elliott-Wellen-Analyse\n"
            "Aktive Welle? Impuls oder Korrektur? Position im Zyklus?\n\n"
            "## 2. EMA-Trendstruktur\n"
            "Preis vs. EMA50 vs. EMA200. Golden Cross / Death Cross?\n\n"
            "## 3. RSI-Analyse\n"
            "Momentum, Zonen, Divergenzen?\n\n"
            "## 4. MACD-Analyse\n"
            "Crossover, Histogramm-Richtung, Momentum?\n\n"
            "## 5. Gesamtbild & Schluesselniveaus\n"
            "Bias + konkrete Support/Resistance-Preiszonen in USD/oz.\n\n"
            "## 6. 2-Tages-Prognose (48h)\n"
            "Was wird in den naechsten 48 Stunden WAHRSCHEINLICH passieren?\n"
            "- HAUPTSZENARIO (XX% Wahrscheinlichkeit): Beschreibe den wahrscheinlichsten "
            "Kursverlauf mit konkretem Kursziel und Prozentveraenderung.\n"
            "- ALTERNATIVSZENARIO (XX% Wahrscheinlichkeit): Gegenszenario mit Kursziel.\n"
            "- ENTSCHEIDENDE MARKEN: Welche Preislevels bestimmen das Szenario?\n"
            "- INVALIDIERUNGSLEVEL: Ab welchem Kurs wird das Hauptszenario ungueltig?\n"
            "- HANDLUNGSEMPFEHLUNG: Klar und direkt.\n"
        )}]
    }).encode()

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages", data=payload,
        headers={"Content-Type": "application/json",
                 "x-api-key": ANTHROPIC_API_KEY,
                 "anthropic-version": "2023-06-01"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())["content"][0]["text"]

def to_html(metal, unit, coin_color, data, text):
    last      = data[-1]
    def px(v): return f"${v:,.2f}" if v else "-"
    def rc(v):
        if not v: return "#888"
        return "#e74c3c" if v > 70 else ("#27ae60" if v < 30 else "#f39c12")
    def tc(v): return "#27ae60" if (v or 0) > 0 else "#e74c3c"

    ema50_ok  = (last["price"] or 0) > (last["ema50"]  or 0)
    ema200_ok = (last["price"] or 0) > (last["ema200"] or 0)

    html_text = ""
    for line in text.split("\n"):
        if line.startswith("## "):
            section = line[3:]
            is_prog = "2-Tages" in section or "Prognose" in section
            bc      = "#e74c3c" if is_prog else coin_color
            col     = "#ff6b6b" if is_prog else "#2c3e50"
            html_text += (f'<h3 style="color:{col};border-bottom:3px solid {bc};'
                          f'padding:8px 0 6px 0;margin-top:28px">{section}</h3>')
        elif any(line.startswith(f"- {k}") for k in ["HAUPTSZENARIO","ALTERNATIVSZENARIO"]):
            html_text += f'<p style="margin:8px 0;line-height:1.8;font-weight:bold;color:#e74c3c">{html.escape(line)}</p>'
        elif any(line.startswith(f"- {k}") for k in ["ENTSCHEIDENDE","INVALIDIERUNG","HANDLUNG"]):
            html_text += f'<p style="margin:8px 0;line-height:1.8;font-weight:bold;color:#f39c12">{html.escape(line)}</p>'
        elif "**" in line:
            html_text += f'<p style="margin:4px 0;line-height:1.7"><strong>{html.escape(line.replace("**",""))}</strong></p>'
        elif line.strip():
            html_text += f'<p style="margin:4px 0;line-height:1.7">{html.escape(line)}</p>'

    def row(bg, label, value, color, status, sc):
        return (f'<tr style="border-bottom:1px solid #eee;background:{bg}">'
                f'<td style="padding:11px 16px;color:#555;font-size:13px">{label}</td>'
                f'<td style="padding:11px 16px;font-weight:bold;color:{color}">{value}</td>'
                f'<td style="padding:11px 16px;font-size:12px;font-weight:bold;color:{sc}">{status}</td></tr>')

    return f"""
<div style="font-family:Arial,sans-serif;max-width:680px;margin:0 auto 40px auto;background:#f8f9fa;padding:20px;border-radius:8px">
  <div style="background:linear-gradient(135deg,#1a1a2e,#16213e);color:white;padding:20px;border-radius:8px;margin-bottom:20px;border-left:5px solid {coin_color}">
    <div style="font-size:11px;letter-spacing:2px;opacity:0.6">EDELMETALL ANALYSE - DAILY - {last['date']}</div>
    <div style="font-size:24px;font-weight:bold;margin-top:4px;color:{coin_color}">{metal} / USD</div>
    <div style="font-size:13px;opacity:0.7;margin-top:2px">{unit} · Elliott Wave · RSI · MACD · EMA 50/200 · 48h-Prognose</div>
  </div>

  <table style="width:100%;border-collapse:collapse;margin-bottom:20px;background:white;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08)">
    <tr style="background:#2c3e50;color:white">
      <td style="padding:10px 16px;font-size:11px;font-weight:bold">INDIKATOR</td>
      <td style="padding:10px 16px;font-size:11px;font-weight:bold">WERT</td>
      <td style="padding:10px 16px;font-size:11px;font-weight:bold">STATUS</td>
    </tr>
    {row("white",   "Preis (USD/oz)", f'<span style="font-size:17px">{px(last["price"])}</span>', coin_color, "", "")}
    {row("#fafafa", "EMA 50",   px(last["ema50"]),  "#2980b9", "Preis UEBER EMA50"  if ema50_ok  else "Preis UNTER EMA50",  "#27ae60" if ema50_ok  else "#e74c3c")}
    {row("white",   "EMA 200",  px(last["ema200"]), "#c0392b", "Preis UEBER EMA200" if ema200_ok else "Preis UNTER EMA200", "#27ae60" if ema200_ok else "#e74c3c")}
    {row("#fafafa", "RSI (14)", str(last["rsi"]),   rc(last["rsi"]),  "Ueberkauft" if (last["rsi"] or 0)>70 else ("Ueberverkauft" if (last["rsi"] or 0)<30 else "Neutral"), rc(last["rsi"]))}
    {row("white",   "MACD",     str(last["macd"]),  tc(last["macd"]), "Bullish" if (last["macd"] or 0)>0 else "Bearish", tc(last["macd"]))}
    {row("#fafafa", "Histogramm", str(last["hist"]), tc(last["hist"]), "Momentum steigt" if (last["hist"] or 0)>0 else "Momentum faellt", tc(last["hist"]))}
  </table>

  <div style="background:white;border-radius:8px;padding:22px;box-shadow:0 2px 8px rgba(0,0,0,0.08)">
    <div style="font-size:11px;color:#888;letter-spacing:1px;margin-bottom:14px">ANALYSE · CLAUDE AI</div>
    {html_text}
  </div>
  <div style="text-align:center;margin-top:14px;font-size:11px;color:#aaa">
    Automatisch generiert · Keine Anlageberatung · Daten: Yahoo Finance
  </div>
</div>"""

def send_email(subject, html_body):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = GMAIL_ABSENDER
    msg["To"]      = EMPFAENGER
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(GMAIL_ABSENDER, GMAIL_APP_PASSWORT)
        s.sendmail(GMAIL_ABSENDER, EMPFAENGER, msg.as_string())

def main():
    heute = datetime.date.today().strftime("%d.%m.%Y")
    print(f"=== Gold & Silber Analyse {heute} ===\n")
    alle_html = ""

    for metal in METALS:
        name  = metal["name"]
        sym   = metal["symbol"]
        color = metal["color"]
        unit  = metal["unit"]

        print(f"  {name}: Lade Yahoo Finance Daten ({sym}) ...")
        try:
            raw  = fetch_yahoo(sym)
            data = build(raw)
            print(f"   {len(data)} Tage, letzter Kurs: ${data[-1]['price']:,.2f}")
        except Exception as e:
            print(f"   Datenfehler: {e}"); continue

        print(f"  {name}: Claude analysiert ...")
        try:
            text = claude_analyse(name, unit, data)
            print(f"   Analyse erhalten ({len(text)} Zeichen)")
        except Exception as e:
            print(f"   API-Fehler: {e}"); continue

        alle_html += to_html(name, unit, color, data, text)
        alle_html += '<hr style="margin:10px 0 30px 0;border:none;border-top:3px solid #eee">'
        time.sleep(2)

    if not alle_html:
        print("Keine Daten - E-Mail wird nicht gesendet."); return

    print(f"\n  Sende E-Mail an {EMPFAENGER} ...")
    try:
        send_email(f"Gold & Silber Elliott-Wave + 48h-Prognose - {heute}", alle_html)
        print("  E-Mail erfolgreich gesendet!")
    except Exception as e:
        print(f"  E-Mail-Fehler: {e}")

if __name__ == "__main__":
    main()
