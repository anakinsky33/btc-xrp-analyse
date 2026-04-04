#!/usr/bin/env python3
"""
BTC & XRP Elliott Wave Analyse – täglich per E-Mail
Datenquelle: CoinGecko (funktioniert auf PythonAnywhere)
"""

import os, json, datetime, urllib.request, urllib.error, smtplib, html, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ══════════════════════════════════════════════════════════════
#  KONFIGURATION
# ══════════════════════════════════════════════════════════════

ANTHROPIC_API_KEY  = os.environ["ANTHROPIC_API_KEY"]
GMAIL_ABSENDER     = os.environ["GMAIL_ABSENDER"]
GMAIL_APP_PASSWORT = os.environ["GMAIL_APP_PASSWORT"]
EMPFAENGER         = os.environ["EMPFAENGER"]

# Kraken-Paare  (nicht ändern)
COINS = [
    {"name": "BTC", "pair": "XBTUSD",  "kraken": "XXBTZUSD"},
    {"name": "XRP", "pair": "XRPUSD",  "kraken": "XXRPZUSD"},
]

# ══════════════════════════════════════════════════════════════
#  DATENABRUF  (Kraken – kein API-Key, kein Geo-Block)
# ══════════════════════════════════════════════════════════════

def fetch_kraken(pair, kraken_key, limit=720):
    # since = Unix-Timestamp vor 'limit' Tagen
    since = int((datetime.datetime.utcnow() -
                 datetime.timedelta(days=limit)).timestamp())
    url = (f"https://api.kraken.com/0/public/OHLC"
           f"?pair={pair}&interval=1440&since={since}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.loads(r.read())
    if data.get("error"):
        raise Exception(f"Kraken-Fehler: {data['error']}")
    candles = data["result"][kraken_key]
    return [
        {"date":  datetime.date.fromtimestamp(int(c[0])).isoformat(),
         "close": float(c[4])}          # index 4 = close
        for c in candles
        if float(c[4]) > 0
    ]

# ══════════════════════════════════════════════════════════════
#  INDIKATOREN
# ══════════════════════════════════════════════════════════════

def ema(prices, period):
    k = 2/(period+1); out=[]; prev=None
    for i,p in enumerate(prices):
        if i < period-1: out.append(None); continue
        if prev is None: prev = sum(prices[:period])/period
        else: prev = p*k + prev*(1-k)
        out.append(round(prev, 6))
    return out

def rsi(prices, period=14):
    out=[None]*period; ag=al=0.0
    for i in range(1, period+1):
        d=prices[i]-prices[i-1]
        if d>0: ag+=d
        else: al-=d
    ag/=period; al/=period
    out.append(round(100 if al==0 else 100-100/(1+ag/al), 2))
    for i in range(period+1, len(prices)):
        d=prices[i]-prices[i-1]
        ag=(ag*(period-1)+max(d,0))/period
        al=(al*(period-1)+max(-d,0))/period
        out.append(round(100 if al==0 else 100-100/(1+ag/al), 2))
    return out

def macd(prices):
    e12=ema(prices,12); e26=ema(prices,26)
    ml=[round(e12[i]-e26[i],6) if e12[i] and e26[i] else None for i in range(len(prices))]
    st=next(i for i,v in enumerate(ml) if v is not None)
    sr=ema([v for v in ml if v is not None],9)
    sig=[None if ml[i] is None else sr[i-st] for i in range(len(prices))]
    hist=[round(ml[i]-sig[i],6) if ml[i] is not None and sig[i] is not None else None
          for i in range(len(prices))]
    return ml, sig, hist

def build(raw):
    prices=[r["close"] for r in raw]
    e50=ema(prices,50); e200=ema(prices,200)
    r14=rsi(prices); ml,sig,hist=macd(prices)
    return [{"date":raw[i]["date"],"price":raw[i]["close"],
             "ema50":e50[i],"ema200":e200[i],
             "rsi":r14[i],"macd":ml[i],"signal":sig[i],"hist":hist[i]}
            for i in range(len(raw))]

# ══════════════════════════════════════════════════════════════
#  CLAUDE-ANALYSE
# ══════════════════════════════════════════════════════════════

def claude_analyse(coin, data):
    last=data[-1]
    def px(v): return f"${v:,.2f}" if v and v>=1 else (f"${v:.5f}" if v else "—")
    ctx  = f"Coin: {coin}/USD · Daily · {last['date']}\n\nAKTUELL:\n"
    ctx += f"  Preis:   {px(last['price'])}\n  EMA 50:  {px(last['ema50'])}\n"
    ctx += f"  EMA 200: {px(last['ema200'])}\n  RSI(14): {last['rsi']}\n"
    ctx += f"  MACD:    {last['macd']}  Signal: {last['signal']}  Hist: {last['hist']}\n\nLETZTE 30 TAGE:\n"
    for d in data[-30:]:
        ctx += f"  {d['date']}: {px(d['price'])} | RSI:{d['rsi']} | MACD:{d['macd']} | Hist:{d['hist']}\n"

    payload = json.dumps({
        "model": "claude-opus-4-5",
        "max_tokens": 1500,
        "system": "Du bist ein professioneller Krypto-Technischer-Analyst mit Expertise in Elliott-Wellen. Analysiere präzise auf Deutsch.",
        "messages": [{"role":"user","content":(
            f"{ctx}\n\nGib eine vollständige technische Analyse:\n"
            "## 1. Elliott-Wellen-Analyse\n## 2. EMA-Trendstruktur\n"
            "## 3. RSI-Analyse\n## 4. MACD-Analyse\n## 5. Gesamtbild & Schlüsselniveaus"
        )}]
    }).encode()

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages", data=payload,
        headers={"Content-Type":"application/json",
                 "x-api-key": ANTHROPIC_API_KEY,
                 "anthropic-version":"2023-06-01"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())["content"][0]["text"]

# ══════════════════════════════════════════════════════════════
#  HTML-EMAIL
# ══════════════════════════════════════════════════════════════

def analyse_to_html(coin, data, text):
    last=data[-1]
    def px(v): return f"${v:,.2f}" if v and v>=1 else (f"${v:.5f}" if v else "—")
    def rsi_color(v):
        if not v: return "#888"
        return "#e74c3c" if v>70 else ("#27ae60" if v<30 else "#f39c12")
    def tc(v): return "#27ae60" if (v or 0)>0 else "#e74c3c"

    coin_color   = "#f7931a" if coin=="BTC" else "#346aa9"
    ema50_ok     = (last["price"] or 0) > (last["ema50"]  or 0)
    ema200_ok    = (last["price"] or 0) > (last["ema200"] or 0)

    html_text = ""
    for line in text.split("\n"):
        if line.startswith("## "):
            html_text += f'<h3 style="color:#2c3e50;border-bottom:2px solid {coin_color};padding-bottom:4px;margin-top:24px">{line[3:]}</h3>'
        elif "**" in line:
            html_text += f'<p style="margin:4px 0;line-height:1.7"><strong>{html.escape(line.replace("**",""))}</strong></p>'
        elif line.strip():
            html_text += f'<p style="margin:4px 0;line-height:1.7">{html.escape(line)}</p>'

    def row(bg, label, value, color, status, status_color):
        return (f'<tr style="border-bottom:1px solid #eee;background:{bg}">'
                f'<td style="padding:11px 16px;color:#555;font-size:13px">{label}</td>'
                f'<td style="padding:11px 16px;font-weight:bold;color:{color}">{value}</td>'
                f'<td style="padding:11px 16px;font-size:12px;font-weight:bold;color:{status_color}">{status}</td></tr>')

    return f"""
<div style="font-family:Arial,sans-serif;max-width:680px;margin:0 auto 40px auto;background:#f8f9fa;padding:20px;border-radius:8px">
  <div style="background:linear-gradient(135deg,#1a1a2e,#16213e);color:white;padding:20px;border-radius:8px;margin-bottom:20px;border-left:5px solid {coin_color}">
    <div style="font-size:11px;letter-spacing:2px;opacity:0.6">TECHNISCHE ANALYSE · DAILY · {last['date']}</div>
    <div style="font-size:24px;font-weight:bold;margin-top:4px;color:{coin_color}">{coin}/USD</div>
    <div style="font-size:13px;opacity:0.7;margin-top:2px">Elliott Wave · RSI · MACD · EMA 50/200</div>
  </div>

  <table style="width:100%;border-collapse:collapse;margin-bottom:20px;background:white;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08)">
    <tr style="background:#2c3e50;color:white">
      <td style="padding:10px 16px;font-size:11px;letter-spacing:1px;font-weight:bold">INDIKATOR</td>
      <td style="padding:10px 16px;font-size:11px;letter-spacing:1px;font-weight:bold">WERT</td>
      <td style="padding:10px 16px;font-size:11px;letter-spacing:1px;font-weight:bold">STATUS</td>
    </tr>
    {row("white",      "Preis",      f'<span style="font-size:17px">{px(last["price"])}</span>', coin_color, "", "")}
    {row("#fafafa",    "EMA 50",     px(last["ema50"]),  "#2980b9", "Preis ÜBER EMA50 ▲" if ema50_ok  else "Preis UNTER EMA50 ▼",  "#27ae60" if ema50_ok  else "#e74c3c")}
    {row("white",      "EMA 200",    px(last["ema200"]), "#c0392b", "Preis ÜBER EMA200 ▲" if ema200_ok else "Preis UNTER EMA200 ▼", "#27ae60" if ema200_ok else "#e74c3c")}
    {row("#fafafa",    "RSI (14)",   str(last["rsi"]),   rsi_color(last["rsi"]), "🔴 Überkauft" if (last["rsi"] or 0)>70 else ("🟢 Überverkauft" if (last["rsi"] or 0)<30 else "🟡 Neutral"), rsi_color(last["rsi"]))}
    {row("white",      "MACD",       str(last["macd"]),  tc(last["macd"]), "🟢 Bullish" if (last["macd"] or 0)>0 else "🔴 Bearish", tc(last["macd"]))}
    {row("#fafafa",    "Histogramm", str(last["hist"]),  tc(last["hist"]), "↑ Momentum steigt" if (last["hist"] or 0)>0 else "↓ Momentum fällt", tc(last["hist"]))}
  </table>

  <div style="background:white;border-radius:8px;padding:22px;box-shadow:0 2px 8px rgba(0,0,0,0.08)">
    <div style="font-size:11px;color:#888;letter-spacing:1px;margin-bottom:14px">⚡ KI ELLIOTT WAVE ANALYSE · CLAUDE AI</div>
    {html_text}
  </div>
  <div style="text-align:center;margin-top:14px;font-size:11px;color:#aaa">
    Automatisch generiert · Nur zu Informationszwecken · Keine Anlageberatung
  </div>
</div>"""

# ══════════════════════════════════════════════════════════════
#  E-MAIL VERSAND
# ══════════════════════════════════════════════════════════════

def send_email(subject, html_body):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = GMAIL_ABSENDER
    msg["To"]      = EMPFAENGER
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(GMAIL_ABSENDER, GMAIL_APP_PASSWORT)
        s.sendmail(GMAIL_ABSENDER, EMPFAENGER, msg.as_string())

# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════

def main():
    heute = datetime.date.today().strftime("%d.%m.%Y")
    print(f"=== BTC & XRP Analyse {heute} ===\n")
    alle_html = ""

    for coin in COINS:
        name = coin["name"]
        print(f"⟳  {name}: Lade Kraken-Daten …")
        try:
            raw  = fetch_kraken(coin["pair"], coin["kraken"])
            data = build(raw)
            print(f"   ✓ {len(data)} Tage geladen, letzter Kurs: ${data[-1]['price']:,.2f}")
        except Exception as e:
            print(f"   ⚠ Datenfehler: {e}"); continue

        print(f"⟳  {name}: Claude analysiert …")
        try:
            text = claude_analyse(name, data)
            print(f"   ✓ Analyse erhalten ({len(text)} Zeichen)")
        except Exception as e:
            print(f"   ⚠ API-Fehler: {e}"); continue

        alle_html += analyse_to_html(name, data, text)
        alle_html += '<hr style="margin:10px 0 30px 0;border:none;border-top:3px solid #eee">'

        # Kurze Pause zwischen den Coins (CoinGecko Rate-Limit)
        time.sleep(2)

    if not alle_html:
        print("⚠ Keine Daten – E-Mail wird nicht gesendet."); return

    print(f"\n⟳  Sende E-Mail an {EMPFAENGER} …")
    try:
        send_email(f"📊 BTC & XRP Elliott-Wave-Analyse · {heute}", alle_html)
        print(f"✅ E-Mail erfolgreich gesendet!")
    except Exception as e:
        print(f"⚠ E-Mail-Fehler: {e}")
        print("\n→ Gmail App-Passwort prüfen:")
        print("  1. myaccount.google.com → Sicherheit")
        print("  2. '2-Schritt-Verifizierung' muss AN sein")
        print("  3. Suche nach 'App-Passwörter'")
        print("  4. Neues App-Passwort erstellen → in Zeile 19 eintragen")

if __name__ == "__main__":
    main()
