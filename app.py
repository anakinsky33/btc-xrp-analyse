#!/usr/bin/env python3
import streamlit as st
import os, json, datetime, urllib.request, time
import pandas as pd
import yfinance as yf

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
        st.caption(f"Key erkannt: `{masked}` ({len(api_key)} Zeichen)")

    st.divider()
    st.subheader("📧 E-Mail (optional)")
    send_mail = st.toggle("E-Mail senden", value=False)
    if send_mail:
        gmail_absender = st.text_input("Absender (Gmail)", value=get_secret("GMAIL_ABSENDER"))
        gmail_passwort = st.text_input("App-Passwort",     value=get_secret("GMAIL_APP_PASSWORT"), type="password")
        empfaenger     = st.text_input("Empfänger",        value=get_secret("EMPFAENGER"))

    st.divider()
    st.subheader("📊 Aktien auswählen")
    ausgewaehlt = []
    for a in ALLE_AKTIEN:
        if st.checkbox(a["name"], value=True):
            ausgewaehlt.append(a)

# ── Hilfsfunktionen ────────────────────────────────────────────────────────────

def fetch_yahoo(symbol, days=400):
    end   = int(datetime.datetime.utcnow().timestamp())
    start = int((datetime.datetime.utcnow() - datetime.timedelta(days=days)).timestamp())
    url   = (f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
             f"?interval=1d&period1={start}&period2={end}")
    req = urllib.request.Request(url, headers=YAHOO_HEADERS)
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.loads(r.read())
    result     = data["chart"]["result"][0]
    timestamps = result["timestamp"]
    closes     = result["indicators"]["quote"][0]["close"]
    return [{"date": datetime.date.fromtimestamp(ts).isoformat(), "close": round(float(c), 4)}
            for ts, c in zip(timestamps, closes) if c is not None and c > 0]

YAHOO_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/124.0.0.0 Safari/537.36"),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8",
    "Referer": "https://finance.yahoo.com/",
    "Origin": "https://finance.yahoo.com",
}

def fetch_fundamentals(symbol):
    try:
        info = yf.Ticker(symbol).info
        def g(k): return info.get(k)
        return {
            "marketCap":      g("marketCap"),
            "trailingPE":     g("trailingPE"),
            "forwardPE":      g("forwardPE"),
            "priceToBook":    g("priceToBook"),
            "trailingEps":    g("trailingEps"),
            "dividendYield":  g("dividendYield"),
            "revenueGrowth":  g("revenueGrowth"),
            "earningsGrowth": g("earningsGrowth"),
            "profitMargins":  g("profitMargins"),
            "returnOnEquity": g("returnOnEquity"),
            "debtToEquity":   g("debtToEquity"),
            "week52High":     g("fiftyTwoWeekHigh"),
            "week52Low":      g("fiftyTwoWeekLow"),
        }
    except Exception:
        return {}

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
    e12 = ema(prices,12); e26 = ema(prices,26)
    ml  = [round(e12[i]-e26[i],4) if e12[i] and e26[i] else None for i in range(len(prices))]
    st_ = next(i for i,x in enumerate(ml) if x is not None)
    sr  = ema([x for x in ml if x is not None], 9)
    sig = [None if ml[i] is None else sr[i-st_] for i in range(len(prices))]
    hist= [round(ml[i]-sig[i],4) if ml[i] is not None and sig[i] is not None else None
           for i in range(len(prices))]
    return ml, sig, hist

def build(raw):
    prices = [r["close"] for r in raw]
    e50, e200 = ema(prices,50), ema(prices,200)
    r14 = rsi(prices)
    ml, sig, hist = macd(prices)
    return [{"date": raw[i]["date"], "price": raw[i]["close"],
             "ema50": e50[i], "ema200": e200[i],
             "rsi": r14[i], "macd": ml[i], "signal": sig[i], "hist": hist[i]}
            for i in range(len(raw))]

def claude_analyse(name, einheit, data, fund, key):
    last = data[-1]
    def px(v): return f"{v:,.2f} {einheit}" if v else "-"
    ctx  = f"Wertpapier: {name} ({einheit}) - Daily - {last['date']}\n\nAKTUELL:\n"
    ctx += f"  Kurs: {px(last['price'])}  EMA50: {px(last['ema50'])}  EMA200: {px(last['ema200'])}\n"
    ctx += f"  RSI: {last['rsi']}  MACD: {last['macd']}  Signal: {last['signal']}  Hist: {last['hist']}\n"
    if fund:
        def fp(v): return f"{v:.2f}" if v is not None else "-"
        def pct(v): return f"{v*100:.1f}%" if v is not None else "-"
        def mc(v):
            if not v: return "-"
            return f"${v/1e12:.2f}T" if v>=1e12 else f"${v/1e9:.2f}B"
        ctx += (f"\nFUNDAMENTALDATEN: MarktCap={mc(fund.get('marketCap'))} "
                f"KGV={fp(fund.get('trailingPE'))} KGV-fwd={fp(fund.get('forwardPE'))} "
                f"KBV={fp(fund.get('priceToBook'))} EPS={fp(fund.get('trailingEps'))} "
                f"Div={pct(fund.get('dividendYield'))} UmsatzWachstum={pct(fund.get('revenueGrowth'))} "
                f"GewinnWachstum={pct(fund.get('earningsGrowth'))} Marge={pct(fund.get('profitMargins'))} "
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
            "- HAUPTSZENARIO (XX%): Kursziel + Prozentveränderung\n"
            "- ALTERNATIVSZENARIO (XX%): Gegenszenario\n"
            "- ENTSCHEIDENDE MARKEN:\n"
            "- INVALIDIERUNGSLEVEL:\n"
            "- HANDLUNGSEMPFEHLUNG:\n"
        )}]
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages", data=payload,
        headers={"Content-Type":"application/json","x-api-key":key,"anthropic-version":"2023-06-01"},
        method="POST")
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read())["content"][0]["text"]

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
    def fp(v, dec=2): return f"{v:.{dec}f}" if v is not None else "—"
    def pct(v): return f"{v*100:.1f} %" if v is not None else "—"
    def mc(v):
        if not v: return "—"
        return f"${v/1e12:.2f} T" if v>=1e12 else f"${v/1e9:.2f} B"
    rows = [
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
        ("52W-Hoch",             fp(fund.get("week52High"))),
        ("52W-Tief",             fp(fund.get("week52Low"))),
    ]
    return pd.DataFrame(rows, columns=["Kennzahl", "Wert"])

# ── Hauptbereich ───────────────────────────────────────────────────────────────

st.title("📈 Aktienmarkt Analyse")
st.caption(f"Elliott Wave · RSI · MACD · EMA 50/200 · Fundamentaldaten · 48h-Prognose")

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

start_btn = st.button("🚀 Analyse starten", type="primary", use_container_width=True)

if start_btn:
    heute = datetime.date.today().strftime("%d.%m.%Y")
    gesamt_html = ""
    fortschritt = st.progress(0, text="Starte Analyse...")

    for idx, aktie in enumerate(ausgewaehlt):
        name    = aktie["name"]
        symbol  = aktie["symbol"]
        farbe   = aktie["color"]
        einheit = aktie["einheit"]
        anteil  = (idx + 1) / len(ausgewaehlt)

        st.subheader(f"{name}", divider="gray")
        col1, col2 = st.columns([1, 1])

        # Kursdaten
        fortschritt.progress(anteil * 0.3 + idx/len(ausgewaehlt)*0.7,
                             text=f"{name}: Lade Kursdaten...")
        try:
            raw  = fetch_yahoo(symbol)
            data = build(raw)
            last = data[-1]
        except Exception as e:
            st.error(f"Kursdaten-Fehler: {e}")
            continue

        # Technische Indikatoren anzeigen
        with col1:
            def clr(v, good, bad): return "🟢" if v==good else ("🔴" if v==bad else "🟡")
            ema50_ok  = last["price"] > (last["ema50"]  or 0)
            ema200_ok = last["price"] > (last["ema200"] or 0)
            rsi_val   = last["rsi"] or 0
            rsi_status = "Überkauft 🔴" if rsi_val>70 else ("Überverkauft 🟢" if rsi_val<30 else "Neutral 🟡")

            st.metric("Kurs", f"{last['price']:,.2f} {einheit}")
            tech_df = pd.DataFrame([
                ["EMA 50",      f"{last['ema50']:,.2f}" if last['ema50'] else "—",
                 "🟢 darüber" if ema50_ok else "🔴 darunter"],
                ["EMA 200",     f"{last['ema200']:,.2f}" if last['ema200'] else "—",
                 "🟢 darüber" if ema200_ok else "🔴 darunter"],
                ["RSI (14)",    str(rsi_val), rsi_status],
                ["MACD",        str(last["macd"]), "🟢 Bullish" if (last["macd"] or 0)>0 else "🔴 Bearish"],
                ["Histogramm",  str(last["hist"]), "🟢 steigt" if (last["hist"] or 0)>0 else "🔴 fällt"],
            ], columns=["Indikator", "Wert", "Status"])
            st.dataframe(tech_df, hide_index=True, use_container_width=True)

        # Fundamentaldaten
        fortschritt.progress(anteil * 0.5 + idx/len(ausgewaehlt)*0.5,
                             text=f"{name}: Lade Fundamentaldaten...")
        fund = fetch_fundamentals(symbol)

        with col2:
            if fund:
                st.markdown("**Fundamentaldaten**")
                st.dataframe(fmt_fund_df(fund), hide_index=True, use_container_width=True)
            else:
                st.info("Keine Fundamentaldaten verfügbar.")

        # Claude Analyse
        fortschritt.progress(anteil * 0.8 + idx/len(ausgewaehlt)*0.2,
                             text=f"{name}: Claude analysiert...")
        try:
            with st.spinner(f"Claude analysiert {name}..."):
                analyse_text = claude_analyse(name, einheit, data, fund, api_key)
        except Exception as e:
            st.error(f"API-Fehler: {e}")
            continue

        with st.expander("📋 Vollständige Analyse anzeigen", expanded=True):
            st.markdown(analyse_text)

        # HTML für E-Mail aufbauen
        if send_mail:
            from aktienmarkt_analyse import to_html
            gesamt_html += to_html(name, einheit, farbe, data, analyse_text, fund)
            gesamt_html += '<hr style="margin:10px 0 30px 0;border:none;border-top:3px solid #eee">'

        fortschritt.progress(anteil, text=f"{name}: fertig ✓")
        if idx < len(ausgewaehlt) - 1:
            time.sleep(1)

    fortschritt.progress(1.0, text="Analyse abgeschlossen ✓")

    # E-Mail senden
    if send_mail and gesamt_html:
        try:
            send_email_func(
                f"Aktienmarkt Elliott-Wave + 48h-Prognose - {heute}",
                gesamt_html, gmail_absender, gmail_passwort, empfaenger
            )
            st.success(f"✅ E-Mail gesendet an {empfaenger}")
        except Exception as e:
            st.error(f"E-Mail-Fehler: {e}")

    st.balloons()
