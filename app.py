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

ALLE_AKTIEN = [
    {"name": "S&P 500",   "symbol": "^GSPC", "color": "#1a73e8", "einheit": "Punkte"},
    {"name": "NVIDIA",    "symbol": "NVDA",  "color": "#76b900", "einheit": "USD"},
    {"name": "Apple",     "symbol": "AAPL",  "color": "#555555", "einheit": "USD"},
    {"name": "Microsoft", "symbol": "MSFT",  "color": "#00a4ef", "einheit": "USD"},
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://finance.yahoo.com/",
}

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Einstellungen")
    st.subheader("📊 Aktien auswählen")
    ausgewaehlt = []
    for a in ALLE_AKTIEN:
        if st.checkbox(a["name"], value=True):
            ausgewaehlt.append(a)
    st.divider()
    st.subheader("📧 E-Mail (optional)")
    send_mail = st.toggle("E-Mail senden", value=False)
    if send_mail:
        gmail_absender = st.text_input("Absender (Gmail)", value=get_secret("GMAIL_ABSENDER"))
        gmail_passwort = st.text_input("App-Passwort", value=get_secret("GMAIL_APP_PASSWORT"), type="password")
        empfaenger     = st.text_input("Empfänger",    value=get_secret("EMPFAENGER"))

# ── Datenabruf ─────────────────────────────────────────────────────────────────
def fetch_yahoo(symbol, days=400):
    now   = datetime.datetime.now(datetime.timezone.utc)
    end   = int(now.timestamp())
    start = int((now - datetime.timedelta(days=days)).timestamp())
    url   = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&period1={start}&period2={end}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.loads(r.read())
    result = data["chart"]["result"][0]
    return [{"date": datetime.date.fromtimestamp(ts).isoformat(), "close": round(float(c), 4)}
            for ts, c in zip(result["timestamp"], result["indicators"]["quote"][0]["close"])
            if c is not None and c > 0]

def fetch_fundamentals(symbol):
    # Versuch 1: yfinance (robuster, handhabt Cookies automatisch)
    try:
        import yfinance as yf
        info = yf.Ticker(symbol).info
        if info and len(info) > 5:
            def g(k): return info.get(k)
            fund = {
                "marketCap": g("marketCap"), "trailingPE": g("trailingPE"),
                "forwardPE": g("forwardPE"), "priceToBook": g("priceToBook"),
                "trailingEps": g("trailingEps"), "dividendYield": g("dividendYield"),
                "revenueGrowth": g("revenueGrowth"), "earningsGrowth": g("earningsGrowth"),
                "profitMargins": g("profitMargins"), "returnOnEquity": g("returnOnEquity"),
                "debtToEquity": g("debtToEquity"),
                "week52High": g("fiftyTwoWeekHigh"), "week52Low": g("fiftyTwoWeekLow"),
            }
            if any(v is not None for v in fund.values()):
                return fund
    except Exception:
        pass
    # Versuch 2: direkte Yahoo Finance API
    try:
        url = (f"https://query2.finance.yahoo.com/v11/finance/quoteSummary/{symbol}"
               f"?modules=financialData%2CdefaultKeyStatistics%2CsummaryDetail")
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read())
        res = data["quoteSummary"]["result"][0]
        fd, ks, sd = res.get("financialData",{}), res.get("defaultKeyStatistics",{}), res.get("summaryDetail",{})
        def v(d, k):
            x = d.get(k, {})
            return x.get("raw") if isinstance(x, dict) else x
        fund = {
            "marketCap": v(ks,"marketCap"), "trailingPE": v(sd,"trailingPE"),
            "forwardPE": v(ks,"forwardPE"), "priceToBook": v(ks,"priceToBook"),
            "trailingEps": v(ks,"trailingEps"), "dividendYield": v(sd,"dividendYield"),
            "revenueGrowth": v(fd,"revenueGrowth"), "earningsGrowth": v(fd,"earningsGrowth"),
            "profitMargins": v(fd,"profitMargins"), "returnOnEquity": v(fd,"returnOnEquity"),
            "debtToEquity": v(fd,"debtToEquity"),
            "week52High": v(sd,"fiftyTwoWeekHigh"), "week52Low": v(sd,"fiftyTwoWeekLow"),
        }
        if any(val is not None for val in fund.values()):
            return fund
    except Exception:
        pass
    return {}

# ── Indikatoren ────────────────────────────────────────────────────────────────
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
    e12=ema(prices,12); e26=ema(prices,26)
    ml=[round(e12[i]-e26[i],4) if e12[i] and e26[i] else None for i in range(len(prices))]
    st_=next(i for i,x in enumerate(ml) if x is not None)
    sr=ema([x for x in ml if x is not None],9)
    sig=[None if ml[i] is None else sr[i-st_] for i in range(len(prices))]
    hist=[round(ml[i]-sig[i],4) if ml[i] is not None and sig[i] is not None else None for i in range(len(prices))]
    return ml, sig, hist

def build(raw):
    prices=[r["close"] for r in raw]
    e50,e200=ema(prices,50),ema(prices,200)
    r14=rsi(prices); ml,sig,hist=macd(prices)
    return [{"date":raw[i]["date"],"price":raw[i]["close"],
             "ema50":e50[i],"ema200":e200[i],
             "rsi":r14[i],"macd":ml[i],"signal":sig[i],"hist":hist[i]}
            for i in range(len(raw))]

# ── Regelbasierte Prognose ─────────────────────────────────────────────────────
def generate_prognose(data):
    last = data[-1]
    signals_bull, signals_bear = [], []

    # EMA-Trend
    p, e50, e200 = last["price"], last["ema50"] or 0, last["ema200"] or 0
    if p > e50 > e200:
        signals_bull.append("Golden Cross / Preis über EMA50 & EMA200")
    elif p < e50 < e200:
        signals_bear.append("Death Cross / Preis unter EMA50 & EMA200")
    elif p > e50:
        signals_bull.append("Preis über EMA50")
    else:
        signals_bear.append("Preis unter EMA50")

    # RSI
    r = last["rsi"] or 50
    if r > 70:
        signals_bear.append(f"RSI überkauft ({r})")
    elif r < 30:
        signals_bull.append(f"RSI überverkauft – Erholung wahrscheinlich ({r})")
    elif r > 55:
        signals_bull.append(f"RSI bullish ({r})")
    elif r < 45:
        signals_bear.append(f"RSI bearish ({r})")

    # MACD
    if last["macd"] is not None and last["signal"] is not None:
        if last["macd"] > last["signal"]:
            signals_bull.append("MACD über Signal-Linie")
        else:
            signals_bear.append("MACD unter Signal-Linie")

    # Histogramm-Richtung
    if len(data) >= 3:
        h1, h2 = last["hist"], data[-2]["hist"]
        if h1 is not None and h2 is not None:
            if h1 > h2:
                signals_bull.append("Histogramm steigt (zunehmendes Momentum)")
            else:
                signals_bear.append("Histogramm fällt (abnehmendes Momentum)")

    # Kurzfristiger Preisimpuls (letzte 3 Tage)
    if len(data) >= 4:
        trend3 = data[-1]["price"] - data[-4]["price"]
        if trend3 > 0:
            signals_bull.append(f"3-Tage-Impuls positiv (+{trend3:.2f})")
        else:
            signals_bear.append(f"3-Tage-Impuls negativ ({trend3:.2f})")

    nb, nd = len(signals_bull), len(signals_bear)
    total = max(nb + nd, 1)
    bull_pct = round(nb / total * 100)
    bear_pct = 100 - bull_pct
    main_bull = bull_pct >= bear_pct

    # Kursziele aus jüngster Volatilität
    recent = [d["price"] for d in data[-10:]]
    atr = (max(recent) - min(recent)) / len(recent)
    target_main = p + atr * 1.5 if main_bull else p - atr * 1.5
    target_alt  = p - atr if main_bull else p + atr
    inval       = p - atr * 2 if main_bull else p + atr * 2

    if bull_pct >= 70:
        empfehlung = "Vorsichtiger Long-Aufbau möglich"
    elif bear_pct >= 70:
        empfehlung = "Kein Long-Einstieg empfohlen"
    else:
        empfehlung = "Abwarten auf Bestätigung"

    return {
        "main_bull": main_bull,
        "bull_pct": bull_pct,
        "bear_pct": bear_pct,
        "target_main": target_main,
        "target_alt": target_alt,
        "inval": inval,
        "signals_bull": signals_bull,
        "signals_bear": signals_bear,
        "empfehlung": empfehlung,
        "current": p,
    }

# ── Anzeige-Hilfsfunktionen ────────────────────────────────────────────────────
def fmt_fund_df(fund):
    def fp(v): return f"{v:.2f}" if v is not None else "—"
    def pct(v): return f"{v*100:.1f} %" if v is not None else "—"
    def mc(v): return (f"${v/1e12:.2f} T" if v>=1e12 else f"${v/1e9:.2f} B") if v else "—"
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

def show_prognose(prog, einheit):
    richtung = "📈 BULLISCH" if prog["main_bull"] else "📉 BÄRISCH"
    farbe    = "green" if prog["main_bull"] else "red"
    p        = prog["current"]
    pct_main = (prog["target_main"] - p) / p * 100
    pct_alt  = (prog["target_alt"]  - p) / p * 100

    st.subheader(f"🕐 2-Tages-Prognose (48h) — :{farbe}[{richtung}]")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(
            f"Hauptszenario ({prog['bull_pct']}%)",
            f"{prog['target_main']:,.2f} {einheit}",
            f"{pct_main:+.2f}%"
        )
    with c2:
        st.metric(
            f"Alternativszenario ({prog['bear_pct']}%)",
            f"{prog['target_alt']:,.2f} {einheit}",
            f"{pct_alt:+.2f}%"
        )
    with c3:
        st.metric("Invalidierungslevel", f"{prog['inval']:,.2f} {einheit}")

    st.info(f"**Handlungsempfehlung:** {prog['empfehlung']}")

    with st.expander("📊 Signal-Details"):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**🟢 Bullische Signale**")
            for s in prog["signals_bull"]:
                st.markdown(f"- {s}")
        with c2:
            st.markdown("**🔴 Bärische Signale**")
            for s in prog["signals_bear"]:
                st.markdown(f"- {s}")

# ── Hauptbereich ───────────────────────────────────────────────────────────────
st.title("📈 Aktienmarkt Analyse")
st.caption("Elliott Wave · RSI · MACD · EMA 50/200 · Fundamentaldaten · 48h-Prognose")

if not ausgewaehlt:
    st.warning("Bitte mindestens eine Aktie auswählen.")
    st.stop()

def send_email_func(subject, html_body, absender, passwort, emp):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    msg = MIMEMultipart("alternative")
    msg["Subject"]=subject; msg["From"]=absender; msg["To"]=emp
    msg.attach(MIMEText(html_body,"html","utf-8"))
    with smtplib.SMTP_SSL("smtp.gmail.com",465) as s:
        s.login(absender,passwort)
        s.sendmail(absender,emp,msg.as_string())

if st.button("🚀 Analyse starten", type="primary", width='stretch'):
    heute = datetime.date.today().strftime("%d.%m.%Y")
    bar = st.progress(0, text="Starte...")
    n = len(ausgewaehlt)

    for idx, aktie in enumerate(ausgewaehlt):
        name    = aktie["name"]
        symbol  = aktie["symbol"]
        farbe   = aktie["color"]
        einheit = aktie["einheit"]

        st.subheader(name, divider="gray")

        bar.progress((idx*3+1)/(n*3), text=f"{name}: Kursdaten...")
        try:
            raw  = fetch_yahoo(symbol)
            data = build(raw)
            last = data[-1]
        except Exception as e:
            st.error(f"Kursdaten-Fehler: {e}"); continue

        # 1. PROGNOSE OBEN
        prog = generate_prognose(data)
        show_prognose(prog, einheit)

        st.markdown("---")

        # 2. Technische Indikatoren
        bar.progress((idx*3+2)/(n*3), text=f"{name}: Indikatoren & Fundamentaldaten...")
        col1, col2 = st.columns(2)
        with col1:
            ema50_ok  = last["price"] > (last["ema50"]  or 0)
            ema200_ok = last["price"] > (last["ema200"] or 0)
            rsi_val   = last["rsi"] or 0
            st.metric("Aktueller Kurs", f"{last['price']:,.2f} {einheit}")
            st.dataframe(pd.DataFrame([
                ["EMA 50",     f"{last['ema50']:,.2f}" if last['ema50'] else "—", "🟢 darüber" if ema50_ok  else "🔴 darunter"],
                ["EMA 200",    f"{last['ema200']:,.2f}" if last['ema200'] else "—", "🟢 darüber" if ema200_ok else "🔴 darunter"],
                ["RSI (14)",   str(rsi_val), "🔴 Überkauft" if rsi_val>70 else ("🟢 Überverkauft" if rsi_val<30 else "🟡 Neutral")],
                ["MACD",       str(last["macd"]), "🟢 Bullish" if (last["macd"] or 0)>0 else "🔴 Bearish"],
                ["Histogramm", str(last["hist"]), "🟢 steigt"  if (last["hist"] or 0)>0 else "🔴 fällt"],
            ], columns=["Indikator", "Wert", "Status"]), hide_index=True, width='stretch')

        # 3. Fundamentaldaten
        fund = fetch_fundamentals(symbol)
        with col2:
            if fund:
                st.markdown("**Fundamentaldaten**")
                st.dataframe(fmt_fund_df(fund), hide_index=True, width='stretch')
            else:
                st.info("Keine Fundamentaldaten verfügbar (Index oder API-Limit)")

        bar.progress((idx*3+3)/(n*3), text=f"{name}: fertig ✓")
        if idx < n-1:
            time.sleep(1)

    bar.progress(1.0, text="Fertig ✓")

    if send_mail:
        try:
            send_email_func(f"Aktienmarkt Analyse - {heute}", "<p>Analyse abgeschlossen.</p>",
                            gmail_absender, gmail_passwort, empfaenger)
            st.success(f"✅ E-Mail gesendet an {empfaenger}")
        except Exception as e:
            st.error(f"E-Mail-Fehler: {e}")

    st.balloons()
