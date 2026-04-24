# stock_eval_app_topdown_v4.py
# 台股法人成本 / 均線 / 兩週漲幅評估工具 - 上下直覺操作美化版 v4
#
# 執行方式：
#   pip install streamlit yfinance pandas numpy openpyxl twstock
#   streamlit run stock_eval_app_topdown_v4.py

from __future__ import annotations

import html
import re
from io import BytesIO
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf


# -----------------------------
# Page config + CSS
# -----------------------------
st.set_page_config(
    page_title="台股評估工具",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
/* 主畫面 */
.block-container {
    padding-top: 2.6rem;
    padding-bottom: 2.4rem;
    max-width: 980px;
}

/* 頁首安全留白：避免在手機或瀏覽器縮放時上緣看起來被裁切 */
.top-safe-space {
    height: 12px;
}

/* 更乾淨的 Hero 卡片 */
.app-hero {
    position: relative;
    box-sizing: border-box;
    border-radius: 26px;
    padding: 22px 22px 20px 22px;
    margin: 0 0 18px 0;
    background:
        radial-gradient(circle at 0% 0%, rgba(46, 118, 255, 0.16), transparent 34%),
        linear-gradient(135deg, #f8fbff 0%, #eef7ff 45%, #f6fff8 100%);
    border: 1px solid rgba(80, 130, 220, 0.20);
    box-shadow: 0 10px 28px rgba(35, 80, 140, 0.10);
    overflow: visible;
}
.app-title-row {
    display: flex;
    align-items: center;
    gap: 12px;
    min-height: 46px;
    overflow: visible;
}
.app-icon {
    width: 38px;
    height: 38px;
    min-width: 38px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 13px;
    background: rgba(46, 118, 255, 0.13);
    box-shadow: inset 0 0 0 1px rgba(46, 118, 255, 0.14);
    font-size: 1.22rem;
    line-height: 1;
}
.app-title {
    font-size: 1.72rem;
    line-height: 1.65;
    font-weight: 850;
    letter-spacing: 0.2px;
    margin: 0;
    padding-top: 2px;
    color: #14213d;
    overflow: visible;
}
.app-subtitle {
    font-size: 0.95rem;
    line-height: 1.65;
    color: #667085;
    margin: 8px 0 0 50px;
}
.hero-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 13px 0 0 50px;
}
.hero-tag {
    display: inline-flex;
    align-items: center;
    border-radius: 999px;
    padding: 5px 10px;
    font-size: 0.78rem;
    font-weight: 700;
    color: #315276;
    background: rgba(255,255,255,0.68);
    border: 1px solid rgba(80, 130, 220, 0.16);
}
.soft-alert {
    border-radius: 16px;
    padding: 12px 14px;
    margin: 0 0 18px 0;
    background: rgba(33, 150, 243, 0.10);
    border: 1px solid rgba(33, 150, 243, 0.18);
    color: #155fa0;
    line-height: 1.55;
    font-size: 0.95rem;
}
.section-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 1.24rem;
    line-height: 1.4;
    font-weight: 850;
    margin: 18px 0 10px 0;
}
.section-hint {
    font-size: 0.88rem;
    color: #7a7f87;
    line-height: 1.55;
    margin: -2px 0 10px 0;
}

/* Streamlit 原生元件微調 */
.stButton > button {
    width: 100%;
    border-radius: 15px;
    min-height: 50px;
    font-size: 1.05rem;
    font-weight: 800;
}
div[data-testid="stVerticalBlock"] {
    gap: 0.75rem;
}
input, textarea {
    border-radius: 12px !important;
}
div[data-testid="stNumberInput"] button {
    border-radius: 10px !important;
}

/* 參數說明小字 */
.small-note {
    font-size: 0.86rem;
    color: #777;
    line-height: 1.55;
}

/* 結果卡片 */
.stock-card {
    border: 1px solid rgba(128,128,128,0.22);
    border-radius: 20px;
    padding: 16px 16px 14px 16px;
    margin: 13px 0;
    box-shadow: 0 2px 12px rgba(0,0,0,0.045);
    background: rgba(255,255,255,0.03);
}
.stock-title {
    font-size: 1.25rem;
    line-height: 1.35;
    font-weight: 850;
    margin-bottom: 2px;
}
.stock-subtitle {
    font-size: 0.86rem;
    color: #777;
    margin-bottom: 12px;
}
.metric-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 9px;
    margin-bottom: 10px;
}
.metric-box {
    border: 1px solid rgba(128,128,128,0.18);
    border-radius: 15px;
    padding: 10px 10px;
    background: rgba(128,128,128,0.05);
}
.metric-label {
    font-size: 0.75rem;
    color: #777;
    margin-bottom: 4px;
}
.metric-value {
    font-size: 1.05rem;
    font-weight: 850;
}
.suggestion-box {
    border-radius: 15px;
    padding: 12px 12px;
    margin-top: 10px;
    line-height: 1.58;
    font-size: 0.96rem;
}
.signal-buy {
    background: rgba(34, 197, 94, 0.16);
    border: 1px solid rgba(34, 197, 94, 0.45);
}
.signal-hold {
    background: rgba(0, 123, 255, 0.10);
    border: 1px solid rgba(0, 123, 255, 0.28);
}
.signal-watch {
    background: rgba(255, 193, 7, 0.14);
    border: 1px solid rgba(255, 193, 7, 0.35);
}
.signal-reduce {
    background: rgba(220, 53, 69, 0.16);
    border: 1px solid rgba(220, 53, 69, 0.45);
}
.signal-sell {
    background: rgba(185, 28, 28, 0.20);
    border: 1px solid rgba(185, 28, 28, 0.55);
}
.signal-na {
    background: rgba(128, 128, 128, 0.10);
    border: 1px solid rgba(128, 128, 128, 0.25);
}
.badge {
    display: inline-block;
    border-radius: 999px;
    padding: 4px 10px;
    font-size: 0.78rem;
    font-weight: 850;
    margin-bottom: 9px;
}
.signal-buy.badge { color: #15803d; }
.signal-hold.badge { color: #1d4ed8; }
.signal-watch.badge { color: #a16207; }
.signal-reduce.badge { color: #b91c1c; }
.signal-sell.badge { color: #991b1b; }

/* 手機優化 */
@media (max-width: 640px) {
    .block-container {
        padding-left: 0.78rem;
        padding-right: 0.78rem;
        padding-top: 1.9rem;
    }
    .top-safe-space {
        height: 10px;
    }
    .app-hero {
        border-radius: 22px;
        padding: 18px 15px 15px 15px;
        margin-bottom: 14px;
        box-shadow: 0 8px 22px rgba(35, 80, 140, 0.10);
    }
    .app-title-row {
        min-height: 42px;
        gap: 9px;
        align-items: center;
    }
    .app-icon {
        width: 32px;
        height: 32px;
        min-width: 32px;
        font-size: 1.04rem;
        border-radius: 10px;
    }
    .app-title {
        font-size: 1.26rem;
        line-height: 1.75;
        padding-top: 1px;
    }
    .app-subtitle {
        font-size: 0.86rem;
        line-height: 1.65;
        margin-left: 41px;
    }
    .hero-tags {
        margin-left: 41px;
        gap: 6px;
    }
    .hero-tag {
        font-size: 0.72rem;
        padding: 4px 8px;
    }
    .soft-alert {
        font-size: 0.88rem;
        border-radius: 14px;
        padding: 10px 12px;
    }
    .section-title {
        font-size: 1.12rem;
        margin-top: 16px;
    }
    .metric-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 7px;
    }
    .metric-box {
        padding: 9px 8px;
        border-radius: 14px;
    }
    .metric-value {
        font-size: 0.98rem;
    }
    .stock-card {
        padding: 14px 12px;
        border-radius: 17px;
    }
    div[data-testid="stDataFrame"] {
        font-size: 0.82rem;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


# -----------------------------
# Header
# -----------------------------
st.markdown(
    """
<div class="top-safe-space"></div>
<div class="app-hero">
    <div class="app-title-row">
        <div class="app-icon">📈</div>
        <div class="app-title">台股法人成本 / 均線評估</div>
    </div>
    <div class="app-subtitle">操作順序：設定判斷參數 → 輸入股票 → 開始評估 → 查看卡片結果。</div>
    <div class="hero-tags">
        <span class="hero-tag">最新股價</span>
        <span class="hero-tag">5日 / 10日線</span>
        <span class="hero-tag">兩週漲幅</span>
        <span class="hero-tag">買賣建議</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="soft-alert">
    法人成本價與法人目標價建議手動輸入。若啟用估算法人成本，僅是用近 N 日均價近似，不等於真正法人成本。
</div>
""",
    unsafe_allow_html=True,
)


# -----------------------------
# 股票代號/名稱解析
# -----------------------------
COMMON_NAME_MAP = {
    "台積電": "2330",
    "鴻海": "2317",
    "聯發科": "2454",
    "國巨": "2327",
    "永光": "1711",
    "南亞": "1303",
    "中磊": "5388",
    "上銀": "2049",
    "佳能": "2374",
    "元大台灣50": "0050",
    "0050": "0050",
    "00981A": "00981A",
    "00981a": "00981A",
}


@st.cache_data(ttl=24 * 3600, show_spinner=False)
def load_twstock_codes() -> Dict[str, Dict[str, str]]:
    try:
        import twstock  # type: ignore

        result = {}
        for code, info in twstock.codes.items():
            try:
                result[code] = {
                    "code": code,
                    "name": info.name,
                    "market": info.market,
                    "type": info.type,
                }
            except Exception:
                continue
        return result
    except Exception:
        return {}


def resolve_stock_query(query: str, code_db: Dict[str, Dict[str, str]]) -> Tuple[str, str, str]:
    q = str(query).strip()
    if not q:
        return "", "", ""

    if q.upper().endswith((".TW", ".TWO")):
        code = q.split(".")[0].upper()
        info = code_db.get(code, {})
        return code, info.get("name", q), info.get("market", "")

    m = re.search(r"\b([0-9]{4,6}[A-Za-z]?)\b", q)
    if m:
        code = m.group(1).upper()
        info = code_db.get(code, {})
        return code, info.get("name", q), info.get("market", "")

    if q in COMMON_NAME_MAP:
        code = COMMON_NAME_MAP[q]
        info = code_db.get(code, {})
        return code, info.get("name", q), info.get("market", "")

    exact_matches = [
        v for v in code_db.values()
        if str(v.get("name", "")).strip().lower() == q.lower()
    ]
    if exact_matches:
        item = exact_matches[0]
        return item["code"], item.get("name", q), item.get("market", "")

    partial_matches = [
        v for v in code_db.values()
        if q.lower() in str(v.get("name", "")).lower()
    ]
    if partial_matches:
        item = partial_matches[0]
        return item["code"], item.get("name", q), item.get("market", "")

    return q.upper(), q, ""


def yahoo_candidates(code: str, market: str = "") -> List[str]:
    code = str(code).upper().strip()
    market = str(market).strip()

    if market == "上櫃":
        return [f"{code}.TWO", f"{code}.TW"]
    return [f"{code}.TW", f"{code}.TWO"]


@st.cache_data(ttl=10 * 60, show_spinner=False)
def fetch_history_from_yahoo(code: str, market: str = "") -> Tuple[pd.DataFrame, str, str]:
    errors = []
    for ticker in yahoo_candidates(code, market):
        try:
            df = yf.Ticker(ticker).history(period="3mo", interval="1d", auto_adjust=False)
            if df is not None and not df.empty and "Close" in df.columns:
                df = df.dropna(subset=["Close"]).copy()
                if not df.empty:
                    return df, ticker, ""
        except Exception as e:
            errors.append(f"{ticker}: {e}")

    return pd.DataFrame(), "", " / ".join(errors) if errors else "No data"


def latest_price_from_history(df: pd.DataFrame) -> Optional[float]:
    if df.empty or "Close" not in df:
        return None
    return float(df["Close"].dropna().iloc[-1])


def moving_average(df: pd.DataFrame, days: int) -> Optional[float]:
    if df.empty or len(df["Close"].dropna()) < days:
        return None
    return float(df["Close"].dropna().tail(days).mean())


def two_week_performance(df: pd.DataFrame, trading_days: int = 10) -> Tuple[Optional[float], Optional[float]]:
    if df.empty or "Close" not in df:
        return None, None

    close = df["Close"].dropna()
    if len(close) <= trading_days:
        return None, None

    latest = float(close.iloc[-1])
    base = float(close.iloc[-trading_days - 1])

    if base <= 0:
        return base, None

    perf_pct = (latest / base - 1) * 100
    return base, perf_pct


def stable_above_level(
    df: pd.DataFrame,
    level: float,
    stable_days: int,
    require_ma_bull: bool,
) -> bool:
    if df.empty or len(df["Close"].dropna()) < stable_days:
        return False

    recent_ok = bool((df["Close"].dropna().tail(stable_days) >= level).all())

    if not require_ma_bull:
        return recent_ok

    ma5 = moving_average(df, 5)
    ma10 = moving_average(df, 10)
    if ma5 is None or ma10 is None:
        return False

    return recent_ok and ma5 >= ma10


def fmt_num(x: Optional[float], digits: int = 2) -> str:
    if x is None or pd.isna(x):
        return "-"
    return f"{x:.{digits}f}"


def fmt_pct(x: Optional[float], digits: int = 2) -> str:
    if x is None or pd.isna(x):
        return "-"
    sign = "+" if x > 0 else ""
    return f"{sign}{x:.{digits}f}%"


def to_float_or_none(x) -> Optional[float]:
    try:
        if x is None or x == "":
            return None
        value = float(x)
        if np.isnan(value):
            return None
        return value
    except Exception:
        return None


def make_suggestion(
    price: Optional[float],
    ma5: Optional[float],
    ma10: Optional[float],
    legal_cost: Optional[float],
    target_price: Optional[float],
    two_week_perf: Optional[float],
    df: pd.DataFrame,
    stable_days: int,
    require_ma_bull: bool,
    strong_gain_pct: float,
) -> Tuple[str, str]:
    if price is None:
        return "抓不到股價，請確認代號/名稱。", "NA"

    notes = []
    signal = "HOLD"

    # 均線風控優先
    if ma10 is not None and price < ma10:
        notes.append("🔴 跌破 10 日線：建議賣出或至少減碼")
        signal = "SELL"
    elif ma5 is not None and price < ma5:
        notes.append("🟠 跌破 5 日線：短線轉弱，小心觀察")
        signal = "REDUCE"
    else:
        notes.append("✅ 股價仍在 5 日/10 日線上方，短線結構尚可")
        signal = "HOLD"

    # 兩週漲幅提醒
    if two_week_perf is not None:
        if two_week_perf >= strong_gain_pct:
            notes.append(f"⚠️ 兩週漲幅已達 {two_week_perf:.1f}%：追價風險升高，適合等拉回或用 5 日線移動停利")
            if signal in ("BUY/HOLD", "HOLD"):
                signal = "HOLD"
        elif two_week_perf <= -8:
            notes.append(f"⚠️ 兩週跌幅 {two_week_perf:.1f}%：短線偏弱，先不要急著接")
            if signal != "SELL":
                signal = "WATCH"

    # 法人成本 / 1.2 / 1.4 倍邏輯
    if legal_cost is not None and legal_cost > 0:
        level_12 = legal_cost * 1.2
        level_14 = legal_cost * 1.4
        is_stable_12 = stable_above_level(df, level_12, stable_days, require_ma_bull)

        if price >= level_14:
            notes.append("🟣 已達或超過 1.4 倍法人成本：可考慮分批停利，或用 5 日線做移動停利")
            if signal not in ("SELL", "REDUCE"):
                signal = "REDUCE"
        elif is_stable_12:
            notes.append("🟢 已站穩 1.2 倍法人成本：偏多續抱，觀察是否挑戰 1.4 倍")
            if signal == "HOLD":
                signal = "BUY/HOLD"
        elif price >= level_12:
            notes.append("🟢 突破 1.2 倍法人成本，但尚未確認站穩：續抱觀察")
            if signal == "HOLD":
                signal = "HOLD"
        elif price >= legal_cost:
            notes.append("🟡 股價在法人成本上方，但未到 1.2 倍：偏中性，等突破")
            if signal == "HOLD":
                signal = "WATCH"
        else:
            notes.append("⚪ 股價低於法人成本：籌碼優勢不明，保守觀望")
            if signal == "HOLD":
                signal = "WATCH"
    else:
        notes.append("未輸入法人成本價：僅用均線與兩週漲幅判斷")

    # 目標價邏輯
    if target_price is not None and target_price > 0:
        upside = (target_price / price - 1) * 100
        if upside >= 20:
            notes.append(f"法人目標價仍有 {upside:.1f}% 空間")
        elif upside >= 5:
            notes.append(f"距法人目標價剩 {upside:.1f}%：續抱但不宜追太急")
        elif upside >= 0:
            notes.append(f"接近法人目標價，剩 {upside:.1f}%：留意停利")
            if signal in ("BUY/HOLD", "HOLD"):
                signal = "HOLD"
        else:
            notes.append(f"已高於法人目標價 {-upside:.1f}%：追價風險高")
            if signal != "SELL":
                signal = "REDUCE"

    return "；".join(notes), signal


def signal_css(signal: str) -> str:
    s = str(signal).upper()
    if "SELL" in s:
        return "signal-sell"
    if "REDUCE" in s:
        return "signal-reduce"
    if "WATCH" in s:
        return "signal-watch"
    if "BUY" in s:
        return "signal-buy"
    if "HOLD" in s:
        return "signal-hold"
    return "signal-na"


def evaluate_stocks(
    input_df: pd.DataFrame,
    stable_days: int,
    require_ma_bull: bool,
    use_estimated_cost: bool,
    estimate_days: int,
    strong_gain_pct: float,
) -> pd.DataFrame:
    code_db = load_twstock_codes()
    rows = []

    valid_inputs = input_df.dropna(how="all").copy()

    for _, row in valid_inputs.iterrows():
        query = str(row.get("股票代號或名稱", "")).strip()
        if not query:
            continue

        legal_cost = to_float_or_none(row.get("法人成本價"))
        target_price = to_float_or_none(row.get("法人目標價"))

        code, name, market = resolve_stock_query(query, code_db)
        hist, yahoo_ticker, err = fetch_history_from_yahoo(code, market)

        price = latest_price_from_history(hist)
        ma5 = moving_average(hist, 5)
        ma10 = moving_average(hist, 10)
        two_week_base, two_week_perf = two_week_performance(hist, trading_days=10)

        cost_source = "手動"
        if (legal_cost is None or legal_cost <= 0) and use_estimated_cost and not hist.empty:
            close_series = hist["Close"].dropna()
            if len(close_series) >= estimate_days:
                legal_cost = float(close_series.tail(int(estimate_days)).mean())
                cost_source = f"近{estimate_days}日均價估算"
            else:
                legal_cost = None
                cost_source = "無"

        level_12 = legal_cost * 1.2 if legal_cost else None
        level_14 = legal_cost * 1.4 if legal_cost else None
        price_to_cost = price / legal_cost if price and legal_cost else None
        target_upside = (target_price / price - 1) * 100 if price and target_price else None

        suggestion, signal = make_suggestion(
            price=price,
            ma5=ma5,
            ma10=ma10,
            legal_cost=legal_cost,
            target_price=target_price,
            two_week_perf=two_week_perf,
            df=hist,
            stable_days=int(stable_days),
            require_ma_bull=bool(require_ma_bull),
            strong_gain_pct=float(strong_gain_pct),
        )

        rows.append(
            {
                "輸入": query,
                "股票代號": code,
                "股票名稱": name,
                "市場": market or "-",
                "Yahoo Ticker": yahoo_ticker or "-",
                "最新價/近收盤": price,
                "5日線": ma5,
                "10日線": ma10,
                "兩週前收盤": two_week_base,
                "兩週漲幅%": two_week_perf,
                "法人成本價": legal_cost,
                "成本來源": cost_source if legal_cost else "-",
                "1.2倍法人成本": level_12,
                "1.4倍法人成本": level_14,
                "股價/法人成本": price_to_cost,
                "法人目標價": target_price,
                "距目標價%": target_upside,
                "訊號": signal,
                "買賣建議": suggestion,
                "錯誤訊息": err if err and hist.empty else "",
            }
        )

    return pd.DataFrame(rows)


def show_stock_card(row: pd.Series) -> None:
    signal = str(row.get("訊號", "NA"))
    css = signal_css(signal)

    title = html.escape(f"{row.get('股票代號', '-') } {row.get('股票名稱', '-')}")
    subtitle = html.escape(f"{row.get('市場', '-')}｜{row.get('Yahoo Ticker', '-')}")
    suggestion = html.escape(str(row.get("買賣建議", "-")))

    card_html = f"""
<div class="stock-card">
    <div class="stock-title">{title}</div>
    <div class="stock-subtitle">{subtitle}</div>
    <span class="badge {css}">訊號：{html.escape(signal)}</span>
    <div class="metric-grid">
        <div class="metric-box">
            <div class="metric-label">最新價 / 近收盤</div>
            <div class="metric-value">{fmt_num(row.get('最新價/近收盤'))}</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">兩週漲幅</div>
            <div class="metric-value">{fmt_pct(row.get('兩週漲幅%'))}</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">5 日線</div>
            <div class="metric-value">{fmt_num(row.get('5日線'))}</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">10 日線</div>
            <div class="metric-value">{fmt_num(row.get('10日線'))}</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">法人成本價</div>
            <div class="metric-value">{fmt_num(row.get('法人成本價'))}</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">股價 / 法人成本</div>
            <div class="metric-value">{fmt_num(row.get('股價/法人成本'), 2)}x</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">1.2 倍法人成本</div>
            <div class="metric-value">{fmt_num(row.get('1.2倍法人成本'))}</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">1.4 倍法人成本</div>
            <div class="metric-value">{fmt_num(row.get('1.4倍法人成本'))}</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">法人目標價</div>
            <div class="metric-value">{fmt_num(row.get('法人目標價'))}</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">距目標價</div>
            <div class="metric-value">{fmt_pct(row.get('距目標價%'))}</div>
        </div>
    </div>
    <div class="suggestion-box {css}">
        <b>建議：</b>{suggestion}
    </div>
</div>
"""
    st.markdown(card_html, unsafe_allow_html=True)


# -----------------------------
# Top-down parameters
# -----------------------------
st.markdown('<div class="section-title">1) 判斷參數</div>', unsafe_allow_html=True)
st.markdown('<div class="section-hint">先設定你要用的技術條件；手機上會由上到下顯示，不再使用左側收合欄。</div>', unsafe_allow_html=True)

with st.container(border=True):
    stable_days = st.number_input(
        "站穩 1.2 倍需要連續幾個交易日？",
        min_value=1,
        max_value=10,
        value=3,
        step=1,
    )

    require_ma_bull = st.checkbox(
        "站穩 1.2 倍時，要求 5 日線 ≥ 10 日線",
        value=True,
    )

    strong_gain_pct = st.number_input(
        "兩週漲幅超過多少 % 提醒追高？",
        min_value=3.0,
        max_value=50.0,
        value=15.0,
        step=1.0,
        format="%.2f",
    )

    use_estimated_cost = st.checkbox(
        "若法人成本空白，用近 N 日均價估算",
        value=False,
    )

    estimate_days = st.number_input(
        "估算法人成本：近 N 日均價",
        min_value=5,
        max_value=120,
        value=20,
        step=5,
        disabled=not use_estimated_cost,
    )

    st.caption("建議：若券商 App 有法人成本價，優先手動輸入，不要用估算值取代。")


# -----------------------------
# Input table
# -----------------------------
st.markdown('<div class="section-title">2) 輸入股票</div>', unsafe_allow_html=True)
st.markdown('<div class="section-hint">輸入股票代號或名稱；法人成本價、法人目標價可空白。手機上可直接點表格欄位輸入。</div>', unsafe_allow_html=True)

default_df = pd.DataFrame(
    [
        {"股票代號或名稱": "2330", "法人成本價": np.nan, "法人目標價": np.nan},
        {"股票代號或名稱": "2454", "法人成本價": np.nan, "法人目標價": np.nan},
        {"股票代號或名稱": "永光", "法人成本價": np.nan, "法人目標價": np.nan},
    ]
)

input_df = st.data_editor(
    default_df,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    column_config={
        "股票代號或名稱": st.column_config.TextColumn(
            "股票代號或名稱",
            help="可輸入 2330、台積電、2454、聯發科等。名稱解析不到時，請改輸入代號。",
            required=True,
        ),
        "法人成本價": st.column_config.NumberColumn(
            "法人成本價",
            help="請填你從券商/看盤軟體看到的法人持股成本或主力成本。",
            min_value=0.0,
            format="%.2f",
        ),
        "法人目標價": st.column_config.NumberColumn(
            "法人目標價",
            help="請填券商報告或你信任來源的法人目標價。",
            min_value=0.0,
            format="%.2f",
        ),
    },
)

run_button = st.button("3) 開始評估", type="primary")


# -----------------------------
# Main evaluation
# -----------------------------
if run_button:
    if input_df.empty:
        st.error("請至少輸入一檔股票。")
        st.stop()

    with st.spinner("抓取股價與計算中..."):
        result_df = evaluate_stocks(
            input_df=input_df,
            stable_days=int(stable_days),
            require_ma_bull=bool(require_ma_bull),
            use_estimated_cost=bool(use_estimated_cost),
            estimate_days=int(estimate_days),
            strong_gain_pct=float(strong_gain_pct),
        )

    if result_df.empty:
        st.error("沒有可評估的股票。請確認輸入格式。")
        st.stop()

    st.markdown('<div class="section-title">4) 評估結果</div>', unsafe_allow_html=True)

    show_table = st.toggle("顯示完整表格", value=False)

    if show_table:
        display_df = result_df.copy()
        number_cols = [
            "最新價/近收盤",
            "5日線",
            "10日線",
            "兩週前收盤",
            "兩週漲幅%",
            "法人成本價",
            "1.2倍法人成本",
            "1.4倍法人成本",
            "股價/法人成本",
            "法人目標價",
            "距目標價%",
        ]
        for col in number_cols:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: None if pd.isna(x) else round(float(x), 2))
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    for _, r in result_df.iterrows():
        show_stock_card(r)

    # Download Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        result_df.to_excel(writer, index=False, sheet_name="Stock_Evaluation")
    output.seek(0)

    st.download_button(
        label="下載 Excel 結果",
        data=output,
        file_name="stock_evaluation_result.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

    with st.expander("判斷邏輯說明"):
        st.markdown(
            f"""
- 跌破 **5 日線**：短線轉弱，小心觀察。
- 跌破 **10 日線**：建議賣出或至少減碼。
- 站穩 **1.2 倍法人成本**：最近 **{stable_days} 個交易日** 都在 1.2 倍法人成本上方；若有勾選，也要求 **5 日線 ≥ 10 日線**。
- 接近或超過 **1.4 倍法人成本**：偏向分批停利，或用 5 日線移動停利。
- 兩週漲幅超過 **{strong_gain_pct:.0f}%**：提醒追高風險，不代表一定要賣。
"""
        )
else:
    st.info("請由上往下操作：確認判斷參數 → 輸入股票 → 按「開始評估」。")
