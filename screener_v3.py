"""
美股綜合 Screener v3 — GitHub Actions 版
=========================================
自動輸出 docs/index.html 供 GitHub Pages 顯示
包含：主選股 Tab + 資料庫統計 Tab

資料庫入庫條件：K線分 ≥ 72 OR 綜合分 ≥ 70
資料庫位置：docs/stats_db.json（隨 HTML 一起推上 GitHub）

執行：python screener_v3.py [CORE|SOX|NDX|SPX|ALL]
"""

import yfinance as yf
import pandas as pd
import numpy as np
import json, os, time, sys, argparse
from datetime import datetime, timedelta

# ══════════════════════════════════════════════════════════════
# 成分股清單
# ══════════════════════════════════════════════════════════════

SOX_TICKERS = [
    "NVDA","AVGO","TSM","QCOM","AMD","TXN","AMAT","INTC","LRCX","KLAC",
    "MU","MRVL","ADI","NXPI","MCHP","ON","STM","MPWR","SWKS","QRVO",
    "WOLF","ENTG","COHR","AMKR","RMBS","CRUS","SLAB","ONTO","UMC","ASML",
]

NDX_TICKERS = [
    "ADBE","ADP","ABNB","GOOGL","GOOG","AMZN","AMD","AEP","AMGN","ADI",
    "AAPL","AMAT","ASML","AZN","TEAM","ADSK","BIDU","BIIB","BKNG","AVGO","CDNS",
    "CDW","CHTR","CTAS","CSCO","CMCSA","CPRT","CSGP","COST","CRWD","CSX","DDOG",
    "DXCM","FANG","DLTR","DASH","EA","EXC","FAST","FTNT","GEHC","GILD","GFS",
    "HON","IDXX","ILMN","INTC","INTU","ISRG","KDP","KLAC","KHC","LRCX","LULU",
    "MAR","MRVL","MELI","META","MCHP","MU","MSFT","MDLZ","MNST","NFLX","NVDA",
    "NXPI","ORLY","ON","PCAR","PANW","PAYX","PYPL","PDD","QCOM","REGN","ROP",
    "ROST","SBUX","SNPS","TMUS","TSLA","TXN","TTD","VRSK","VRTX","WBD",
    "WDAY","XEL","ZS","ZM",
]

SPX_CORE_TICKERS = [
    "AAPL","MSFT","GOOGL","GOOG","AMZN","META","TSLA","NVDA","AVGO",
    "CRM","ORCL","NOW","ADBE","INTU","PANW","CRWD","FTNT","SNPS","CDNS",
    "ANET","IBM","ACN","CTSH","GDDY","EPAM","AKAM","FFIV","VRSN",
    "TXN","QCOM","INTC","AMD","AMAT","LRCX","KLAC","MU","ADI","MCHP",
    "UNH","JNJ","LLY","ABBV","MRK","TMO","ABT","DHR","BSX","ISRG",
    "REGN","VRTX","GILD","AMGN","BIIB","MRNA","EW","IDXX","IQV","STE",
    "HCA","CVS","CI","ELV","MOH","HUM","HOLX","PODD","DXCM","RMD",
    "JPM","BAC","GS","MS","BLK","BX","KKR","SCHW","C","WFC",
    "AXP","V","MA","PYPL","ICE","CME","SPGI","MCO","CBOE","MSCI",
    "COF","AIG","PRU","MET","ALL","PGR","CB","AFL","RJF","BK",
    "AMZN","HD","LOW","TGT","COST","WMT","MCD","SBUX","CMG","YUM",
    "NKE","LULU","DECK","TJX","ROST","ORLY","AZO","TSCO","ULTA","RCL",
    "CCL","LVS","WYNN","MGM","MAR","HLT","BKNG","EXPE","ABNB","NCLH",
    "GE","HON","CAT","DE","ETN","EMR","ITW","ROK","CARR","OTIS",
    "LMT","RTX","NOC","GD","LHX","HII","BA","TDG","HWM","GEV",
    "PCAR","CMI","AXON","PWR","BLDR","MLM","VMC","URI","FAST","ODFL",
    "XOM","CVX","COP","EOG","SLB","MPC","PSX","VLO","OXY","HAL",
    "FANG","DVN","EQT","CTRA","BKR","TRGP","OKE",
    "GOOGL","META","NFLX","DIS","CMCSA","T","VZ","TMUS","WBD","TTWO",
    "EA","EBAY","MTCH","OMC","IPG",
    "LIN","APD","ECL","SHW","PPG","FCX","NEM","ALB","CE","DD","DOW","LYB",
    "MDT","SYK","ZBH","BAX","BDX","TFX","COO","HOLX","WAT","A","RVTY",
    "BRK-B","MMM","GIS","TSN","ADM","MOS","CF",
    "CPRT","CSGP","VRSK","IRM","EQIX","DLR",
    "SPGI","MCO","MKTX","NDAQ","ICE",
    "UNP","CSX","NSC","UAL","DAL","AAL","UPS","FDX",
    "AMP","IVZ","TROW","BEN","PFG",
]

SPX_TICKERS = [
    "MMM","AOS","ABT","ABBV","ACN","ADBE","AMD","AES","AFL","A","APD","ABNB",
    "AKAM","ALB","ARE","ALGN","ALLE","LNT","ALL","GOOGL","GOOG","MO","AMZN",
    "AMCR","AEE","AAL","AEP","AXP","AIG","AMT","AWK","AMP","AME","AMGN","APH",
    "ADI","AON","APA","AAPL","AMAT","APTV","ACGL","ADM","ANET","AJG",
    "AIZ","T","ATO","ADSK","ADP","AZO","AVB","AVY","AXON","BKR","BALL","BAC",
    "BK","BBWI","BAX","BDX","WRB","BRK-B","BBY","BIO","TECH","BIIB","BLK",
    "BX","BA","BSX","BMY","AVGO","BR","BRO","BF-B","BLDR","BG","CDNS","CZR",
    "CPT","CPB","COF","CAH","KMX","CCL","CARR","CAT","CBOE","CBRE","CDW","CE",
    "COR","CNC","CDAY","CF","CRL","SCHW","CHTR","CVX","CMG","CB","CHD","CI",
    "CINF","CTAS","CSCO","C","CFG","CLX","CME","CMS","KO","CTSH","CL","CMCSA",
    "CAG","COP","ED","STZ","CEG","COO","CPRT","GLW","CPAY","CTVA","CSGP","COST",
    "CTRA","CRWD","CCI","CSX","CMI","CVS","DHR","DRI","DVA","DECK","DE","DAL",
    "DVN","DXCM","FANG","DLR","DFS","DG","DLTR","D","DPZ","DOV","DOW","DHI",
    "DTE","DUK","DD","EMN","ETN","EBAY","ECL","EIX","EW","EA","ELV","LLY","EMR",
    "ENPH","ETR","EOG","EQT","EFX","EQIX","EQR","ESS","EL","ETSY","EG","ES",
    "EXC","EXPE","EXPD","EXR","XOM","FFIV","FDS","FICO","FAST","FRT","FDX","FIS",
    "FITB","FSLR","FE","FI","FMC","F","FTNT","FTV","FOXA","FOX","BEN","FCX",
    "GRMN","IT","GE","GEHC","GEV","GEN","GNRC","GD","GIS","GM","GPC","GILD",
    "GPN","GL","GDDY","GS","HAL","HIG","HAS","HCA","HSIC","HSY","HES","HPE",
    "HLT","HOLX","HD","HON","HRL","HST","HWM","HPQ","HUBB","HUM","HBAN","HII",
    "IBM","IEX","IDXX","ITW","INCY","IR","PODD","INTC","ICE","IFF","IP","IPG",
    "INTU","ISRG","IVZ","INVH","IQV","IRM","JBHT","JBL","JKHY","J","JNJ","JCI",
    "JPM","K","KDP","KEY","KEYS","KMB","KIM","KMI","KKR","KLAC","KHC","KR",
    "LHX","LH","LRCX","LW","LVS","LDOS","LEN","LII","LIN","LYV","LKQ","LMT",
    "L","LOW","LULU","LYB","MTB","MRO","MPC","MKTX","MAR","MMC","MLM","MAS",
    "MA","MTCH","MKC","MCD","MCK","MDT","MRK","META","MET","MTD","MGM","MCHP",
    "MU","MSFT","MAA","MRNA","MHK","MOH","TAP","MDLZ","MPWR","MNST","MCO","MS",
    "MOS","MSI","MSCI","NDAQ","NTAP","NFLX","NEM","NWSA","NWS","NEE","NKE","NI",
    "NDSN","NSC","NTRS","NOC","NCLH","NRG","NUE","NVDA","NVR","NXPI","ORLY",
    "OXY","ODFL","OMC","ON","OKE","ORCL","OTIS","PCAR","PKG","PANW","PH","PAYX",
    "PAYC","PYPL","PNR","PEP","PFE","PCG","PM","PSX","PNW","PNC","POOL","PPG",
    "PPL","PFG","PG","PGR","PLD","PRU","PEG","PTC","PSA","PHM","QRVO","PWR",
    "QCOM","DGX","RL","RJF","RTX","O","REG","REGN","RF","RSG","RMD","RVTY",
    "ROK","ROL","ROP","ROST","RCL","SPGI","CRM","SBAC","SLB","STX","SRE","NOW",
    "SHW","SPG","SWKS","SJM","SNA","SOLV","SO","LUV","SWK","SBUX","STT","STLD",
    "STE","SYK","SYF","SNPS","SYY","TMUS","TROW","TTWO","TPR","TRGP","TGT",
    "TEL","TDY","TFX","TER","TSLA","TXN","TMO","TJX","TSCO","TT","TDG","TRV",
    "TRMB","TFC","TYL","TSN","USB","UBER","UDR","ULTA","UNP","UAL","UPS","URI",
    "UNH","UHS","VLO","VTR","VLTO","VRSN","VRSK","VZ","VRTX","VTRS","VICI","V",
    "VST","VMC","WAB","WMT","DIS","WBD","WM","WAT","WEC","WFC","WELL",
    "WST","WDC","WHR","WLK","WTW","WY","WYNN","XEL","XYL","YUM","ZBRA","ZBH","ZTS",
]

def build_core():
    seen, result = set(), []
    for t in SOX_TICKERS + NDX_TICKERS + SPX_CORE_TICKERS:
        if t not in seen:
            seen.add(t)
            result.append(t)
    return result

INDEX_MAP = {
    "CORE": (None, "精選池（SOX+NDX+SPX優質股，約200檔）"),
    "SOX":  (SOX_TICKERS, "SOX 費城半導體指數 30檔"),
    "NDX":  (NDX_TICKERS, "Nasdaq-100 約100檔"),
    "SPX":  (SPX_TICKERS, "S&P 500 完整版（約500檔）"),
    "ALL":  (None, "SOX + S&P500 + NDX 合併去重（約550檔）"),
}

# ══════════════════════════════════════════════════════════════
# 工具函數
# ══════════════════════════════════════════════════════════════

def calc_rsi(series, period=14):
    if len(series) < period + 1:
        return None
    delta = series.diff().dropna()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    val = rsi.iloc[-1]
    return round(float(val), 1) if not np.isnan(val) else None

def fmt(val, decimals=2, prefix="", suffix="", na="N/A"):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return na
    return f"{prefix}{val:.{decimals}f}{suffix}"

# ══════════════════════════════════════════════════════════════
# K線技術計分引擎（完整移植自 kline-analysis-v2.2）
# ══════════════════════════════════════════════════════════════

_STRATEGY_WEIGHTS = {
    "balanced": dict(ma=1.0, rsi=1.0, kd=1.0, macd=1.0, vol=1.0, pattern=1.0),
    "breakout": dict(ma=1.3, rsi=0.6, kd=0.7, macd=1.4, vol=1.8, pattern=1.3),
    "pullback": dict(ma=1.4, rsi=1.2, kd=1.2, macd=0.5, vol=1.3, pattern=1.1),
    "reversal": dict(ma=0.4, rsi=2.0, kd=2.0, macd=0.6, vol=1.5, pattern=1.8),
}

def _detect_rsi_divergence(data, rsi_arr):
    n = len(data)
    if n < 20:
        return None
    wb = 5
    price_highs, price_lows = [], []
    rsi_highs, rsi_lows = [], []
    for i in range(wb, n - wb):
        rv = rsi_arr[i]
        if rv is None:
            continue
        window_rsi = [v for v in rsi_arr[i-wb:i+wb+1] if v is not None]
        is_p_high = all(data[j]["close"] <= data[i]["close"] for j in range(i-wb, i+wb+1) if j != i)
        is_p_low  = all(data[j]["close"] >= data[i]["close"] for j in range(i-wb, i+wb+1) if j != i)
        is_r_high = all(r <= rv for r in window_rsi)
        is_r_low  = all(r >= rv for r in window_rsi)
        if is_p_high and is_r_high:
            price_highs.append({"i": i, "price": data[i]["close"]})
            rsi_highs.append({"i": i, "val": rv})
        if is_p_low and is_r_low:
            price_lows.append({"i": i, "price": data[i]["close"]})
            rsi_lows.append({"i": i, "val": rv})
    if (len(price_highs) >= 2 and len(rsi_highs) >= 2
            and price_highs[-1]["price"] > price_highs[-2]["price"]
            and rsi_highs[-1]["val"] < rsi_highs[-2]["val"]):
        return "bear"
    if (len(price_lows) >= 2 and len(rsi_lows) >= 2
            and price_lows[-1]["price"] < price_lows[-2]["price"]
            and rsi_lows[-1]["val"] > rsi_lows[-2]["val"]):
        return "bull"
    return None


def calc_kline_score(ohlcv):
    data = ohlcv
    n = len(data)
    if n < 20:
        return None

    def _ma(p):
        return [None if i < p-1 else sum(d["close"] for d in data[i-p+1:i+1]) / p for i in range(n)]

    def _rsi_arr(p=14):
        g, l = [], []
        for i in range(1, n):
            dv = data[i]["close"] - data[i-1]["close"]
            g.append(dv if dv > 0 else 0)
            l.append(-dv if dv < 0 else 0)
        return [None if i < p else
                (100 if sum(l[i-p:i]) == 0 else
                 100 - 100 / (1 + sum(g[i-p:i])/p / (sum(l[i-p:i])/p)))
                for i in range(n)]

    def _kdj(p=9):
        pk, pd_ = 50.0, 50.0
        result = []
        for i in range(n):
            if i < p-1:
                result.append(None); continue
            sl = data[i-p+1:i+1]
            hi = max(b["high"] for b in sl)
            lo = min(b["low"] for b in sl)
            rsv = 50 if hi == lo else (data[i]["close"] - lo) / (hi - lo) * 100
            kv = pk * 2/3 + rsv / 3
            dv = pd_ * 2/3 + kv / 3
            pk, pd_ = kv, dv
            result.append({"k": kv, "d": dv})
        return result

    def _bb(p=20):
        ma_arr = _ma(p)
        result = []
        for i in range(n):
            if ma_arr[i] is None:
                result.append(None); continue
            sl = data[i-p+1:i+1]; mean = ma_arr[i]
            std = (sum((d["close"] - mean)**2 for d in sl) / p) ** 0.5
            result.append({"upper": mean + 2*std, "lower": mean - 2*std, "mid": mean})
        return result

    def _avg_vol(p=20):
        return [None if i < p-1 else sum(d["volume"] for d in data[i-p+1:i+1]) / p for i in range(n)]

    def _macd(fast=12, slow=26, sig=9):
        closes = [d["close"] for d in data]
        def ema(arr, p):
            if not arr: return []
            k = 2/(p+1); e = arr[0]; r = []
            for i, v in enumerate(arr):
                e = v*k + e*(1-k) if i > 0 else e
                r.append(e)
            return r
        ef, es = ema(closes, fast), ema(closes, slow)
        ml = [ef[i] - es[i] for i in range(n)]
        ml_slice = ml[slow-1:]
        sl2 = ema(ml_slice, sig) if len(ml_slice) >= sig else []
        result = []
        for i in range(n):
            if i < slow-1:
                result.append(None); continue
            si = i - (slow-1); m = ml[i]
            sg = sl2[si-(sig-1)] if sl2 and si >= sig-1 else None
            result.append({"macd": m, "signal": sg, "hist": m-sg if sg is not None else None})
        return result

    ma5a  = _ma(5); ma10a = _ma(10); ma20a = _ma(20); ma60a = _ma(60)
    rsiA  = _rsi_arr(); kdjA = _kdj(); bbA = _bb(); avgVA = _avg_vol()
    macdA = _macd()

    last = data[n-1]; prev = data[n-2]
    lma5  = ma5a[n-1];  lma10 = ma10a[n-1]; lma20 = ma20a[n-1]; lma60 = ma60a[n-1]
    pma5  = ma5a[n-2];  pma10 = ma10a[n-2]
    lrsi  = rsiA[n-1];  prsi  = rsiA[n-2]
    lkdj  = kdjA[n-1];  pkdj  = kdjA[n-2]
    lbb   = bbA[n-1];   lavg  = avgVA[n-1]
    lmacd = macdA[n-1]; pmacd = macdA[n-2]

    body       = abs(last["close"] - last["open"])
    range_     = last["high"] - last["low"]
    upShadow   = last["high"] - max(last["close"], last["open"])
    downShadow = min(last["close"], last["open"]) - last["low"]
    isBull = last["close"] > last["open"]
    isBear = last["close"] < last["open"]
    volRatio = (last["volume"] / lavg) if lavg else 1.0

    vol20avg_as = sum(d["volume"] for d in data[-20:]) / min(20, n)
    vol5avg_as  = sum(d["volume"] for d in data[-5:]) / min(5, n)
    volShrink_as = vol5avg_as < vol20avg_as * 0.85
    lma60_as = (sum(d["close"] for d in data[-60:]) / 60) if n >= 60 else None
    week5  = sum(d["close"] for d in data[-5:]) / min(5, n)
    week20 = sum(d["close"] for d in data[-20:]) / min(20, n)

    if lrsi is not None and lrsi < 35 and lkdj and lkdj["k"] < 30:
        auto_strat = "reversal"
    elif (volRatio > 1.5 and isBull and lmacd and lmacd["macd"] is not None
          and lmacd["macd"] > 0 and lmacd["hist"] is not None and lmacd["hist"] > 0):
        auto_strat = "breakout"
    elif lma20 and abs(last["close"] - lma20)/lma20 < 0.05 and volShrink_as and lrsi and 38 < lrsi < 62:
        auto_strat = "pullback"
    elif lma60_as and abs(last["close"] - lma60_as)/lma60_as < 0.06 and volShrink_as and lrsi and lrsi > 35:
        auto_strat = "pullback"
    elif week5 > week20 and lma5 and lma10 and lma20 and lma5 > lma10 > lma20:
        auto_strat = "breakout"
    else:
        auto_strat = "balanced"

    w = _STRATEGY_WEIGHTS[auto_strat]

    ma_bull = 0; ma_bear = 0
    rsi_bull = 0; rsi_bear = 0
    kd_bull = 0; kd_bear = 0
    macd_bull = 0; macd_bear = 0
    vol_bull = 0; vol_bear = 0
    pat_bull = 0; pat_bear = 0
    extra_bull = 0; extra_bear = 0

    if lma5 and lma10 and lma20 and lma60:
        if lma5 > lma10 > lma20 > lma60:
            ma_bull += 15
        elif lma5 > lma10 > lma20:
            ma_bull += 8
        elif lma5 < lma10 < lma20:
            ma_bear += 4 if auto_strat == "pullback" else 12
    if lma5 and pma5 and lma10 and pma10:
        if pma5 <= pma10 and lma5 > lma10: ma_bull += 10
        elif pma5 >= pma10 and lma5 < lma10: ma_bear += 10
    if lma20:
        if last["close"] > lma20: ma_bull += 5
    if lma60:
        if last["close"] > lma60: ma_bull += 5
    if lma20 and n >= 2:
        prev_close = data[n-2]["close"]
        if prev_close <= lma20 and last["close"] > lma20:
            ma_bull += 8
        elif prev_close >= lma20 and last["close"] < lma20:
            ma_bear += 8

    _RSI_THRESHOLDS = {
        "balanced": (70, 35),
        "breakout": (85, 30),
        "pullback": (65, 38),
        "reversal": (58, 42),
    }
    rsiOB, rsiOS = _RSI_THRESHOLDS[auto_strat]
    if lrsi is not None:
        if prsi is not None and prsi < rsiOS and lrsi > rsiOS:
            rsi_bull += 10
        elif lrsi < rsiOS:
            rsi_bull += 6
        elif prsi is not None and prsi > rsiOB and lrsi < rsiOB:
            rsi_bear += 8
        elif lrsi > 80:
            rsi_bear += 8
        elif lrsi > rsiOB:
            rsi_bear += 4
        elif lrsi >= 50:
            rsi_bull += 4

    div_result = _detect_rsi_divergence(data, rsiA)
    if div_result == "bull": rsi_bull += 14
    elif div_result == "bear": rsi_bear += 14

    if lkdj and pkdj:
        if pkdj["k"] < pkdj["d"] and lkdj["k"] > lkdj["d"] and lkdj["k"] < 50:
            kd_bull += 12
        elif pkdj["k"] < pkdj["d"] and lkdj["k"] > lkdj["d"]:
            kd_bull += 7
        elif pkdj["k"] > pkdj["d"] and lkdj["k"] < lkdj["d"] and lkdj["k"] > 80:
            kd_bear += 12
        elif pkdj["k"] > pkdj["d"] and lkdj["k"] < lkdj["d"]:
            kd_bear += 6
        elif lkdj["k"] > lkdj["d"] and lkdj["k"] < 80:
            kd_bull += 3

    if lmacd and pmacd:
        if pmacd["macd"] is not None and lmacd["macd"] is not None:
            if lmacd["macd"] > 0: macd_bull += 5
            else: macd_bear += 5
            if pmacd["macd"] < 0 and lmacd["macd"] >= 0: macd_bull += 12
            elif pmacd["macd"] > 0 and lmacd["macd"] <= 0: macd_bear += 12
        if all(x is not None for x in [pmacd["signal"], lmacd["signal"], pmacd["macd"], lmacd["macd"]]):
            if pmacd["macd"] < pmacd["signal"] and lmacd["macd"] > lmacd["signal"]: macd_bull += 8
            elif pmacd["macd"] > pmacd["signal"] and lmacd["macd"] < lmacd["signal"]: macd_bear += 8
        if lmacd["hist"] is not None and pmacd["hist"] is not None:
            if lmacd["hist"] > 0 and lmacd["hist"] > pmacd["hist"]: macd_bull += 4
            elif lmacd["hist"] < 0 and lmacd["hist"] < pmacd["hist"]: macd_bear += 4

    if isBull and volRatio > 1.5:
        vol_bull += 10
    elif isBull and volRatio > 1.2:
        vol_bull += 6
    elif isBull and 0.6 <= volRatio <= 1.2 and auto_strat == "pullback":
        vol_bull += 8
    elif isBear and volRatio > 1.5:
        vol_bear += 10
    elif volRatio < 0.5 and auto_strat == "pullback":
        vol_bull += 5

    if lbb:
        if last["close"] < lbb["lower"]: pat_bull += 7
        elif last["close"] > lbb["upper"]: pat_bear += 4

    r60 = data[-min(60, n):]
    hi60 = max(d["high"] for d in r60); lo60 = min(d["low"] for d in r60)
    pos60 = (last["close"] - lo60) / (hi60 - lo60 + 1e-9)

    def eff_pts(dir_, min_vol=1.0):
        vol_ok = volRatio >= min_vol
        if dir_ == "bull":
            if pos60 < 0.35 and vol_ok: return 12
            if pos60 < 0.35: return 7
            if pos60 > 0.65: return 3
            return 7
        else:
            if pos60 > 0.65 and vol_ok: return 12
            if pos60 > 0.65: return 7
            if pos60 < 0.35: return 3
            return 7

    if range_ > 0 and downShadow >= body*2 and upShadow <= body*0.5 and body > 0:
        pat_bull += eff_pts("bull", 1.2)
    if isBull and body >= range_*0.7 and volRatio >= 1.2:
        pat_bull += eff_pts("bull", 1.2) + 2
    if isBear and body >= range_*0.7 and volRatio >= 1.2:
        pat_bear += eff_pts("bear", 1.2) + 2
    if isBull and prev["close"] < prev["open"] and last["open"] <= prev["close"] and last["close"] >= prev["open"]:
        pat_bull += eff_pts("bull", 1.3) + 3
    if isBear and prev["close"] > prev["open"] and last["open"] >= prev["close"] and last["close"] <= prev["open"]:
        pat_bear += eff_pts("bear", 1.3) + 3
    if isBear and volRatio > 2.5:
        pat_bear += 12
    if isBull and volRatio > 2.0 and n > 5 and last["close"] > max(d["high"] for d in data[-5:]):
        pat_bull += 13
    if n >= 3:
        b0, b1, b2 = data[n-3], data[n-2], data[n-1]
        if (b0["close"]>b0["open"] and b1["close"]>b1["open"] and b2["close"]>b2["open"]
                and b1["close"]>b0["close"] and b2["close"]>b1["close"]):
            pat_bull += eff_pts("bull", 1.0) + 5
        if (b0["close"]<b0["open"] and b1["close"]<b1["open"] and b2["close"]<b2["open"]
                and b1["close"]<b0["close"] and b2["close"]<b1["close"]):
            pat_bear += eff_pts("bear", 1.0) + 5
        if (b0["close"]<b0["open"] and abs(b1["close"]-b1["open"]) < (b1["high"]-b1["low"])*0.3
                and b2["close"]>b2["open"] and b2["close"] >= (b0["open"]+b0["close"])/2):
            pat_bull += eff_pts("bull", 1.2) + 5

    day_range = last["high"] - last["low"] or 0.01
    close_pos = (last["close"] - last["low"]) / day_range
    if close_pos >= 0.8: extra_bull += 5
    elif close_pos >= 0.6: extra_bull += 3
    elif close_pos <= 0.2: extra_bear += 5
    elif close_pos <= 0.4: extra_bear += 3

    upper_ratio = upShadow / day_range if day_range > 0 else 0
    lower_ratio = downShadow / day_range if day_range > 0 else 0
    if upper_ratio > 0.35 and isBull: extra_bear += 3
    elif upper_ratio > 0.35: extra_bear += 5
    elif lower_ratio > 0.35 and isBull: extra_bull += 5
    elif lower_ratio > 0.35: extra_bull += 3
    elif upper_ratio < 0.1 and isBull: extra_bull += 4

    if week5 > week20: extra_bull += 6
    else: extra_bear += 6
    if n >= 60:
        month60 = sum(d["close"] for d in data[-60:]) / 60
        if last["close"] > month60: extra_bull += 5
        else: extra_bear += 5

    if n >= 6:
        pv = [d["volume"] for d in data[-6:-1]]
        p5a = sum(pv)/5; p3a = sum(pv[-3:])/3
        if p3a < p5a * 0.85 and volRatio > 1.4:
            if isBull: extra_bull += 12
            else: extra_bear += 8

    bull_pts = (ma_bull * w["ma"] + rsi_bull * w["rsi"] + kd_bull * w["kd"]
                + macd_bull * w["macd"] + vol_bull * w["vol"] + pat_bull * w["pattern"]
                + extra_bull)
    bear_pts = (ma_bear * w["ma"] + rsi_bear * w["rsi"] + kd_bear * w["kd"]
                + macd_bear * w["macd"] + vol_bear * w["vol"] + pat_bear * w["pattern"]
                + extra_bear)

    bonus = 0
    if auto_strat == "breakout":
        bonus = 8 if isBull else 0
    elif auto_strat == "pullback" and n >= 25:
        ma20_v = lma20 or 0
        ma60_v = lma60_as
        biasMA20 = (last["close"] - ma20_v) / ma20_v * 100 if ma20_v else 0
        biasMA60 = (last["close"] - ma60_v) / ma60_v * 100 if ma60_v else None
        recent_lows = [d["low"] for d in data[-8:]]
        touchedMA20 = any(abs(lo - ma20_v)/ma20_v < 0.03 for lo in recent_lows) if ma20_v else False
        touchedMA60 = any(abs(lo - ma60_v)/ma60_v < 0.04 for lo in recent_lows) if ma60_v else False
        if biasMA20 >= 0 and biasMA20 < 8 and touchedMA20:
            bonus += 18 if biasMA20 < 3 else 10
        if ma60_v and biasMA60 is not None and 0 <= biasMA60 < 10 and touchedMA60:
            bonus += 20 if biasMA60 < 4 else 12
        vol20a = sum(d["volume"] for d in data[-20:]) / 20
        vol5a  = sum(d["volume"] for d in data[-5:]) / 5
        if vol5a < vol20a * 0.85: bonus += 10
        today_ratio = last["volume"] / vol20a if vol20a > 0 else 1
        if isBull and 0.7 <= today_ratio < 1.8: bonus += 12
        elif isBull and 1.8 <= today_ratio < 2.5: bonus += 6
        if n >= 25:
            ma20_5ago = sum(d["close"] for d in data[-25:-5]) / 20
            if ma20_v > ma20_5ago: bonus += 6
        bonus = min(bonus, 40)
    elif auto_strat == "reversal" and n >= 15:
        rsi_window = rsiA[-45:]
        rsi_vals = [v for v in rsi_window if v is not None]
        if len(rsi_vals) >= 3:
            lrsi_b, prsi_b, p2rsi_b = rsi_vals[-1], rsi_vals[-2], rsi_vals[-3]
            if lrsi_b < 25: bonus += 15
            elif lrsi_b < 35: bonus += 8
            was_low = min(prsi_b, p2rsi_b) < 38
            if was_low and lrsi_b > prsi_b: bonus += 18
            elif was_low and lrsi_b > p2rsi_b: bonus += 8
        vol20a = sum(d["volume"] for d in data[-20:]) / 20
        vol3a  = sum(d["volume"] for d in data[-4:-1]) / 3
        end_shrink = vol3a < vol20a * 0.75
        today_ratio = last["volume"] / vol20a if vol20a > 0 else 1
        if end_shrink and isBull and today_ratio > 1.2: bonus += 15
        elif isBull and today_ratio > 1.0: bonus += 6
        if day_range > 0 and downShadow / day_range > 0.35: bonus += 8
        bonus = min(bonus, 45)

    net = bull_pts - bear_pts + bonus
    score = round(50 + (net / 200) * 50)
    return max(0, min(100, score))


# ══════════════════════════════════════════════════════════════
# 資料抓取
# ══════════════════════════════════════════════════════════════

def fetch_ticker_data(ticker):
    base = dict(
        ticker=ticker, name=ticker,
        price=None, prev_close=None, change_pct=None,
        targetMean=None, upside_pct=None,
        recMean=None, recKey="N/A", analysts=None,
        volume_today=None, volume_avg20=None, volume_ratio=None,
        ma5=None, ma20=None, price_vs_ma20_pct=None,
        week52_high=None, week52_pct=None, rsi14=None,
        upgrades_7d=0, downgrades_7d=0, net_upgrade=0,
        kline_score=None, _hist_ohlcv=None,
        earnings_days=None, news_3d=0,
        ret5d=None, ma20_rising=None,
        entry_signal="", rsi_div=None,
        rs5d=None, patterns=[],
        composite=None,
    )
    try:
        t = yf.Ticker(ticker)
        info = t.info
        base["name"]       = info.get("shortName", ticker)
        base["price"]      = info.get("currentPrice") or info.get("regularMarketPrice")
        base["targetMean"] = info.get("targetMeanPrice")
        base["recMean"]    = info.get("recommendationMean")
        base["recKey"]     = info.get("recommendationKey", "N/A")
        base["analysts"]   = info.get("numberOfAnalystOpinions")

        if base["price"] and base["targetMean"] and base["price"] > 0:
            base["upside_pct"] = (base["targetMean"] - base["price"]) / base["price"] * 100

        hist = t.history(period="1y")
        # 移除末尾 Close=nan 的不完整當日 bar（盤中執行或 yfinance 插入預告行時會出現）
        if hist is not None and not hist.empty:
            hist = hist[hist["Close"].notna()]
        if hist is not None and len(hist) >= 20:
            closes  = hist["Close"]
            volumes = hist["Volume"]
            # 今日漲跌幅：(現價 - 前一日收盤) / 前一日收盤 * 100
            if len(closes) >= 2:
                base["prev_close"] = float(closes.iloc[-2])
                if base["prev_close"] and base["prev_close"] > 0:
                    cur = float(closes.iloc[-1])
                    base["change_pct"] = round((cur - base["prev_close"]) / base["prev_close"] * 100, 2)
            base["volume_today"] = int(volumes.iloc[-1])
            base["volume_avg20"] = int(volumes.iloc[-20:].mean())
            if base["volume_avg20"] > 0:
                base["volume_ratio"] = round(base["volume_today"] / base["volume_avg20"], 2)
            base["ma5"]  = round(float(closes.iloc[-5:].mean()), 2)
            base["ma20"] = round(float(closes.iloc[-20:].mean()), 2)
            if base["ma20"] and base["price"]:
                base["price_vs_ma20_pct"] = round((base["price"] - base["ma20"]) / base["ma20"] * 100, 1)
            wh = float(closes.iloc[-252:].max()) if len(closes) >= 252 else float(closes.max())
            base["week52_high"] = round(wh, 2)
            if base["price"]:
                base["week52_pct"] = round((base["price"] - wh) / wh * 100, 1)
            base["rsi14"] = calc_rsi(closes)
            if len(closes) >= 6:
                base["ret5d"] = round((float(closes.iloc[-1]) / float(closes.iloc[-6]) - 1) * 100, 2)
            if len(closes) >= 25:
                ma20_now  = float(closes.iloc[-20:].mean())
                ma20_5ago = float(closes.iloc[-25:-5].mean())
                base["ma20_rising"] = ma20_now > ma20_5ago
            base["_hist_ohlcv"] = [
                {"open": float(row.Open), "high": float(row.High), "low": float(row.Low),
                 "close": float(row.Close), "volume": float(row.Volume)}
                for _, row in hist.iterrows()
            ]
            if base["_hist_ohlcv"]:
                last_bar = base["_hist_ohlcv"][-1]
                base["_is_bull"] = last_bar["close"] > last_bar["open"]

        try:
            cal = t.calendar
            if cal is not None:
                ed_list = None
                if isinstance(cal, dict) and "Earnings Date" in cal:
                    ed_list = cal["Earnings Date"]
                elif hasattr(cal, "columns") and "Earnings Date" in cal.columns:
                    ed_list = list(cal["Earnings Date"].values)
                if ed_list is not None:
                    for ed in (ed_list if hasattr(ed_list, "__iter__") and not isinstance(ed_list, str) else [ed_list]):
                        try:
                            ed_date = pd.Timestamp(ed).date()
                            base["earnings_days"] = (ed_date - datetime.now().date()).days
                            break
                        except Exception:
                            pass
        except Exception:
            pass

        try:
            news = t.news
            if news:
                cutoff_ts = time.time() - 3 * 86400
                base["news_3d"] = sum(1 for n in news if n.get("providerPublishTime", 0) > cutoff_ts)
        except Exception:
            pass

        try:
            upgrades_df = t.upgrades_downgrades
            if upgrades_df is not None and not upgrades_df.empty:
                cutoff = datetime.now() - timedelta(days=7)
                idx = pd.to_datetime(upgrades_df.index)
                recent = upgrades_df[idx >= cutoff]
                if "Action" in recent.columns:
                    actions = recent["Action"].str.lower()
                    base["upgrades_7d"]   = int(actions.str.contains("up|rais|init|start").sum())
                    base["downgrades_7d"] = int(actions.str.contains("down|lower|cut").sum())
                base["net_upgrade"] = base["upgrades_7d"] - base["downgrades_7d"]
        except Exception:
            pass
    except Exception:
        pass
    return base


# ══════════════════════════════════════════════════════════════
# 綜合評分 v3
# ══════════════════════════════════════════════════════════════

def calc_composite(r):
    score = 0.0
    rec = r.get("recMean")
    if rec is not None:
        rec_score = max(0, (3.0 - rec) / 1.5) * 25
        score += min(rec_score, 25)
    up = r.get("upside_pct")
    if up is not None:
        up_score = min(max(up, 0) / 30.0, 1.0) * 25
        score += up_score
    rsi = r.get("rsi14")
    if rsi is not None:
        if rsi <= 30:   score += 15
        elif rsi <= 40: score += 13
        elif rsi <= 55: score += 10
        elif rsi <= 65: score +=  5
        else:           score +=  0
    net = r.get("net_upgrade", 0) or 0
    if net >= 3:    score += 10
    elif net == 2:  score +=  8
    elif net == 1:  score +=  5
    elif net == -1: score -=  2
    elif net <= -2: score -=  4
    vr = r.get("volume_ratio")
    is_bull = r.get("_is_bull")
    if vr is not None:
        if vr >= 1.5:
            if is_bull:
                score += min((vr / 3.0), 1.0) * 15
            else:
                score -= 3
    w52 = r.get("week52_pct")
    if w52 is not None:
        if -20 <= w52 <= -3:   score += 10
        elif -25 <= w52 < -20: score +=  7
        elif w52 > -3:         score +=  5
    return round(min(max(score, 0), 100), 1)


def fetch_spy_data():
    try:
        spy = yf.Ticker("SPY")
        h = spy.history(period="3mo")
        if h is None or h.empty:
            return None
        # 移除末尾 Close=nan 的不完整當日 bar（盤中執行時 yfinance 會插入）
        h = h[h["Close"].notna()]
        if len(h) < 22:
            return None
        closes = h["Close"]
        ret5d  = round((float(closes.iloc[-1]) / float(closes.iloc[-6]) - 1) * 100, 2)
        rsi    = calc_rsi(closes)
        ma20   = float(closes.iloc[-20:].mean())
        price  = float(closes.iloc[-1])
        return {"ret5d": ret5d, "rsi": rsi, "price": price,
                "below_ma20": price < ma20, "ma20": round(ma20, 2)}
    except Exception:
        return None


def calc_entry_signal(ohlcv):
    n = len(ohlcv)
    if n < 10:
        return ""
    last = ohlcv[-1]
    avg20 = sum(d["volume"] for d in ohlcv[-20:]) / min(20, n)
    if avg20 == 0:
        return ""
    vol_ratio = last["volume"] / avg20
    is_bull   = last["close"] > last["open"]
    day_range = (last["high"] - last["low"]) or 0.01
    close_pos = (last["close"] - last["low"]) / day_range
    if is_bull and vol_ratio >= 2.0 and n >= 6:
        prev5_high = max(d["high"] for d in ohlcv[-6:-1])
        if last["close"] > prev5_high:
            return "💥突破放量"
    if is_bull and vol_ratio >= 1.5 and close_pos >= 0.7:
        return "🚀主力進場"
    if is_bull and vol_ratio >= 1.3 and n >= 6:
        prev3_shrink = sum(1 for d in ohlcv[-4:-1] if d["volume"] < avg20 * 0.85)
        if prev3_shrink >= 2:
            return "✅洗盤結束"
    if vol_ratio < 0.6:
        return "📉量縮整理"
    return ""


def detect_ht_patterns(r):
    out = []
    if r.get("upgrades_7d", 0) >= 1 and (r.get("volume_ratio") or 0) >= 1.5:
        out.append(("A升評爆量", "pat-a"))
    w52 = r.get("week52_pct")
    rsi = r.get("rsi14")
    if (w52 is not None and -25 <= w52 <= -8
            and rsi is not None and 32 <= rsi <= 55
            and r.get("ma20_rising") is True):
        out.append(("B回檔承接", "pat-b"))
    if r.get("rsi_div") == "bull":
        out.append(("C底背離", "pat-c"))
    return out


SORT_MODES = {
    "composite": ("composite",    False, "綜合評分"),
    "analyst":   ("recMean",      True,  "分析師評分強度"),
    "upside":    ("upside_pct",   False, "目標價上漲空間"),
    "volume":    ("volume_ratio", False, "爆量倍數"),
    "upgrade":   ("net_upgrade",  False, "近7天升評淨次數"),
    "rsi":       ("rsi14",        True,  "RSI 超賣程度"),
    "kline":     ("kline_score",  False, "K線技術評分"),
}

# ══════════════════════════════════════════════════════════════
# 資料庫統計（stats_db.json）
# ══════════════════════════════════════════════════════════════

DB_PATH = "docs/stats_db.json"

# 入庫條件
DB_KLINE_MIN = 72
DB_COMP_MIN  = 70

def load_db():
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"signals": []}


def save_db(db):
    os.makedirs("docs", exist_ok=True)
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False)


def update_db(results, today_str):
    """
    將今日符合條件（K線≥72 OR 綜合≥70）的訊號寫入資料庫
    同一天同一股只記一次（去重）
    """
    db = load_db()
    existing_keys = {(s["date"], s["ticker"]) for s in db["signals"]}
    added = 0
    for r in results:
        kl = r.get("kline_score") or 0
        cp = r.get("composite") or 0
        if kl < DB_KLINE_MIN and cp < DB_COMP_MIN:
            continue
        key = (today_str, r["ticker"])
        if key in existing_keys:
            continue
        existing_keys.add(key)
        entry = {
            "date":        today_str,
            "ticker":      r["ticker"],
            "name":        r.get("name", r["ticker"]),
            "kline":       kl,
            "composite":   cp,
            "price":       r.get("price"),
            "entry_signal": r.get("entry_signal", ""),
            "patterns":    [p[0] for p in r.get("patterns", [])],
            "rsi14":       r.get("rsi14"),
            "volume_ratio": r.get("volume_ratio"),
            "upside_pct":  r.get("upside_pct"),
            "week52_pct":  r.get("week52_pct"),
            "net_upgrade": r.get("net_upgrade", 0),
            # T+1/T+3/T+5 後填（此時先留 null）
            "t1": None, "t3": None, "t5": None, "t7": None, "t10": None,
        }
        db["signals"].append(entry)
        added += 1

    # ── 嘗試回填歷史訊號的 T+N 報酬 ──
    # 找出還有 null T 值且 date != today 的訊號，用當前 results 填
    price_map = {r["ticker"]: r.get("price") for r in results}
    today_dt = datetime.strptime(today_str, "%Y-%m-%d")
    for sig in db["signals"]:
        if sig["date"] == today_str:
            continue
        if all(sig[k] is not None for k in ["t1","t3","t5","t7","t10"]):
            continue
        sig_dt = datetime.strptime(sig["date"], "%Y-%m-%d")
        days_passed = (today_dt - sig_dt).days
        cur_price = price_map.get(sig["ticker"])
        entry_price = sig.get("price")
        if cur_price and entry_price and entry_price > 0:
            pct = round((cur_price - entry_price) / entry_price * 100, 2)
            if days_passed >= 1 and sig["t1"] is None:  sig["t1"] = pct
            if days_passed >= 3 and sig["t3"] is None:  sig["t3"] = pct
            if days_passed >= 5 and sig["t5"] is None:  sig["t5"] = pct
            if days_passed >= 7 and sig["t7"] is None:  sig["t7"] = pct
            if days_passed >= 10 and sig["t10"] is None: sig["t10"] = pct

    save_db(db)
    print(f"  📊 資料庫：今日新增 {added} 筆訊號，累計 {len(db['signals'])} 筆")
    return db


# ══════════════════════════════════════════════════════════════
# HTML 產生
# ══════════════════════════════════════════════════════════════

def generate_html(rows, sort_key, ascending, index_name, generated_at, market_info=None, db=None):
    sorted_rows = sorted(rows, key=lambda x: (
        x.get(sort_key) is None,
        x.get(sort_key) if ascending else -(x.get(sort_key) or 0)
    ))

    def badge(label, cls):
        return f'<span class="badge {cls}">{label}</span>'

    def rec_badge(v):
        if v is None: return badge("無資料", "badge-hold")
        if v < 1.5:  return badge(f"強力買進 {v:.2f}", "badge-sb")
        if v < 2.5:  return badge(f"買進 {v:.2f}", "badge-buy")
        if v < 3.5:  return badge(f"持有 {v:.2f}", "badge-hold")
        if v < 4.5:  return badge(f"表現落後 {v:.2f}", "badge-under")
        return badge(f"賣出 {v:.2f}", "badge-sell")

    def change_cell(v):
        """今日漲跌幅：綠漲紅跌（美股慣例）"""
        if v is None: return '<td class="na">N/A</td>'
        cls = "chg-up" if v > 0 else "chg-dn" if v < 0 else "neu"
        sign = "+" if v > 0 else ""
        return f'<td class="{cls}">{sign}{v:.2f}%</td>'

    def upside_cell(v):
        if v is None: return '<td class="na">N/A</td>'
        cls = "pos-strong" if v >= 20 else "pos" if v >= 10 else "neutral" if v >= 0 else "neg"
        return f'<td class="{cls}">{v:+.1f}%</td>'

    def upgrade_cell(up, dn):
        net = up - dn
        cls = "pos-strong" if net >= 2 else "pos" if net >= 1 else "neg" if net < 0 else "neutral"
        arr = "▲" if net > 0 else "▼" if net < 0 else "—"
        return f'<td class="{cls}">{arr}{up}/{dn}</td>'

    def vol_cell(v):
        if v is None: return '<td class="na">N/A</td>'
        cls = "pos-strong" if v >= 3 else "pos" if v >= 2 else "neutral" if v >= 1.5 else ""
        return f'<td class="{cls}">{v:.2f}x</td>'

    def rsi_cell(v):
        if v is None: return '<td class="na">N/A</td>'
        cls = "neg" if v >= 70 else "neutral" if v >= 60 else "pos-strong" if v <= 30 else "pos" if v <= 40 else ""
        return f'<td class="{cls}">{v:.1f}</td>'

    def pct_cell(v, good_positive=True):
        if v is None: return '<td class="na">N/A</td>'
        cls = ("pos" if v > 0 else "neg") if good_positive else ("neg" if v > 0 else "pos")
        return f'<td class="{cls}">{v:+.1f}%</td>'

    def score_cell(v):
        if v is None: return '<td class="na">N/A</td>'
        cls = "pos-strong" if v >= 70 else "pos" if v >= 50 else "neutral" if v >= 30 else "neg"
        bar = int(v)
        return f'<td class="{cls} score-cell"><span class="score-num">{v:.1f}</span><div class="score-bar"><div class="score-fill" style="width:{bar}%"></div></div></td>'

    def kline_score_cell(v, ticker=""):
        if v is None: return '<td class="na">N/A</td>'
        if v >= 78:   cls, tag = "pos-strong", "🔥"
        elif v >= 62: cls, tag = "pos",        "📈"
        elif v >= 45: cls, tag = "neutral",    "⚖️"
        elif v >= 30: cls, tag = "neg",        "⚠️"
        else:         cls, tag = "neg",        "🔻"
        bar = int(v)
        kline_url = f"https://flydav003-alt.github.io/k-line/?stock={ticker}"
        link = f'<a href="{kline_url}" target="_blank" style="text-decoration:none;color:inherit;display:inline-flex;align-items:center;gap:2px">{tag}<span class="score-num">{v}</span></a>'
        return f'<td class="{cls} score-cell">{link}<div class="score-bar"><div class="score-fill" style="width:{bar}%"></div></div></td>'

    def entry_signal_cell(v):
        if not v: return '<td class="na">—</td>'
        if "突破" in v:   css = "sig-breakthrough"
        elif "主力" in v: css = "sig-main"
        elif "洗盤" in v: css = "sig-washout"
        elif "量縮" in v: css = "sig-shrink"
        else:              css = ""
        return f'<td class="{css}">{v}</td>'

    def rs5d_cell(v):
        if v is None: return '<td class="na">N/A</td>'
        css = "rs-strong" if v >= 3 else "rs-pos" if v >= 0 else "rs-neg"
        arrow = "▲" if v > 0 else "▼"
        return f'<td class="{css}">{arrow}{abs(v):.1f}%</td>'

    def patterns_cell(pats):
        if not pats: return '<td class="na">—</td>'
        badges = "".join(f'<span class="pat {c}">{l}</span>' for l, c in pats)
        return f'<td style="white-space:normal;padding:4px 6px"><div style="display:flex;flex-direction:column;align-items:center;gap:3px">{badges}</div></td>'

    def earnings_cell(days):
        if days is None: return '<td class="na">N/A</td>'
        if 0 <= days <= 3:   css, note = "earnings-warn", "⚠️"
        elif -5 <= days < 0: css, note = "earnings-near", "剛公布"
        elif days <= 14:     css, note = "earnings-near", ""
        else:                css, note = "earnings-ok",  ""
        label = f"{note}{days}天" if days >= 0 else f"{note}{abs(days)}天前"
        return f'<td class="{css}">{label}</td>'

    rows_html = ""
    # 欄位順序：代號 現價 漲跌 目標價% 評分/方向 K線分 綜合分 升降評 爆量倍數 RSI-14 距MA20 距52W高 RS(5日) 今日訊號 型態 財報距離 分析師數
    for r in sorted_rows:
        kl_url = f"https://finance.yahoo.com/quote/{r['ticker']}"
        rows_html += f"""
        <tr>
          <td class="ticker"><a href="{kl_url}" target="_blank">{r['ticker']}</a></td>
          <td>${fmt(r['price'], 2, na='N/A')}</td>
          {change_cell(r.get('change_pct'))}
          {upside_cell(r.get('upside_pct'))}
          <td>{rec_badge(r.get('recMean'))}</td>
          {kline_score_cell(r.get('kline_score'), r['ticker'])}
          {score_cell(r.get('composite'))}
          {upgrade_cell(r['upgrades_7d'], r['downgrades_7d'])}
          {vol_cell(r.get('volume_ratio'))}
          {rsi_cell(r.get('rsi14'))}
          {pct_cell(r.get('price_vs_ma20_pct'), good_positive=True)}
          {pct_cell(r.get('week52_pct'), good_positive=False)}
          {rs5d_cell(r.get('rs5d'))}
          {entry_signal_cell(r.get('entry_signal', ''))}
          {patterns_cell(r.get('patterns', []))}
          {earnings_cell(r.get('earnings_days'))}
          <td class="analysts">{int(r['analysts']) if r.get('analysts') else 'N/A'}</td>
        </tr>"""

    total     = len(sorted_rows)
    sb_count  = sum(1 for r in sorted_rows if r.get("recMean") and r["recMean"] < 1.5)
    buy_count = sum(1 for r in sorted_rows if r.get("recMean") and 1.5 <= r["recMean"] < 2.5)
    vol_count = sum(1 for r in sorted_rows if r.get("volume_ratio") and r["volume_ratio"] >= 2)
    up_count  = sum(1 for r in sorted_rows if r.get("net_upgrade", 0) > 0)
    pat_count = sum(1 for r in sorted_rows if r.get("patterns"))
    sig_count = sum(1 for r in sorted_rows if r.get("entry_signal") and "📉" not in r["entry_signal"])
    earn_warn = sum(1 for r in sorted_rows if r.get("earnings_days") is not None and 0 <= r["earnings_days"] <= 3)
    db_today  = sum(1 for r in sorted_rows if (r.get("kline_score") or 0) >= DB_KLINE_MIN or (r.get("composite") or 0) >= DB_COMP_MIN)

    if market_info:
        spy_rsi  = market_info.get("rsi") or 0
        spy_below = market_info.get("below_ma20", False)
        spy_ret5  = market_info.get("ret5d") or 0
        if spy_below or spy_rsi > 75:
            mkt_cls, mkt_icon = "danger",  "🚨"
            mkt_msg = f"大盤警示：SPY {'跌破MA20' if spy_below else ''} {'RSI='+str(round(spy_rsi,0))+' 超買' if spy_rsi>75 else ''}，建議降低倉位或暫停進場"
        elif spy_rsi > 68 or spy_ret5 > 5:
            mkt_cls, mkt_icon = "caution", "⚠️"
            mkt_msg = f"大盤偏熱：SPY RSI={round(spy_rsi,0)}，近5日漲{spy_ret5:+.1f}%，個股勝率降低，嚴格篩選進場點"
        else:
            mkt_cls, mkt_icon = "ok",      "✅"
            mkt_msg = f"大盤健康：SPY RSI={round(spy_rsi,0)}，近5日{spy_ret5:+.1f}%，環境適合波段操作"
        market_banner = f'<div class="market-warn {mkt_cls}">{mkt_icon} {mkt_msg}</div>'
    else:
        market_banner = ""

    # ── 資料庫統計 Tab HTML ──
    db_html = _gen_stats_tab(db) if db else "<p style='padding:24px;color:#888'>尚無資料庫資料</p>"
    db_count = len(db["signals"]) if db else 0

    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>美股綜合 Screener v3 — {index_name}</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: -apple-system,"Segoe UI",Arial,sans-serif; background:#f0f2f5; color:#222; font-size:13px; }}
.header {{ background:#1a1a2e; color:#fff; padding:14px 24px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:8px; }}
.header h1 {{ font-size:18px; font-weight:700; }}
.header p {{ color:#aaa; font-size:11px; margin-top:2px; }}
/* ── Tabs ── */
.tabs {{ display:flex; background:#fff; border-bottom:2px solid #e0e0e0; padding:0 24px; }}
.tab-btn {{ padding:10px 20px; border:none; background:none; cursor:pointer; font-size:13px; font-weight:500; color:#666; border-bottom:2px solid transparent; margin-bottom:-2px; transition:all .15s; }}
.tab-btn.active {{ color:#1a1a2e; border-bottom-color:#1a56db; }}
.tab-btn:hover {{ color:#1a1a2e; }}
.tab-panel {{ display:none; }}
.tab-panel.active {{ display:block; }}
/* ── Summary ── */
.summary {{ display:flex; gap:10px; padding:12px 24px; background:#fff; border-bottom:1px solid #e0e0e0; flex-wrap:wrap; }}
.stat {{ background:#f7f8fa; border:1px solid #e0e0e0; border-radius:8px; padding:8px 14px; min-width:90px; text-align:center; }}
.stat .num {{ font-size:20px; font-weight:800; color:#1a1a2e; }}
.stat .lbl {{ font-size:10px; color:#888; margin-top:2px; }}
/* ── Controls ── */
.controls {{ padding:10px 24px; background:#fff; border-bottom:1px solid #eee; display:flex; gap:12px; align-items:center; flex-wrap:wrap; }}
.controls input[type=text] {{ padding:6px 12px; border:1px solid #ccc; border-radius:6px; font-size:12px; width:180px; }}
.slider-wrap {{ display:flex; align-items:center; gap:6px; font-size:12px; color:#555; }}
.slider-wrap input[type=range] {{ width:110px; accent-color:#1a56db; -webkit-appearance:none; appearance:none; margin:0; padding:0; cursor:pointer; height:6px; border-radius:3px; background:linear-gradient(to right,#1a56db 0%,#1a56db 0%,#d1d5db 0%,#d1d5db 100%); outline:none; }}
.slider-wrap input[type=range]::-webkit-slider-thumb {{ -webkit-appearance:none; width:16px; height:16px; border-radius:50%; background:#1a56db; cursor:pointer; border:2px solid #fff; box-shadow:0 1px 3px rgba(0,0,0,.25); }}
.slider-wrap input[type=range]::-moz-range-thumb {{ width:16px; height:16px; border-radius:50%; background:#1a56db; cursor:pointer; border:2px solid #fff; box-shadow:0 1px 3px rgba(0,0,0,.25); }}
.slider-wrap input[type=range]::-moz-range-track {{ height:6px; border-radius:3px; background:#d1d5db; }}
.slider-val {{ font-weight:600; color:#1a1a2e; min-width:26px; text-align:center; }}
/* ── Table ── */
.table-wrap {{ overflow-x:auto; padding:16px 24px; min-height:300px; }}
table {{ width:100%; border-collapse:collapse; background:#fff; border-radius:10px; overflow:hidden; box-shadow:0 1px 4px rgba(0,0,0,.08); }}
thead th {{ background:#1a1a2e; color:#fff; padding:9px 7px; text-align:center; font-size:11px; white-space:nowrap; cursor:pointer; user-select:none; }}
thead th:hover {{ background:#2d2d4e; }}
thead th::after {{ content:" ↕"; opacity:.4; font-size:10px; }}
tbody tr {{ border-bottom:1px solid #f0f0f0; }}
tbody tr:hover {{ background:#f5f8ff; }}
td {{ padding:7px 7px; text-align:center; white-space:nowrap; }}
td.ticker a {{ font-weight:700; color:#1a56db; text-decoration:none; }}
td.ticker a:hover {{ text-decoration:underline; }}
td.analysts {{ color:#888; font-size:11px; }}
.pos-strong {{ color:#166534; font-weight:700; }}
.pos         {{ color:#15803d; }}
.neutral     {{ color:#854d0e; }}
.neg         {{ color:#be123c; }}
.na          {{ color:#aaa; }}
/* 漲跌：綠漲紅跌（美股慣例）*/
.chg-up {{ color:#16a34a; font-weight:600; }}
.chg-dn {{ color:#dc2626; font-weight:600; }}
.neu {{ color:#888; }}
.badge {{ display:inline-block; padding:2px 7px; border-radius:10px; font-size:10px; font-weight:600; }}
.badge-sb    {{ background:#dcfce7; color:#14532d; }}
.badge-buy   {{ background:#d1fae5; color:#065f46; }}
.badge-hold  {{ background:#fef9c3; color:#713f12; }}
.badge-under {{ background:#fee2e2; color:#7f1d1d; }}
.badge-sell  {{ background:#fca5a5; color:#450a0a; }}
.score-cell  {{ min-width:56px; }}
.score-num   {{ font-weight:700; font-size:13px; }}
.score-bar   {{ height:3px; background:#e5e7eb; border-radius:2px; margin-top:3px; max-width:44px; }}
.score-fill  {{ height:100%; background:linear-gradient(90deg,#3b82f6,#22c55e); border-radius:2px; }}
.hidden {{ display:none; }}
.pat {{ display:inline-block; padding:2px 6px; border-radius:8px; font-size:10px; font-weight:600; margin:1px; white-space:nowrap; }}
.pat-a {{ background:#fef3c7; color:#92400e; }}
.pat-b {{ background:#dbeafe; color:#1e40af; }}
.pat-c {{ background:#f0fdf4; color:#166534; }}
.sig-breakthrough {{ color:#dc2626; font-weight:700; }}
.sig-main        {{ color:#16a34a; font-weight:700; }}
.sig-washout     {{ color:#2563eb; font-weight:600; }}
.sig-shrink      {{ color:#9ca3af; }}
.rs-strong {{ color:#166534; font-weight:700; }}
.rs-pos    {{ color:#15803d; }}
.rs-neg    {{ color:#be123c; }}
.earnings-warn {{ color:#dc2626; font-weight:700; }}
.earnings-near {{ color:#d97706; font-weight:600; }}
.earnings-ok   {{ color:#6b7280; }}
.market-warn {{ margin:0 24px 10px; padding:10px 18px; border-radius:8px; font-size:12px; font-weight:600; }}
.market-warn.danger  {{ background:#fee2e2; border-left:4px solid #dc2626; color:#7f1d1d; }}
.market-warn.caution {{ background:#fef9c3; border-left:4px solid #d97706; color:#78350f; }}
.market-warn.ok      {{ background:#dcfce7; border-left:4px solid #16a34a; color:#14532d; }}
/* ── Stats Tab ── */
.stats-wrap {{ padding:16px 24px; min-height:400px; }}
.stats-grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:1px; background:#e0e0e0; margin-bottom:16px; border-radius:8px; overflow:hidden; }}
.stats-card {{ background:#fff; padding:14px 16px; }}
.stats-card .sk {{ font-size:11px; color:#888; margin-bottom:4px; }}
.stats-card .sv {{ font-size:22px; font-weight:600; }}
.sec-title {{ font-size:13px; font-weight:600; margin:16px 0 8px; color:#1a1a2e; }}
.db-tools {{ display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin-bottom:8px; }}
.db-tools input {{ background:#fff; border:1px solid #ccc; border-radius:6px; padding:5px 10px; font-size:12px; outline:none; width:140px; }}
.db-tools label {{ display:flex; align-items:center; gap:4px; color:#555; font-size:12px; }}
.db-cnt {{ color:#888; font-size:12px; }}
.db-cnt b {{ color:#1a1a2e; }}
.stbl {{ width:100%; border-collapse:collapse; background:#fff; border-radius:8px; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,.06); }}
.stbl th,.stbl td {{ padding:8px 10px; border-bottom:1px solid #f0f0f0; font-size:12px; white-space:nowrap; text-align:center; }}
.stbl th {{ background:#f7f8fa; color:#555; font-weight:600; cursor:pointer; user-select:none; }}
.stbl th:hover {{ background:#eee; }}
.stbl th::after {{ content:" ↕"; opacity:.4; font-size:10px; }}
.stbl td:first-child {{ text-align:left; }}
.kbdg {{ display:inline-block; padding:2px 7px; border-radius:4px; font-size:11px; font-weight:600; }}
.kbdg-hi {{ background:rgba(220,38,38,.12); color:#dc2626; border:.5px solid rgba(220,38,38,.3); }}
.kbdg-md {{ background:rgba(234,88,12,.12); color:#ea580c; border:.5px solid rgba(234,88,12,.3); }}
.kbdg-lo {{ background:#f1f5f9; color:#64748b; border:.5px solid #e2e8f0; }}
.cbdg {{ display:inline-block; padding:2px 7px; border-radius:4px; font-size:11px; font-weight:600; }}
.cbdg-hi {{ background:rgba(22,163,74,.12); color:#16a34a; border:.5px solid rgba(22,163,74,.25); }}
.cbdg-md {{ background:rgba(202,138,4,.12); color:#ca8a04; border:.5px solid rgba(202,138,4,.25); }}
.cbdg-lo {{ background:#f1f5f9; color:#64748b; border:.5px solid #e2e8f0; }}
.t-pos {{ color:#16a34a; font-weight:500; }}
.t-neg {{ color:#dc2626; font-weight:500; }}
.t-pen {{ color:#9ca3af; font-style:italic; }}
.status-bdg {{ display:inline-block; padding:2px 7px; border-radius:4px; font-size:10px; font-weight:500; }}
.st-done {{ background:rgba(22,163,74,.12); color:#16a34a; border:.5px solid rgba(22,163,74,.25); }}
.st-part {{ background:rgba(234,88,12,.12); color:#ea580c; border:.5px solid rgba(234,88,12,.3); }}
.st-open {{ background:#f1f5f9; color:#64748b; border:.5px solid #e2e8f0; }}
</style>
</head>
<body>

<div class="header">
  <div>
    <h1>📊 美股綜合 Screener v3 — {index_name}</h1>
    <p>產生：{generated_at}　資料：Yahoo Finance　共 {total} 檔</p>
  </div>
</div>

<div class="tabs">
  <button class="tab-btn active" onclick="switchTab('screener',this)">📈 選股結果</button>
  <button class="tab-btn" onclick="switchTab('stats',this)">📊 資料庫統計 <span style="background:#1a56db;color:#fff;border-radius:10px;padding:1px 6px;font-size:10px;margin-left:4px">{db_count}</span></button>
</div>

<!-- ═══ Tab 1: 選股結果 ═══ -->
<div id="tab-screener" class="tab-panel active">

{market_banner}

<div class="summary">
  <div class="stat"><div class="num">{total}</div><div class="lbl">總檔數</div></div>
  <div class="stat"><div class="num" style="color:#14532d">{sb_count}</div><div class="lbl">強力買進</div></div>
  <div class="stat"><div class="num" style="color:#065f46">{buy_count}</div><div class="lbl">買進</div></div>
  <div class="stat"><div class="num" style="color:#1a56db">{vol_count}</div><div class="lbl">爆量(≥2x)</div></div>
  <div class="stat"><div class="num" style="color:#7c3aed">{up_count}</div><div class="lbl">近7天升評</div></div>
  <div class="stat"><div class="num" style="color:#d97706">{pat_count}</div><div class="lbl">高勝率型態</div></div>
  <div class="stat"><div class="num" style="color:#16a34a">{sig_count}</div><div class="lbl">今日訊號</div></div>
  <div class="stat"><div class="num" style="color:#dc2626">{earn_warn}</div><div class="lbl">財報前3天⚠</div></div>
  <div class="stat"><div class="num" style="color:#0891b2">{db_today}</div><div class="lbl">今日入庫</div></div>
</div>

<div class="controls">
  <label style="font-size:12px;color:#555">🔍 搜尋：</label>
  <input type="text" id="searchBox" placeholder="輸入代號篩選..." oninput="filterTable()">
  <div class="slider-wrap">
    K線分 ≥ <input type="range" id="sliderK" min="0" max="100" value="0" oninput="updateSlider('K');filterTable()">
    <span class="slider-val" id="valK">0</span>
  </div>
  <div class="slider-wrap">
    綜合分 ≥ <input type="range" id="sliderC" min="0" max="100" value="0" oninput="updateSlider('C');filterTable()">
    <span class="slider-val" id="valC">0</span>
  </div>
  <select id="selSig" onchange="filterTable()" style="padding:5px 8px;border:1px solid #ccc;border-radius:6px;font-size:12px;background:#fff;color:#333;cursor:pointer">
    <option value="">全部訊號</option>
    <option value="突破放量">💥突破放量</option>
    <option value="主力進場">🚀主力進場</option>
    <option value="洗盤結束">✅洗盤結束</option>
    <option value="量縮整理">📉量縮整理</option>
    <option value="__NONE__">（無訊號）</option>
  </select>
  <select id="selPat" onchange="filterTable()" style="padding:5px 8px;border:1px solid #ccc;border-radius:6px;font-size:12px;background:#fff;color:#333;cursor:pointer">
    <option value="">全部型態</option>
    <option value="A升評爆量">A升評爆量</option>
    <option value="B回檔承接">B回檔承接</option>
    <option value="C底背離">C底背離</option>
    <option value="__NONE__">（無型態）</option>
  </select>
</div>

<div class="table-wrap">
<table id="mainTable">
<thead>
<tr>
  <th onclick="sortTable(0)" title="點擊排序">代號</th>
  <th onclick="sortTable(1)" title="點擊排序">現價</th>
  <th onclick="sortTable(2)" title="(現價−前日收盤)/前日收盤×100，點擊排序">漲跌幅</th>
  <th onclick="sortTable(3)" title="分析師目標均價相對現價漲跌幅，點擊排序">目標價%</th>
  <th onclick="sortTable(4)" title="分析師共識評分，1=強力買進，點擊排序">評分/方向</th>
  <th onclick="sortTable(5)" title="K線技術評分，≥78分🔥勝率極高，點擊排序">K線分</th>
  <th onclick="sortTable(6)" title="綜合評分（分析師+目標價+RSI+爆量+升評+52W位置），點擊排序">綜合評分</th>
  <th onclick="sortTable(7)" title="近7天升評/降評次數，點擊排序">升降評</th>
  <th onclick="sortTable(8)" title="成交量÷20日均量，>2x爆量，點擊排序">爆量倍數</th>
  <th onclick="sortTable(9)" title="RSI-14，>70超買，<30超賣，點擊排序">RSI-14</th>
  <th onclick="sortTable(10)" title="現價距20日均線，點擊排序">距MA20</th>
  <th onclick="sortTable(11)" title="現價距52週高點，點擊排序">距52W高</th>
  <th onclick="sortTable(12)" title="個股5日報酬-SPY5日報酬，點擊排序">RS(5日)</th>
  <th onclick="sortTable(13)" title="今日K線進場訊號，點擊排序">今日訊號</th>
  <th onclick="sortTable(14)" title="高勝率型態，點擊排序">型態</th>
  <th onclick="sortTable(15)" title="距下次財報天數，0~3天⚠️，點擊排序">財報距離</th>
  <th onclick="sortTable(16)" title="分析師覆蓋人數，點擊排序">分析師數</th>
</tr>
</thead>
<tbody>
{rows_html}
</tbody>
</table>
</div>

</div><!-- /tab-screener -->

<!-- ═══ Tab 2: 資料庫統計 ═══ -->
<div id="tab-stats" class="tab-panel">
{db_html}
</div>

<script>
// ── Tab 切換 ──
function switchTab(id, btn) {{
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-'+id).classList.add('active');
  btn.classList.add('active');
}}

// ── Slider 更新（含動態填色）──
function updateSlider(t) {{
  const el = t==='K' ? document.getElementById('sliderK') : document.getElementById('sliderC');
  const valEl = t==='K' ? document.getElementById('valK') : document.getElementById('valC');
  if (!el) return;
  valEl.textContent = el.value;
  const pct = el.value + '%';
  el.style.background = 'linear-gradient(to right,#1a56db 0%,#1a56db '+pct+',#d1d5db '+pct+',#d1d5db 100%)';
}}

// ── 選股篩選 ──
function filterTable() {{
  const q    = document.getElementById('searchBox').value.toLowerCase();
  const minK = parseInt(document.getElementById('sliderK').value) || 0;
  const minC = parseInt(document.getElementById('sliderC').value) || 0;
  const selSig = document.getElementById('selSig').value;
  const selPat = document.getElementById('selPat').value;
  document.querySelectorAll('#mainTable tbody tr').forEach(tr => {{
    const ticker  = tr.cells[0].innerText.toLowerCase();
    const klineEl = tr.cells[5].querySelector('.score-num');
    const scoreEl = tr.cells[6].querySelector('.score-num');
    const kScore  = klineEl ? parseFloat(klineEl.innerText) : 0;
    const cScore  = scoreEl ? parseFloat(scoreEl.innerText) : 0;
    const sigText = tr.cells[13] ? tr.cells[13].innerText.trim() : '';
    const patText = tr.cells[14] ? tr.cells[14].innerText.trim() : '';
    let sigOk = true;
    if (selSig === '__NONE__') {{ sigOk = sigText === '' || sigText === '—'; }}
    else if (selSig) {{ sigOk = sigText.includes(selSig); }}
    let patOk = true;
    if (selPat === '__NONE__') {{ patOk = patText === '' || patText === '—'; }}
    else if (selPat) {{ patOk = patText.includes(selPat); }}
    const show = (!q || ticker.includes(q)) && kScore >= minK && cScore >= minC && sigOk && patOk;
    tr.classList.toggle('hidden', !show);
  }});
}}

// ── 欄位排序（通用）──
var _SIG_ORDER = {{'突破放量':4,'主力進場':3,'洗盤結束':2,'量縮整理':1}};
var _PAT_ORDER = {{'A升評爆量':3,'B回檔承接':2,'C底背離':1}};
var _ST_ORDER  = {{'matured':3,'partial':2,'open':1}};
function _sigPri(txt) {{ for (var k in _SIG_ORDER) {{ if (txt.indexOf(k)>=0) return _SIG_ORDER[k]; }} return 0; }}
function _patPri(txt) {{ var b=0; for (var k in _PAT_ORDER) {{ if (txt.indexOf(k)>=0 && _PAT_ORDER[k]>b) b=_PAT_ORDER[k]; }} return b; }}
function _stPri(txt)  {{ for (var k in _ST_ORDER)  {{ if (txt.indexOf(k)>=0) return _ST_ORDER[k];  }} return 0; }}

// sigCols/patCols/stCols: 指定哪幾個欄位用自訂排序
function makeSort(tableId, sigCols, patCols, stCols) {{
  sigCols = sigCols||[]; patCols = patCols||[]; stCols = stCols||[];
  let sortDir = {{}};
  return function(col) {{
    const tb = document.querySelector('#'+tableId+' tbody');
    if (!tb) return;
    const rows = Array.from(tb.querySelectorAll('tr'));
    sortDir[col] = !sortDir[col];
    rows.sort((a, b) => {{
      const ac = a.cells[col], bc = b.cells[col];
      if (!ac || !bc) return 0;
      if (sigCols.indexOf(col)>=0) {{
        const ap=_sigPri(ac.innerText), bp=_sigPri(bc.innerText);
        return sortDir[col] ? ap-bp : bp-ap;
      }}
      if (patCols.indexOf(col)>=0) {{
        const ap=_patPri(ac.innerText), bp=_patPri(bc.innerText);
        return sortDir[col] ? ap-bp : bp-ap;
      }}
      if (stCols.indexOf(col)>=0) {{
        const ap=_stPri(ac.innerText), bp=_stPri(bc.innerText);
        return sortDir[col] ? ap-bp : bp-ap;
      }}
      let av=ac.innerText.replace(/[^0-9.+-]/g,'');
      let bv=bc.innerText.replace(/[^0-9.+-]/g,'');
      av=parseFloat(av); bv=parseFloat(bv);
      if (isNaN(av)) av=sortDir[col]?Infinity:-Infinity;
      if (isNaN(bv)) bv=sortDir[col]?Infinity:-Infinity;
      return sortDir[col] ? av-bv : bv-av;
    }});
    rows.forEach(r => tb.appendChild(r));
  }};
}}
// 首頁：col13=今日訊號, col14=型態
var sortTable  = makeSort('mainTable', [13], [14], []);
// 統計資料庫：col3=訊號, col12=狀態
var sortDbTable = makeSort('dbRecentTable', [3], [], [12]);

// ── DB Slider 更新（含動態填色）──
function updateDbSlider(t) {{
  const el = t==='K' ? document.getElementById('dbFk') : document.getElementById('dbFc');
  const valEl = t==='K' ? document.getElementById('dbValK') : document.getElementById('dbValC');
  if (!el) return;
  valEl.textContent = el.value;
  const pct = el.value + '%';
  el.style.background = 'linear-gradient(to right,#1a56db 0%,#1a56db '+pct+',#d1d5db '+pct+',#d1d5db 100%)';
}}

// ── DB 篩選 ──
function filterDb() {{
  const q  = (document.getElementById('dbQ')?.value||'').toLowerCase();
  const fk = parseInt(document.getElementById('dbFk')?.value)||0;
  const fc = parseInt(document.getElementById('dbFc')?.value)||0;
  let cnt = 0;
  document.querySelectorAll('#dbRecentTable tbody tr').forEach(tr => {{
    const t = tr.cells[1]?.innerText.toLowerCase()||'';
    const k = parseFloat(tr.cells[4]?.innerText)||0;
    const c = parseFloat(tr.cells[5]?.innerText)||0;
    const show = (!q||t.includes(q)) && k>=fk && c>=fc;
    tr.classList.toggle('hidden', !show);
    if (show) cnt++;
  }});
  const el = document.getElementById('dbCnt');
  if (el) el.textContent = cnt;
}}
</script>
</body>
</html>"""
    return html


def _gen_stats_tab(db):
    """資料庫統計 Tab 的 HTML 內容"""
    signals = db.get("signals", [])
    n_total = len(signals)
    if n_total == 0:
        return '<div class="stats-wrap"><p style="color:#888;padding:24px">尚無歷史資料，等第一次跑完即可開始累積</p></div>'

    # ── 統計計算 ──
    dates = sorted({s["date"] for s in signals})
    n_days = len(dates)

    # T+5 勝率、平均報酬
    t5_vals = [s["t5"] for s in signals if s["t5"] is not None]
    t3_vals = [s["t3"] for s in signals if s["t3"] is not None]
    t10_vals= [s["t10"] for s in signals if s["t10"] is not None]
    t5_wr   = round(sum(1 for v in t5_vals if v > 0) / len(t5_vals) * 100, 1) if t5_vals else None
    t5_avg  = round(sum(t5_vals) / len(t5_vals), 2) if t5_vals else None
    t10_wr  = round(sum(1 for v in t10_vals if v > 0) / len(t10_vals) * 100, 1) if t10_vals else None

    def _pct_fmt(v):
        if v is None: return "—"
        sign = "+" if v >= 0 else ""
        return f"{sign}{v:.2f}%"

    def _wr_fmt(v):
        if v is None: return "—"
        return f"{v:.1f}%"

    # 門檻成果表
    def thresh_row(label, hold, vals):
        if not vals: return ""
        wr = round(sum(1 for v in vals if v > 0) / len(vals) * 100, 1)
        avg = round(sum(vals) / len(vals), 2)
        hi  = round(max(vals), 2)
        lo  = round(min(vals), 2)
        wr_cls = "t-pos" if wr >= 60 else "t-neg"
        avg_cls = "t-pos" if avg >= 0 else "t-neg"
        return f"""<tr>
          <td style="text-align:left">{label}</td><td>{hold}</td><td>{len(vals)}</td>
          <td class="{wr_cls}">{wr:.1f}%</td>
          <td class="{avg_cls}">{_pct_fmt(avg)}</td>
          <td>{_pct_fmt(hi)}</td>
          <td class="t-neg">{_pct_fmt(lo)}</td>
        </tr>"""

    def filter_sigs(kl_min=None, cp_min=None, etype=None):
        out = []
        for s in signals:
            if kl_min and (s.get("kline") or 0) < kl_min: continue
            if cp_min and (s.get("composite") or 0) < cp_min: continue
            if etype and s.get("entry_signal","") != etype: continue
            out.append(s)
        return out

    def get_t(sigs, col):
        return [s[col] for s in sigs if s.get(col) is not None]

    # 門檻成果行
    thresh_rows = (
        thresh_row("K線 ≥ 72", "T+5",  get_t(filter_sigs(kl_min=72), "t5")) +
        thresh_row("K線 ≥ 72", "T+10", get_t(filter_sigs(kl_min=72), "t10")) +
        thresh_row("K線 ≥ 78", "T+5",  get_t(filter_sigs(kl_min=78), "t5")) +
        thresh_row("K線 ≥ 78", "T+10", get_t(filter_sigs(kl_min=78), "t10")) +
        thresh_row("綜合 ≥ 70", "T+5",  get_t(filter_sigs(cp_min=70), "t5")) +
        thresh_row("綜合 ≥ 70", "T+10", get_t(filter_sigs(cp_min=70), "t10")) +
        thresh_row("K線 ≥ 72 且綜合 ≥ 70", "T+3",  get_t(filter_sigs(kl_min=72, cp_min=70), "t3")) +
        thresh_row("K線 ≥ 72 且綜合 ≥ 70", "T+5",  get_t(filter_sigs(kl_min=72, cp_min=70), "t5")) +
        thresh_row("K線 ≥ 72 且綜合 ≥ 70", "T+10", get_t(filter_sigs(kl_min=72, cp_min=70), "t10")) +
        thresh_row("K線 ≥ 78 且綜合 ≥ 70", "T+5",  get_t(filter_sigs(kl_min=78, cp_min=70), "t5"))
    )

    # 訊號型態 T+5
    sig_labels = {"💥突破放量":"突破放量","🚀主力進場":"主力進場","✅洗盤結束":"洗盤結束"}
    t5_by_sig = ""
    for raw, lbl in sig_labels.items():
        vals = get_t([s for s in signals if raw in (s.get("entry_signal",""))], "t5")
        if not vals: continue
        wr = round(sum(1 for v in vals if v > 0) / len(vals) * 100, 1)
        avg = round(sum(vals) / len(vals), 2)
        t5_by_sig += f"""<tr>
          <td style="text-align:left">{lbl}</td><td>{len(vals)}</td>
          <td class="{'t-pos' if wr>=60 else 't-neg'}">{wr:.1f}%</td>
          <td class="{'t-pos' if avg>=0 else 't-neg'}">{_pct_fmt(avg)}</td>
          <td>{_pct_fmt(max(vals))}</td>
          <td class="t-neg">{_pct_fmt(min(vals))}</td>
        </tr>"""

    # 近期訊號表
    recent_rows = ""
    for s in sorted(signals, key=lambda x: x["date"], reverse=True):
        kl = s.get("kline") or 0
        cp = s.get("composite") or 0
        kbdg = "kbdg-hi" if kl >= 78 else "kbdg-md" if kl >= 72 else "kbdg-lo"
        cbdg = "cbdg-hi" if cp >= 80 else "cbdg-md" if cp >= 70 else "cbdg-lo"

        def tp(v, col):
            if v is None: return '<span class="t-pen">pending</span>'
            c = "t-pos" if v >= 0 else "t-neg"
            return f'<span class="{c}">{_pct_fmt(v)}</span>'

        status = "st-done" if s.get("t5") is not None else ("st-part" if s.get("t3") is not None else "st-open")
        status_txt = "matured" if s.get("t5") is not None else ("partial" if s.get("t3") is not None else "open")
        pats = ", ".join(s.get("patterns", [])) or "—"
        recent_rows += f"""<tr>
          <td>{s['date']}</td>
          <td style="color:#6366f1;font-weight:600">{s['ticker']}</td>
          <td>{s.get('name',s['ticker'])}</td>
          <td>{s.get('entry_signal','') or '—'}</td>
          <td><span class="kbdg {kbdg}">{kl}</span></td>
          <td><span class="cbdg {cbdg}">{cp}</span></td>
          <td>{s.get('price') or '—'}</td>
          <td>{tp(s.get('t1'),'t1')}</td>
          <td>{tp(s.get('t3'),'t3')}</td>
          <td>{tp(s.get('t5'),'t5')}</td>
          <td>{tp(s.get('t7'),'t7')}</td>
          <td>{tp(s.get('t10'),'t10')}</td>
          <td><span class="status-bdg {status}">{status_txt}</span></td>
        </tr>"""

    return f"""
<div class="stats-wrap">
  <div class="stats-grid">
    <div class="stats-card"><div class="sk">訊號總筆數</div><div class="sv">{n_total}</div></div>
    <div class="stats-card"><div class="sk">交易日數</div><div class="sv">{n_days}</div></div>
    <div class="stats-card"><div class="sk">T+5 勝率</div><div class="sv" style="color:{'#16a34a' if t5_wr and t5_wr>=60 else '#dc2626' if t5_wr else '#888'}">{_wr_fmt(t5_wr)}</div></div>
    <div class="stats-card"><div class="sk">T+5 平均報酬</div><div class="sv" style="color:{'#16a34a' if t5_avg and t5_avg>=0 else '#dc2626' if t5_avg else '#888'}">{_pct_fmt(t5_avg)}</div></div>
  </div>

  <div class="sec-title">門檻成果表：勝率 / 平均報酬 / 最高 / 最低</div>
  <div style="overflow-x:auto;margin-bottom:16px">
  <table class="stbl">
    <thead><tr>
      <th>條件</th><th>持有</th><th>樣本</th>
      <th onclick="sortStbl(0,3)">勝率 ↕</th>
      <th onclick="sortStbl(0,4)">平均報酬 ↕</th>
      <th onclick="sortStbl(0,5)">最高 ↕</th>
      <th onclick="sortStbl(0,6)">最低 ↕</th>
    </tr></thead>
    <tbody id="threshTbody">{thresh_rows or '<tr><td colspan="7" style="padding:20px;color:#888;text-align:center">資料不足，T+5 尚未到期</td></tr>'}</tbody>
  </table>
  </div>

  <div class="sec-title">T+5 訊號型態摘要</div>
  <div style="overflow-x:auto;margin-bottom:16px">
  <table class="stbl">
    <thead><tr>
      <th>訊號型態</th><th>樣本</th>
      <th onclick="sortStbl(1,2)">勝率 ↕</th>
      <th onclick="sortStbl(1,3)">平均報酬 ↕</th>
      <th onclick="sortStbl(1,4)">最高 ↕</th>
      <th onclick="sortStbl(1,5)">最低 ↕</th>
    </tr></thead>
    <tbody id="sigTbody">{t5_by_sig or '<tr><td colspan="6" style="padding:20px;color:#888;text-align:center">資料不足</td></tr>'}</tbody>
  </table>
  </div>

  <div class="sec-title">近期訊號與 T+1 / T+3 / T+5 / T+7 / T+10</div>
  <div class="db-tools">
    <input type="text" id="dbQ" placeholder="代號 / 名稱" oninput="filterDb()">
    <div class="slider-wrap">K線 ≥ <input type="range" id="dbFk" min="0" max="100" value="0" oninput="updateDbSlider('K');filterDb()"><span class="slider-val" id="dbValK">0</span></div>
    <div class="slider-wrap">綜合 ≥ <input type="range" id="dbFc" min="0" max="100" value="0" oninput="updateDbSlider('C');filterDb()"><span class="slider-val" id="dbValC">0</span></div>
    <span class="db-cnt">顯示 <b id="dbCnt">{n_total}</b> 筆</span>
  </div>
  <div style="overflow-x:auto">
  <table class="stbl" id="dbRecentTable">
    <thead><tr>
      <th onclick="sortDbTable(0)">日期</th>
      <th onclick="sortDbTable(1)">代號</th>
      <th onclick="sortDbTable(2)">名稱</th>
      <th onclick="sortDbTable(3)">訊號</th>
      <th onclick="sortDbTable(4)">K線分</th>
      <th onclick="sortDbTable(5)">綜合分</th>
      <th onclick="sortDbTable(6)">買進收盤</th>
      <th onclick="sortDbTable(7)">T+1</th>
      <th onclick="sortDbTable(8)">T+3</th>
      <th onclick="sortDbTable(9)">T+5</th>
      <th onclick="sortDbTable(10)">T+7</th>
      <th onclick="sortDbTable(11)">T+10</th>
      <th onclick="sortDbTable(12)">狀態</th>
    </tr></thead>
    <tbody>{recent_rows}</tbody>
  </table>
  </div>
</div>

<script>
// 門檻表與訊號表的靜態排序
var _stblDirs = [{{}}, {{}}];
function sortStbl(tIdx, col) {{
  const ids = ['threshTbody','sigTbody'];
  const tb = document.getElementById(ids[tIdx]);
  if (!tb) return;
  const rows = Array.from(tb.querySelectorAll('tr'));
  _stblDirs[tIdx][col] = !_stblDirs[tIdx][col];
  rows.sort((a, b) => {{
    let av = parseFloat((a.cells[col]?.innerText||'').replace(/[^0-9.+-]/g,''));
    let bv = parseFloat((b.cells[col]?.innerText||'').replace(/[^0-9.+-]/g,''));
    if (isNaN(av)) av = _stblDirs[tIdx][col] ? Infinity : -Infinity;
    if (isNaN(bv)) bv = _stblDirs[tIdx][col] ? Infinity : -Infinity;
    return _stblDirs[tIdx][col] ? av-bv : bv-av;
  }});
  rows.forEach(r => tb.appendChild(r));
}}
</script>
"""


# ══════════════════════════════════════════════════════════════
# 主程式
# ══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="美股綜合 Screener v3 — GitHub Actions 版")
    parser.add_argument("index", nargs="?", default="CORE",
                        help="指數：CORE / SOX / SPX / NDX / ALL（預設 CORE）")
    parser.add_argument("-s", "--sort", default="composite",
                        choices=SORT_MODES.keys())
    parser.add_argument("--top", type=int, default=None)
    args = parser.parse_args()

    arg = args.index.upper()
    if arg not in INDEX_MAP:
        print(f"未知指數：{arg}")
        sys.exit(1)

    tickers_list, index_name = INDEX_MAP[arg]
    if arg == "CORE":
        tickers_list = build_core()
    elif arg == "ALL":
        seen, tickers_list = set(), []
        for t in SOX_TICKERS + SPX_TICKERS + NDX_TICKERS:
            if t not in seen:
                seen.add(t)
                tickers_list.append(t)

    sort_key, ascending, sort_desc = SORT_MODES[args.sort]
    print(f"\n{index_name} — 共 {len(tickers_list)} 檔，排序：{sort_desc}")

    print("  抓取 SPY 大盤資料...", end="")
    market_info = fetch_spy_data()
    if market_info:
        print(f" SPY ${market_info['price']:.0f} 近5日{market_info['ret5d']:+.1f}%")
    else:
        print(" 無法取得")

    results = []
    for i, ticker in enumerate(tickers_list, 1):
        sys.stdout.write(f"\r  [{i:03d}/{len(tickers_list)}] {ticker:<6}...")
        sys.stdout.flush()
        data = fetch_ticker_data(ticker)
        ohlcv = data.pop("_hist_ohlcv", None)
        if ohlcv and len(ohlcv) >= 20:
            data["kline_score"]  = calc_kline_score(ohlcv)
            data["entry_signal"] = calc_entry_signal(ohlcv)
            rsi_vals = []
            for j in range(1, len(ohlcv)):
                g_sum = sum(max(ohlcv[k]["close"] - ohlcv[k-1]["close"], 0) for k in range(max(1,j-13), j+1))
                l_sum = sum(max(ohlcv[k-1]["close"] - ohlcv[k]["close"], 0) for k in range(max(1,j-13), j+1))
                cnt = min(j, 14)
                if cnt < 14:
                    rsi_vals.append(None)
                elif l_sum == 0:
                    rsi_vals.append(100.0)
                else:
                    rsi_vals.append(100 - 100 / (1 + (g_sum/cnt) / (l_sum/cnt)))
            rsi_vals = [None] + rsi_vals
            data["rsi_div"] = _detect_rsi_divergence(ohlcv, rsi_vals)
        data["composite"] = calc_composite(data)
        spy_ret5d = market_info["ret5d"] if market_info else None
        if spy_ret5d is not None and data.get("ret5d") is not None:
            data["rs5d"] = round(data["ret5d"] - spy_ret5d, 1)
        data["patterns"] = detect_ht_patterns(data)
        results.append(data)
        time.sleep(0.4)

    print("\r  ✅ 抓取完成！                    ")

    valid = [r for r in results if r["recMean"] is not None or r["volume_ratio"] is not None]

    if args.top:
        display_rows = sorted(valid, key=lambda x: (
            x.get(sort_key) is None,
            x.get(sort_key) if ascending else -(x.get(sort_key) or 0)
        ))[:args.top]
    else:
        display_rows = valid

    # ── 更新資料庫 ──
    today_str = datetime.now().strftime("%Y-%m-%d")
    db = update_db(results, today_str)

    # ── 輸出 HTML ──
    os.makedirs("docs", exist_ok=True)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    html_content = generate_html(display_rows, sort_key, ascending, index_name, generated_at, market_info, db)
    out_path = "docs/index.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"  🌐 HTML → {out_path}")
    print(f"  📊 DB  → {DB_PATH}")
    print(f"  共 {len(valid)} 檔有效，{len(results)-len(valid)} 檔無資料\n")


if __name__ == "__main__":
    main()
