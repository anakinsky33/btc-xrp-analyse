#!/usr/bin/env python3
"""
Aktienmarkt Elliott Wave Analyse - taeglich per E-Mail
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

AKTIEN = [
    {"name": "S&P 500",   "symbol": "^GSPC",  "color": "#1a73e8", "einheit": "Punkte"},
    {"name": "NVIDIA",    "symbol": "NVDA",   "color": "#76b900", "einheit": "USD"},
    {"name": "Apple",     "symbol": "AAPL",   "color": "#555555", "einheit": "USD"},
    {"name": "Microsoft", "symbol": "MSFT",   "color": "#00a4ef", "einheit": "USD"},
]

# =====================================================

def fetch_fundamentals(symbol):
    url = (f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{symbol}"
           f"?modules=financialData,defaultKeyStatistics,summaryDetail")
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read())
        result = data["quoteSummary"]["result"][0]
        fd = result.get("financialData", {})
        ks = result.get("defaultKeyStatistics", {})
        sd = result.get("summaryDetail", {})

        def val(d, key):
            v = d.get(key, {})
            return v.get("raw") if isinstance(v, dict) else v

        return {
            "marketCap":       val(ks, "marketCap"),
            "trailingPE":      val(sd, "trailingPE"),
            "forwardPE":       val(ks, "forwardPE"),
            "priceToBook":     val(ks, "priceToBook"),
            "trailingEps":     val(ks, "trailingEps"),
            "dividendYield":   val(sd, "dividendYield"),
            "revenueGrowth":   val(fd, "revenueGrowth"),
            "earningsGrowth":  val(fd, "earningsGrowth"),
            "profitMargins":   val(fd, "profitMargins"),
            "returnOnEquity":  val(fd, "returnOnEquity"),
            "debtToEquity":    val(fd, "debtToEquity"),
            "week52High":      val(sd, "fiftyTwoWeekHigh"),
            "week52Low":       val(sd, "fiftyTwoWeekLow"),
            "currentRatio":    val(fd, "currentRatio"),
        }
    except Exception:
        return {}

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

    result     = data["chart"]["result"][0]
    timestamps = result["timestamp"]
    closes     = result["indicators"]["quote"][0]["close"]

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

def claude_analyse(name, einheit, data, fund):
    last = data[-1]
    def px(v): return f"{v:,.2f} {einheit}" if v else "-"
    ctx  = f"Wertpapier: {name} ({einheit}) - Daily - {last['date']}\n\nAKTUELL:\n"
    ctx += f"  Kurs:    {px(last['price'])}\n  EMA 50:  {px(last['ema50'])}\n"
    ctx += f"  EMA 200: {px(last['ema200'])}\n  RSI(14): {last['rsi']}\n"
    ctx += f"  MACD:    {last['macd']}  Signal: {last['signal']}  Hist: {last['hist']}\n"

    if fund:
        def fp(v, fmt=".2f", suffix=""): return f"{v:{fmt}}{suffix}" if v is not None else "-"
        def pct(v): return f"{v*100:.1f}%" if v is not None else "-"
        def mcap(v):
            if v is None: return "-"
            if v >= 1e12: return f"${v/1e12:.2f}T"
            if v >= 1e9:  return f"${v/1e9:.2f}B"
            return f"${v/1e6:.2f}M"
        ctx += "\nFUNDAMENTALDATEN:\n"
        ctx += f"  Marktkapitalisierung: {mcap(fund.get('marketCap'))}\n"
        ctx += f"  KGV (Trailing):       {fp(fund.get('trailingPE'))}\n"
        ctx += f"  KGV (Forward):        {fp(fund.get('forwardPE'))}\n"
        ctx += f"  Kurs/Buchwert:        {fp(fund.get('priceToBook'))}\n"
        ctx += f"  EPS (Trailing):       {fp(fund.get('trailingEps'))}\n"
        ctx += f"  Dividendenrendite:    {pct(fund.get('dividendYield'))}\n"
        ctx += f"  Umsatzwachstum (YoY): {pct(fund.get('revenueGrowth'))}\n"
        ctx += f"  Gewinnwachstum (YoY): {pct(fund.get('earningsGrowth'))}\n"
        ctx += f"  Gewinnmarge:          {pct(fund.get('profitMargins'))}\n"
        ctx += f"  Eigenkapitalrendite:  {pct(fund.get('returnOnEquity'))}\n"
        ctx += f"  Verschuldungsgrad:    {fp(fund.get('debtToEquity'))}\n"
        ctx += f"  52W-Hoch:             {fp(fund.get('week52High'))}\n"
        ctx += f"  52W-Tief:             {fp(fund.get('week52Low'))}\n"

    ctx += "\nLETZTE 30 TAGE:\n"
    for d in data[-30:]:
        ctx += f"  {d['date']}: {px(d['price'])} | RSI:{d['rsi']} | MACD:{d['macd']} | Hist:{d['hist']}\n"

    has_fund = bool(fund)
    payload = json.dumps({
        "model": "claude-opus-4-5",
        "max_tokens": 3500,
        "system": (
            f"Du bist ein erfahrener Aktienmarkt-Analyst mit Expertise in Elliott-Wellen, "
            f"RSI, MACD, EMAs und Fundamentalanalyse. Analysiere {name} praezise und "
            f"meinungsstark auf Deutsch. Nenne immer konkrete Preisniveaus."
        ),
        "messages": [{"role": "user", "content": (
            f"{ctx}\n\nGib eine vollstaendige technische"
            f"{' und fundamentale' if has_fund else ''} Analyse:\n\n"
            "## 1. Elliott-Wellen-Analyse\n"
            "Aktive Welle? Impuls oder Korrektur? Position im Zyklus?\n\n"
            "## 2. EMA-Trendstruktur\n"
            "Kurs vs. EMA50 vs. EMA200. Golden Cross / Death Cross?\n\n"
            "## 3. RSI-Analyse\n"
            "Momentum, Zonen, Divergenzen?\n\n"
            "## 4. MACD-Analyse\n"
            "Crossover, Histogramm-Richtung, Momentum?\n\n"
            + (
            "## 5. Fundamentalanalyse\n"
            "Bewertung (KGV, KBV), Wachstum, Margen, Verschuldung. "
            "Ist die Aktie fair bewertet, unter- oder ueberbewertet? "
            "Wie unterstuetzen/widersprechen die Fundamentaldaten dem technischen Bild?\n\n"
            if has_fund else ""
            ) +
            "## 6. Gesamtbild & Schluesselniveaus\n"
            "Bias + konkrete Support/Resistance-Preiszonen.\n\n"
            "## 7. 2-Tages-Prognose (48h)\n"
            "Was wird in den naechsten 48 Stunden WAHRSCHEINLICH passieren?\n"
            "- HAUPTSZENARIO (XX% Wahrscheinlichkeit): Beschreibe den wahrscheinlichsten "
            "Kursverlauf mit konkretem Kursziel und Prozentveraenderung.\n"
            "- ALTERNATIVSZENARIO (XX% Wahrscheinlichkeit): Gegenszenario mit Kursziel.\n"
            "- ENTSCHEIDENDE MARKEN: Welche Kurslevels bestimmen das Szenario?\n"
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

def fund_table_html(fund):
    if not fund:
        return ""

    def fp(v, fmt=".2f", suffix=""): return f"{v:{fmt}}{suffix}" if v is not None else "-"
    def pct(v): return f"{v*100:.1f}%" if v is not None else "-"
    def mcap(v):
        if v is None: return "-"
        if v >= 1e12: return f"${v/1e12:.2f}T"
        if v >= 1e9:  return f"${v/1e9:.2f}B"
        return f"${v/1e6:.2f}M"

    def frow(bg, label, value, hint="", hint_color="#555"):
        return (f'<tr style="border-bottom:1px solid #eee;background:{bg}">'
                f'<td style="padding:9px 16px;color:#555;font-size:13px">{label}</td>'
                f'<td style="padding:9px 16px;font-weight:bold;color:#2c3e50">{value}</td>'
                f'<td style="padding:9px 16px;font-size:12px;color:{hint_color}">{hint}</td></tr>')

    kgv = fund.get("trailingPE")
    kgv_hint = ""
    kgv_color = "#555"
    if kgv:
        if kgv < 15:   kgv_hint, kgv_color = "guenstig", "#27ae60"
        elif kgv < 25: kgv_hint, kgv_color = "moderat", "#f39c12"
        else:          kgv_hint, kgv_color = "teuer", "#e74c3c"

    roe = fund.get("returnOnEquity")
    roe_hint = ""
    roe_color = "#555"
    if roe:
        if roe > 0.20:  roe_hint, roe_color = "stark", "#27ae60"
        elif roe > 0.10: roe_hint, roe_color = "solide", "#f39c12"
        else:            roe_hint, roe_color = "schwach", "#e74c3c"

    rows = [
        frow("white",   "Marktkapitalisierung", mcap(fund.get("marketCap"))),
        frow("#fafafa", "KGV Trailing",          fp(kgv),                    kgv_hint, kgv_color),
        frow("white",   "KGV Forward",           fp(fund.get("forwardPE"))),
        frow("#fafafa", "Kurs / Buchwert",        fp(fund.get("priceToBook"))),
        frow("white",   "EPS (Trailing)",         f"${fp(fund.get('trailingEps'))}"),
        frow("#fafafa", "Dividendenrendite",      pct(fund.get("dividendYield"))),
        frow("white",   "Umsatzwachstum (YoY)",  pct(fund.get("revenueGrowth"))),
        frow("#fafafa", "Gewinnwachstum (YoY)",   pct(fund.get("earningsGrowth"))),
        frow("white",   "Gewinnmarge",            pct(fund.get("profitMargins"))),
        frow("#fafafa", "Eigenkapitalrendite",    pct(roe), roe_hint, roe_color),
        frow("white",   "Verschuldungsgrad",      fp(fund.get("debtToEquity"))),
        frow("#fafafa", "52W-Hoch / Tief",
             f"{fp(fund.get('week52High'))} / {fp(fund.get('week52Low'))}"),
    ]
    return f"""
  <h3 style="color:#2c3e50;border-bottom:3px solid #8e44ad;padding:8px 0 6px 0;margin-top:28px">Fundamentaldaten</h3>
  <table style="width:100%;border-collapse:collapse;margin-bottom:16px;background:white;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.06)">
    <tr style="background:#8e44ad;color:white">
      <td style="padding:9px 16px;font-size:11px;font-weight:bold">KENNZAHL</td>
      <td style="padding:9px 16px;font-size:11px;font-weight:bold">WERT</td>
      <td style="padding:9px 16px;font-size:11px;font-weight:bold">EINSCHAETZUNG</td>
    </tr>
    {"".join(rows)}
  </table>"""

def to_html(name, einheit, farbe, data, text, fund=None):
    last = data[-1]
    def px(v): return f"{v:,.2f}" if v else "-"
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
            bc      = "#e74c3c" if is_prog else farbe
            col     = "#ff6b6b" if is_prog else "#2c3e50"
            html_text += (f'<h3 style="color:{col};border-bottom:3px solid {bc};'
                          f'padding:8px 0 6px 0;margin-top:28px">{section}</h3>')
        elif any(line.startswith(f"- {k}") for k in ["HAUPTSZENARIO", "ALTERNATIVSZENARIO"]):
            html_text += f'<p style="margin:8px 0;line-height:1.8;font-weight:bold;color:#e74c3c">{html.escape(line)}</p>'
        elif any(line.startswith(f"- {k}") for k in ["ENTSCHEIDENDE", "INVALIDIERUNG", "HANDLUNG"]):
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
  <div style="background:linear-gradient(135deg,#1a1a2e,#16213e);color:white;padding:20px;border-radius:8px;margin-bottom:20px;border-left:5px solid {farbe}">
    <div style="font-size:11px;letter-spacing:2px;opacity:0.6">AKTIENMARKT ANALYSE - DAILY - {last['date']}</div>
    <div style="font-size:24px;font-weight:bold;margin-top:4px;color:{farbe}">{name}</div>
    <div style="font-size:13px;opacity:0.7;margin-top:2px">{einheit} · Elliott Wave · RSI · MACD · EMA 50/200 · 48h-Prognose</div>
  </div>

  <table style="width:100%;border-collapse:collapse;margin-bottom:20px;background:white;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08)">
    <tr style="background:#2c3e50;color:white">
      <td style="padding:10px 16px;font-size:11px;font-weight:bold">INDIKATOR</td>
      <td style="padding:10px 16px;font-size:11px;font-weight:bold">WERT</td>
      <td style="padding:10px 16px;font-size:11px;font-weight:bold">STATUS</td>
    </tr>
    {row("white",   f"Kurs ({einheit})", f'<span style="font-size:17px">{px(last["price"])}</span>', farbe, "", "")}
    {row("#fafafa", "EMA 50",     px(last["ema50"]),  "#2980b9", "Kurs UEBER EMA50"  if ema50_ok  else "Kurs UNTER EMA50",  "#27ae60" if ema50_ok  else "#e74c3c")}
    {row("white",   "EMA 200",    px(last["ema200"]), "#c0392b", "Kurs UEBER EMA200" if ema200_ok else "Kurs UNTER EMA200", "#27ae60" if ema200_ok else "#e74c3c")}
    {row("#fafafa", "RSI (14)",   str(last["rsi"]),   rc(last["rsi"]),  "Ueberkauft" if (last["rsi"] or 0)>70 else ("Ueberverkauft" if (last["rsi"] or 0)<30 else "Neutral"), rc(last["rsi"]))}
    {row("white",   "MACD",       str(last["macd"]),  tc(last["macd"]), "Bullish" if (last["macd"] or 0)>0 else "Bearish", tc(last["macd"]))}
    {row("#fafafa", "Histogramm", str(last["hist"]),  tc(last["hist"]), "Momentum steigt" if (last["hist"] or 0)>0 else "Momentum faellt", tc(last["hist"]))}
  </table>

  <div style="background:white;border-radius:8px;padding:22px;box-shadow:0 2px 8px rgba(0,0,0,0.08)">
    <div style="font-size:11px;color:#888;letter-spacing:1px;margin-bottom:14px">ANALYSE · CLAUDE AI</div>
    {fund_table_html(fund)}
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
    print(f"=== Aktienmarkt Analyse {heute} ===\n")
    alle_html = ""

    for aktie in AKTIEN:
        name    = aktie["name"]
        symbol  = aktie["symbol"]
        farbe   = aktie["color"]
        einheit = aktie["einheit"]

        print(f"  {name}: Lade Yahoo Finance Daten ({symbol}) ...")
        try:
            raw  = fetch_yahoo(symbol)
            data = build(raw)
            print(f"   {len(data)} Tage, letzter Kurs: {data[-1]['price']:,.2f} {einheit}")
        except Exception as e:
            print(f"   Datenfehler: {e}"); continue

        print(f"  {name}: Lade Fundamentaldaten ...")
        fund = fetch_fundamentals(symbol)
        if fund:
            print(f"   KGV:{fund.get('trailingPE')} | Marktcap:{fund.get('marketCap')}")
        else:
            print(f"   Keine Fundamentaldaten verfuegbar")

        print(f"  {name}: Claude analysiert ...")
        try:
            text = claude_analyse(name, einheit, data, fund)
            print(f"   Analyse erhalten ({len(text)} Zeichen)")
        except Exception as e:
            print(f"   API-Fehler: {e}"); continue

        alle_html += to_html(name, einheit, farbe, data, text, fund)
        alle_html += '<hr style="margin:10px 0 30px 0;border:none;border-top:3px solid #eee">'
        time.sleep(2)

    if not alle_html:
        print("Keine Daten - E-Mail wird nicht gesendet."); return

    print(f"\n  Sende E-Mail an {EMPFAENGER} ...")
    try:
        send_email(f"Aktienmarkt Elliott-Wave + 48h-Prognose - {heute}", alle_html)
        print("  E-Mail erfolgreich gesendet!")
    except Exception as e:
        print(f"  E-Mail-Fehler: {e}")

if __name__ == "__main__":
    main()
