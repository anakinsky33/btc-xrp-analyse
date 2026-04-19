#!/usr/bin/env python3
import streamlit as st
import os, json, datetime, urllib.request, time, html as html_lib
import pandas as pd

st.set_page_config(page_title="Aktienmarkt Analyse", page_icon="📈", layout="wide")

def get_secret(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.environ.get(key, "")

# ── Konfiguration ──────────────────────────────────────────────────────────────

ALLE_AKTIEN = [
    {"name": "S&P 500",   "symbol": "^GSPC", "color": "#1a73e8", "einheit": "Punkte"},
    {"name": "NVIDIA",    "symbol": "NVDA",  "color": "#76b900", "einheit": "USD"},
    {"name": "Apple",     "symbol": "AAPL",  "color": "#555555", "einheit": "USD"},
    {"name": "Microsoft", "symbol": "MSFT",  "color": "#00a4ef", "einheit": "USD"},
]

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/124.0.0.0 Safari/537.36"),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8",
    "Referer": "https://finance.yahoo.com/",
}

# ── Sidebar ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("⚙️ Einstellungen")

    api_key = st.text_input(
        "Anthropic API Key",
        value=get_secret("ANTHROPIC_API_KEY"),
        type="password"
    )
    if api_key:
        masked = api_key[:8] + "..." + api_key[-4:]
        st.caption(f"Key: `{masked}` ({len(api_key)} Zeichen)")

    st.divider()
    st.subheader("📧 E-Mail (optional)")
    send_mail = st.toggle("E-Mail senden", value=False)
    if send_mail:
        gmail_absender = st.text_input("Absender (Gmail)", value=get_secret("GMAIL_ABSENDER"))
        gmail_passwort = st.text_input("App-Passwort", value=get_secret("GMAIL_APP_PASSWORT"), type="password")
        empfaenger     = st.text_input("Empfänger",    value=get_secret("EMPFAENGER"))

    st.divider()
    st.subheader("📊 Aktien auswählen")
    ausgewaehlt = []
    for a in ALLE_AKTIEN:
        if st.checkbox(a["name"], value=True):
            ausgewaehlt.append(a)

# ── Datenabruf ─────────────────────────────────────────────────────────────────

def fetch_yahoo(symbol, days=400):
    end   = int(datetime.datetime.utcnow().timestamp())
    start = int((datetime.datetime.utcnow() - datetime.timedelta(days=days)).timestamp())
    url   = (f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
             f"?interval=1d&period1={start}&period2={end}")
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.loads(r.read())
    result = data["chart"]["result"][0]
    return [{"date": datetime.date.fromtimestamp(ts).isoformat(), "close": round(float(c), 4)}
            for ts, c in zip(result["timestamp"], result["indicators"]["quote"][0]["close"])
            if c is not None and c > 0]

def fetch_fundamentals(symbol):
    try:
        url = (f"https://query2.finance.yahoo.com/v11/finance/quoteSummary/{symbol}"
               f"?modules=financialData%2CdefaultKeyStatistics%2CsummaryDetail")
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read())
        res = data["quoteSummary"]["result"][0]
        fd = res.get("financialData", {})
        ks = res.get("defaultKeyStatistics", {})
        sd = res.get("summaryDetail", {})
        def v(d, k):
            x = d.get(k, {})
            return x.get("raw") if isinstance(x, dict) else x
        fund = {
            "marketCap":      v(ks, "marketCap"),
            "trailingPE":     v(sd, "trailingPE"),
            "forwardPE":      v(ks, "forwardPE"),
            "priceToBook":    v(ks, "priceToBook"),
            "trailingEps":    v(ks, "trailingEps"),
            "dividendYield":  v(sd, "dividendYield"),
            "revenueGrowth":  v(fd, "revenueGrowth"),
            "earningsGrowth": v(fd, "earningsGrowth"),
            "profitMargins":  v(fd, "profitMargins"),
            "returnOnEquity": v(fd, "returnOnEquity"),
            "debtToEquity":   v(fd, "debtToEquity"),
            "week52High":     v(sd, "fiftyTwoWeekHigh"),
            "week52Low":      v(sd, "fiftyTwoWeekLow"),
        }
        if any(val is not None for val in fund.values()):
            return fund, None
        return {}, "Alle Werte leer"
    except Exception as e:
        return {}, str(e)

# ── Indikatoren ────────────────────────────────────────────────────────────────

def ema(prices, period):
    k = 2/(period+1); out = []; prev = None
    for i, p in enumerate(prices):
        if i < period-1: out.append(None); continue
        if prev is None: prev = sum(prices[:period])/period
        else: prev = p*k + prev*(1-k)
        out.append(round(prev, 4))
    return out

def rsi(prices, period=14):
    out = [None]*period; ag = al = 0.0
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
    st_ = next(i for i, x in enumerate(ml) if x is not None)
    sr  = ema([x for x in ml if x is not None], 9)
    sig = [None if ml[i] is None else sr[i-st_] for i in range(len(prices))]
    hist= [round(ml[i]-sig[i], 4) if ml[i] is not None and sig[i] is not None else None
           for i in range(len(prices))]
    return ml, sig, hist

def build(raw):
    prices = [r["close"] for r in raw]
    e50, e200 = ema(prices, 50), ema(prices, 200)
    r14 = rsi(prices)
    ml, sig, hist = macd(prices)
    return [{"date": raw[i]["date"], "price": raw[i]["close"],
             "ema50": e50[i], "ema200": e200[i],
             "rsi": r14[i], "macd": ml[i], "signal": sig[i], "hist": hist[i]}
            for i in range(len(raw))]

# ── Claude Analyse ─────────────────────────────────────────────────────────────

def claude_analyse(name, einheit, data, fund, key):
    last = data[-1]
    def px(v): return f"{v:,.2f} {einheit}" if v else "-"
    ctx  = f"Wertpapier: {name} ({einheit}) - Daily - {last['date']}\n\nAKTUELL:\n"
    ctx += f"  Kurs: {px(last['price'])}  EMA50: {px(last['ema50'])}  EMA200: {px(last['ema200'])}\n"
    ctx += f"  RSI: {last['rsi']}  MACD: {last['macd']}  Hist: {last['hist']}\n"
    if fund:
        def fp(v): return f"{v:.2f}" if v is not None else "-"
        def pct(v): return f"{v*100:.1f}%" if v is not None else "-"
        def mc(v): return (f"${v/1e12:.2f}T" if v >= 1e12 else f"${v/1e9:.2f}B") if v else "-"
        ctx += (f"\nFUNDAMENTALDATEN: MarktCap={mc(fund.get('marketCap'))} "
                f"KGV={fp(fund.get('trailingPE'))} KGV-fwd={fp(fund.get('forwardPE'))} "
                f"KBV={fp(fund.get('priceToBook'))} EPS={fp(fund.get('trailingEps'))} "
                f"Div={pct(fund.get('dividendYield'))} UmsWachstum={pct(fund.get('revenueGrowth'))} "
                f"GewWachstum={pct(fund.get('earningsGrowth'))} Marge={pct(fund.get('profitMargins'))} "
                f"ROE={pct(fund.get('returnOnEquity'))} D/E={fp(fund.get('debtToEquity'))}\n")
    ctx += "\nLETZTE 30 TAGE:\n"
    for d in data[-30:]:
        ctx += f"  {d['date']}: {px(d['price'])} RSI:{d['rsi']} MACD:{d['macd']}\n"

    has_fund = bool(fund)
    payload = json.dumps({
        "model": "claude-opus-4-5",
        "max_tokens": 3500,
        "system": (f"Du bist ein erfahrener Aktienmarkt-Analyst. Analysiere {name} "
                   f"praezise auf Deutsch mit konkreten Preisniveaus."),
        "messages": [{"role": "user", "content": (
            f"{ctx}\n\nVollstaendige technische{' und fundamentale' if has_fund else ''} Analyse:\n\n"
            "## 1. Elliott-Wellen-Analyse\n"
            "## 2. EMA-Trendstruktur\n"
            "## 3. RSI-Analyse\n"
            "## 4. MACD-Analyse\n"
            + ("## 5. Fundamentalanalyse\nBewertung, Wachstum, Margen. Fair bewertet?\n" if has_fund else "")
            + "## 6. Gesamtbild & Schluesselniveaus\n"
            "## 7. 2-Tages-Prognose (48h)\n"
            "- HAUPTSZENARIO (XX%): Kursziel + Prozentveraenderung\n"
            "- ALTERNATIVSZENARIO (XX%): Gegenszenario\n"
            "- ENTSCHEIDENDE MARKEN:\n"
            "- INVALIDIERUNGSLEVEL:\n"
            "- HANDLUNGSEMPFEHLUNG:\n"
        )}]
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages", data=payload,
        headers={"Content-Type": "application/json", "x-api-key": key,
                 "anthropic-version": "2023-06-01"}, method="POST")
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read())["content"][0]["text"]

# ── E-Mail HTML ────────────────────────────────────────────────────────────────

def build_email_html(name, einheit, farbe, data, text, fund):
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
            s = line[3:]
            is_p = "2-Tages" in s or "Prognose" in s
            html_text += (f'<h3 style="color:{"#ff6b6b" if is_p else "#2c3e50"};'
                          f'border-bottom:3px solid {"#e74c3c" if is_p else farbe};'
                          f'padding:8px 0 6px 0;margin-top:28px">{s}</h3>')
        elif any(line.startswith(f"- {k}") for k in ["HAUPTSZENARIO", "ALTERNATIVSZENARIO"]):
            html_text += f'<p style="font-weight:bold;color:#e74c3c">{html_lib.escape(line)}</p>'
        elif any(line.startswith(f"- {k}") for k in ["ENTSCHEIDENDE", "INVALIDIERUNG", "HANDLUNG"]):
            html_text += f'<p style="font-weight:bold;color:#f39c12">{html_lib.escape(line)}</p>'
        elif line.strip():
            html_text += f'<p style="margin:4px 0;line-height:1.7">{html_lib.escape(line)}</p>'

    def row(bg, label, value, color, status, sc):
        return (f'<tr style="border-bottom:1px solid #eee;background:{bg}">'
                f'<td style="padding:10px 16px;color:#555;font-size:13px">{label}</td>'
                f'<td style="padding:10px 16px;font-weight:bold;color:{color}">{value}</td>'
                f'<td style="padding:10px 16px;font-size:12px;font-weight:bold;color:{sc}">{status}</td></tr>')

    return f"""
<div style="font-family:Arial,sans-serif;max-width:680px;margin:0 auto 40px auto;background:#f8f9fa;padding:20px;border-radius:8px">
  <div style="background:linear-gradient(135deg,#1a1a2e,#16213e);color:white;padding:20px;border-radius:8px;margin-bottom:20px;border-left:5px solid {farbe}">
    <div style="font-size:11px;letter-spacing:2px;opacity:0.6">AKTIENMARKT ANALYSE - {last['date']}</div>
    <div style="font-size:24px;font-weight:bold;margin-top:4px;color:{farbe}">{name}</div>
  </div>
  <table style="width:100%;border-collapse:collapse;margin-bottom:20px;background:white;border-radius:8px;overflow:hidden">
    <tr style="background:#2c3e50;color:white">
      <td style="padding:10px 16px;font-size:11px;font-weight:bold">INDIKATOR</td>
      <td style="padding:10px 16px;font-size:11px;font-weight:bold">WERT</td>
      <td style="padding:10px 16px;font-size:11px;font-weight:bold">STATUS</td>
    </tr>
    {row("white",   f"Kurs ({einheit})", f'<span style="font-size:17px">{px(last["price"])}</span>', farbe, "", "")}
    {row("#fafafa", "EMA 50",   px(last["ema50"]),  "#2980b9", "UEBER EMA50"  if ema50_ok  else "UNTER EMA50",  "#27ae60" if ema50_ok  else "#e74c3c")}
    {row("white",   "EMA 200",  px(last["ema200"]), "#c0392b", "UEBER EMA200" if ema200_ok else "UNTER EMA200", "#27ae60" if ema200_ok else "#e74c3c")}
    {row("#fafafa", "RSI (14)", str(last["rsi"]),   rc(last["rsi"]),  "Ueberkauft" if (last["rsi"] or 0)>70 else ("Ueberverkauft" if (last["rsi"] or 0)<30 else "Neutral"), rc(last["rsi"]))}
    {row("white",   "MACD",     str(last["macd"]),  tc(last["macd"]), "Bullish" if (last["macd"] or 0)>0 else "Bearish", tc(last["macd"]))}
    {row("#fafafa", "Hist",     str(last["hist"]),  tc(last["hist"]), "Momentum steigt" if (last["hist"] or 0)>0 else "Momentum faellt", tc(last["hist"]))}
  </table>
  <div style="background:white;border-radius:8px;padding:22px">{html_text}</div>
  <div style="text-align:center;margin-top:14px;font-size:11px;color:#aaa">Automatisch generiert · Keine Anlageberatung</div>
</div>"""

def send_email_func(subject, html_body, absender, passwort, empfaenger):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject; msg["From"] = absender; msg["To"] = empfaenger
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(absender, passwort)
        s.sendmail(absender, empfaenger, msg.as_string())

def fmt_fund_df(fund):
    def fp(v): return f"{v:.2f}" if v is not None else "—"
    def pct(v): return f"{v*100:.1f} %" if v is not None else "—"
    def mc(v): return (f"${v/1e12:.2f} T" if v >= 1e12 else f"${v/1e9:.2f} B") if v else "—"
    return pd.DataFrame([
        ("Marktkapitalisierung", mc(fund.get("marketCap"))),
        ("KGV Trailing",         fp(fund.get("trailingPE"))),
        ("KGV Forward",          fp(fund.get("forwardPE"))),
        ("Kurs / Buchwert",      fp(fund.get("priceToBook"))),
        ("EPS (Trailing)",       f"${fp(fund.get('trailingEps'))}"),
        ("Dividendenrendite",    pct(fund.get("dividendYield"))),
        ("Umsatzwachstum (YoY)", pct(fund.get("revenueGrowth"))),
        ("Gewinnwachstum (YoY)", pct(fund.get("earningsGrowth"))),
        ("Gewinnmarge",          pct(fund.get("profitMargins"))),
        ("Eigenkapitalrendite",  pct(fund.get("returnOnEquity"))),
        ("Verschuldungsgrad",    fp(fund.get("debtToEquity"))),
        ("52W-Hoch / Tief",      f"{fp(fund.get('week52High'))} / {fp(fund.get('week52Low'))}"),
    ], columns=["Kennzahl", "Wert"])

# ── Hauptbereich ───────────────────────────────────────────────────────────────

st.title("📈 Aktienmarkt Analyse")
st.caption("Elliott Wave · RSI · MACD · EMA 50/200 · Fundamentaldaten · 48h-Prognose")

if not ausgewaehlt:
    st.warning("Bitte mindestens eine Aktie in der Sidebar auswählen.")
    st.stop()

api_key = api_key.strip()
if not api_key:
    st.warning("Bitte Anthropic API Key in der Sidebar eintragen.")
    st.stop()
if not api_key.startswith("sk-"):
    st.error("API Key ungültig — muss mit 'sk-' beginnen.")
    st.stop()

if st.button("🚀 Analyse starten", type="primary", use_container_width=True):
    heute = datetime.date.today().strftime("%d.%m.%Y")
    gesamt_html = ""
    bar = st.progress(0, text="Starte...")

    for idx, aktie in enumerate(ausgewaehlt):
        name    = aktie["name"]
        symbol  = aktie["symbol"]
        farbe   = aktie["color"]
        einheit = aktie["einheit"]
        n       = len(ausgewaehlt)

        st.subheader(name, divider="gray")
        col1, col2 = st.columns(2)

        bar.progress((idx*3+1)/(n*3), text=f"{name}: Kursdaten...")
        try:
            raw  = fetch_yahoo(symbol)
            data = build(raw)
            last = data[-1]
        except Exception as e:
            st.error(f"Kursdaten-Fehler: {e}"); continue

        with col1:
            ema50_ok  = last["price"] > (last["ema50"]  or 0)
            ema200_ok = last["price"] > (last["ema200"] or 0)
            rsi_val   = last["rsi"] or 0
            st.metric("Kurs", f"{last['price']:,.2f} {einheit}")
            st.dataframe(pd.DataFrame([
                ["EMA 50",     f"{last['ema50']:,.2f}" if last['ema50'] else "—", "🟢 darüber" if ema50_ok  else "🔴 darunter"],
                ["EMA 200",    f"{last['ema200']:,.2f}" if last['ema200'] else "—", "🟢 darüber" if ema200_ok else "🔴 darunter"],
                ["RSI (14)",   str(rsi_val), "🔴 Überkauft" if rsi_val>70 else ("🟢 Überverkauft" if rsi_val<30 else "🟡 Neutral")],
                ["MACD",       str(last["macd"]), "🟢 Bullish" if (last["macd"] or 0)>0 else "🔴 Bearish"],
                ["Histogramm", str(last["hist"]), "🟢 steigt"  if (last["hist"] or 0)>0 else "🔴 fällt"],
            ], columns=["Indikator", "Wert", "Status"]), hide_index=True, use_container_width=True)

        bar.progress((idx*3+2)/(n*3), text=f"{name}: Fundamentaldaten...")
        fund, fund_err = fetch_fundamentals(symbol)
        with col2:
            if fund:
                st.markdown("**Fundamentaldaten**")
                st.dataframe(fmt_fund_df(fund), hide_index=True, use_container_width=True)
            else:
                st.warning(f"Keine Fundamentaldaten: {fund_err}")

        bar.progress((idx*3+3)/(n*3), text=f"{name}: Claude analysiert...")
        try:
            with st.spinner(f"Claude analysiert {name}..."):
                analyse_text = claude_analyse(name, einheit, data, fund, api_key)
        except Exception as e:
            st.error(f"API-Fehler: {e}"); continue

        with st.expander("📋 Vollständige Analyse", expanded=True):
            st.markdown(analyse_text)

        if send_mail:
            gesamt_html += build_email_html(name, einheit, farbe, data, analyse_text, fund)
            gesamt_html += '<hr style="margin:10px 0 30px 0;border:none;border-top:3px solid #eee">'

        if idx < len(ausgewaehlt) - 1:
            time.sleep(1)

    bar.progress(1.0, text="Fertig ✓")

    if send_mail and gesamt_html:
        try:
            send_email_func(f"Aktienmarkt Analyse - {heute}",
                            gesamt_html, gmail_absender, gmail_passwort, empfaenger)
            st.success(f"✅ E-Mail gesendet an {empfaenger}")
        except Exception as e:
            st.error(f"E-Mail-Fehler: {e}")

    st.balloons()
