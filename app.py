import html
from datetime import date
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Expense Tracker", page_icon="💸", layout="wide")

# ============================== CONFIG ==============================
COLUMNS = ["Date", "Category", "Description", "Amount", "Payment", "Currency"]
OLD_COLUMNS = ["Date", "Category", "Description", "Amount", "Payment"]  # older version
CSV_PATH = Path("expenses.csv")

CATEGORIES = {
    "Food": "🍜", "Groceries": "🛒", "Transport": "🚌", "Rent": "🏠",
    "Bills": "💡", "Shopping": "🛍️", "Health": "💊", "Entertainment": "🎬",
    "Travel": "✈️", "Education": "📚", "Other": "✨",
}
PAYMENTS = ["UPI", "Cash", "Card", "Net Banking"]

# code: (symbol, flag, name)
CURRENCIES = {
    "INR": ("₹", "🇮🇳", "Indian Rupee"),
    "USD": ("$", "🇺🇸", "US Dollar"),
    "EUR": ("€", "🇪🇺", "Euro"),
    "GBP": ("£", "🇬🇧", "British Pound"),
    "AED": ("AED ", "🇦🇪", "UAE Dirham"),
    "JPY": ("¥", "🇯🇵", "Japanese Yen"),
    "SGD": ("S$", "🇸🇬", "Singapore Dollar"),
    "AUD": ("A$", "🇦🇺", "Australian Dollar"),
}
# Approximate starting values (value of 1 unit in INR).
# You can edit them in the sidebar, or change them here to make them permanent.
DEFAULT_RATES_INR = {
    "INR": 1.0, "USD": 88.0, "EUR": 102.0, "GBP": 116.0,
    "AED": 24.0, "JPY": 0.58, "SGD": 68.0, "AUD": 57.0,
}

CAT_PALETTE = ["#6c5ce7", "#00b894", "#ff7eb3", "#fdcb6e", "#0984e3", "#e17055",
               "#a29bfe", "#55efc4", "#fab1a0", "#74b9ff", "#b2bec3"]
CAT_COLORS = dict(zip(CATEGORIES, CAT_PALETTE))
PAY_PALETTE = ["#6c5ce7", "#00b894", "#fdcb6e", "#ff7eb3"]
PAY_COLORS = dict(zip(PAYMENTS, PAY_PALETTE))

THEMES = {
    "dark": dict(
        bg1="#0e1020", bg2="#181b33", card="#1c2040", text="#eceeff", muted="#9ba1c9",
        border="rgba(255,255,255,0.09)", accent="#8b7bff", accent2="#ff7eb3",
        input="#262b55", shadow="0 8px 30px rgba(0,0,0,0.35)", grid="rgba(255,255,255,0.08)",
    ),
    "light": dict(
        bg1="#faf8ff", bg2="#e8edff", card="#ffffff", text="#1f2340", muted="#6b7090",
        border="rgba(31,35,64,0.09)", accent="#6c5ce7", accent2="#fd79a8",
        input="#f1efff", shadow="0 8px 30px rgba(108,92,231,0.13)", grid="rgba(31,35,64,0.08)",
    ),
}

CSS_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
.stApp, .stApp button, .stApp input, .stApp textarea { font-family: 'Poppins', sans-serif; }
.stApp { background: linear-gradient(135deg, __BG1__ 0%, __BG2__ 100%); color: __TEXT__; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { background: __CARD__; border-right: 1px solid __BORDER__; }
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp li,
[data-testid="stWidgetLabel"] p, [data-testid="stMarkdownContainer"] { color: __TEXT__; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p { color: __MUTED__; }
div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="select"] > div,
div[data-baseweb="textarea"] { background-color: __INPUT__ !important; border-radius: 12px !important; border-color: __BORDER__ !important; }
.stApp input, .stApp textarea, div[data-baseweb="select"] * { color: __TEXT__ !important; }
[data-testid="stNumberInput"] button { background: __INPUT__ !important; color: __TEXT__ !important; border: none; }
div[data-baseweb="popover"] > div, ul[role="listbox"], div[data-baseweb="calendar"] { background: __CARD__ !important; color: __TEXT__ !important; }
ul[role="listbox"] li, div[data-baseweb="calendar"] * { color: __TEXT__ !important; }
[data-testid="stExpander"] { background: __CARD__; border: 1px solid __BORDER__; border-radius: 16px; }
.stButton > button, [data-testid="stFormSubmitButton"] > button, .stDownloadButton > button {
  background: linear-gradient(135deg, __ACCENT__, __ACCENT2__); border: none; border-radius: 12px;
  padding: .55rem 1.3rem; font-weight: 600; box-shadow: __SHADOW__; transition: transform .15s ease; }
.stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover, .stDownloadButton > button:hover { transform: translateY(-2px); }
.stButton > button p, [data-testid="stFormSubmitButton"] > button p, .stDownloadButton > button p { color: #ffffff !important; }
[class*="st-key-card"] { background: __CARD__; border: 1px solid __BORDER__; border-radius: 22px; padding: 1.1rem 1.3rem; box-shadow: __SHADOW__; }
.hero { background: linear-gradient(135deg, __ACCENT__, __ACCENT2__); border-radius: 26px; padding: 1.7rem 2.1rem; box-shadow: __SHADOW__; margin-bottom: 1.2rem; }
.hero h1 { color: #ffffff !important; margin: 0; font-size: 2.1rem; font-weight: 700; padding: 0; }
.hero p { color: rgba(255,255,255,0.9) !important; margin: .35rem 0 0; }
.kpi { background: __CARD__; border: 1px solid __BORDER__; border-radius: 20px; padding: 1.1rem 1.3rem; box-shadow: __SHADOW__; height: 100%; }
.kpi .label { color: __MUTED__; font-size: .74rem; text-transform: uppercase; letter-spacing: .09em; }
.kpi .value { color: __TEXT__; font-size: 1.55rem; font-weight: 700; margin-top: .3rem; }
.panel-title { font-weight: 600; font-size: 1.05rem; color: __TEXT__; margin-bottom: .1rem; }
.panel-sub { color: __MUTED__; font-size: .82rem; margin-bottom: .4rem; }
.table-wrap { max-height: 430px; overflow: auto; background: __CARD__; border: 1px solid __BORDER__; border-radius: 20px; box-shadow: __SHADOW__; }
.table-wrap table { width: 100%; border-collapse: collapse; font-size: .9rem; }
.table-wrap th { position: sticky; top: 0; background: __CARD__; color: __MUTED__; text-align: left; padding: .85rem 1rem; font-weight: 500; font-size: .73rem; text-transform: uppercase; letter-spacing: .07em; border-bottom: 1px solid __BORDER__; }
.table-wrap td { padding: .7rem 1rem; color: __TEXT__; border-bottom: 1px solid __BORDER__; }
.table-wrap tr:hover td { background: __INPUT__; }
.pill { display: inline-block; padding: .15rem .7rem; border-radius: 999px; background: __INPUT__; font-size: .8rem; white-space: nowrap; }
.amt { font-weight: 600; text-align: right; white-space: nowrap; }
</style>
"""


def apply_theme(theme):
    css = CSS_TEMPLATE
    for key, value in theme.items():
        css = css.replace(f"__{key.upper()}__", value)
    st.markdown(css, unsafe_allow_html=True)


def fmt(value, code):
    symbol = CURRENCIES.get(code, ("", "", ""))[0]
    decimals = 0 if code == "JPY" else 2
    return f"{symbol}{value:,.{decimals}f}"


def currency_label(code):
    _, flag, name = CURRENCIES[code]
    return f"{flag} {code} · {name}"


# ============================== AUTH ==============================
def check_password():
    try:
        pwd = st.secrets.get("app_password")
    except Exception:
        pwd = None
    if not pwd:
        return True
    if st.session_state.get("authed"):
        return True
    entered = st.text_input("Password", type="password")
    if entered:
        if entered == pwd:
            st.session_state["authed"] = True
            st.rerun()
        else:
            st.error("Wrong password")
    return False


# ============================== STORAGE ==============================
def sheets_enabled():
    try:
        return "gcp_service_account" in st.secrets and "sheet_url" in st.secrets
    except Exception:
        return False


@st.cache_resource
def get_sheet():
    import gspread
    from google.oauth2.service_account import Credentials

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]), scopes=scopes
    )
    sheet = gspread.authorize(creds).open_by_url(st.secrets["sheet_url"]).sheet1
    header = sheet.row_values(1)
    if header == COLUMNS:
        pass
    elif header == OLD_COLUMNS:
        sheet.update_cell(1, 6, "Currency")  # upgrade older sheet in place
    else:
        sheet.insert_row(COLUMNS, 1)
    return sheet


@st.cache_data(ttl=60, show_spinner=False)
def load_data():
    if sheets_enabled():
        df = pd.DataFrame(get_sheet().get_all_records(), columns=COLUMNS)
    elif CSV_PATH.exists():
        df = pd.read_csv(CSV_PATH)
        if "Currency" not in df:
            df["Currency"] = "INR"
        df = df.reindex(columns=COLUMNS)
    else:
        df = pd.DataFrame(columns=COLUMNS)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
    df["Currency"] = df["Currency"].replace("", "INR").fillna("INR")
    df.loc[~df["Currency"].isin(CURRENCIES), "Currency"] = "INR"
    return df.reset_index(drop=True)


def add_expense(d, category, description, amount, payment, currency):
    row = [d.isoformat(), category, description, float(amount), payment, currency]
    if sheets_enabled():
        get_sheet().append_row(row, value_input_option="USER_ENTERED")
    else:
        new = pd.DataFrame([row], columns=COLUMNS)
        if CSV_PATH.exists():
            old = pd.read_csv(CSV_PATH)
            if "Currency" not in old:
                old["Currency"] = "INR"
            new = pd.concat([old.reindex(columns=COLUMNS), new], ignore_index=True)
        new.to_csv(CSV_PATH, index=False)
    load_data.clear()


def delete_expense(index):
    if sheets_enabled():
        get_sheet().delete_rows(index + 2)  # +1 header row, +1 because sheets are 1-based
    else:
        pd.read_csv(CSV_PATH).drop(index=index).to_csv(CSV_PATH, index=False)
    load_data.clear()


# ============================== CHARTS ==============================
def base_layout(fig, t, height=340):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=t["text"], family="Poppins, sans-serif"),
        margin=dict(l=10, r=10, t=10, b=10), height=height,
    )
    return fig


def donut(labels, values, colors, center_text, symbol, t):
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.62, sort=True, direction="clockwise",
        marker=dict(colors=colors, line=dict(color=t["card"], width=3)),
        textinfo="percent", textposition="inside", insidetextorientation="horizontal",
        hovertemplate="%{label}<br>" + symbol + "%{value:,.2f}<br>%{percent}<extra></extra>",
    ))
    base_layout(fig, t, height=360)
    fig.update_layout(
        uniformtext_minsize=11, uniformtext_mode="hide",
        legend=dict(orientation="h", y=-0.04, x=0.5, xanchor="center"),
        annotations=[dict(text=center_text, x=0.5, y=0.5, showarrow=False,
                          font=dict(size=15, color=t["text"]))],
    )
    return fig


def monthly_bar(months, values, symbol, t):
    fig = go.Figure(go.Bar(
        x=months, y=values, marker=dict(color=t["accent"]),
        hovertemplate="%{x}<br>" + symbol + "%{y:,.2f}<extra></extra>",
    ))
    base_layout(fig, t, height=300)
    fig.update_layout(bargap=0.45)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor=t["grid"], zeroline=False)
    return fig


# ============================== APP ==============================
with st.sidebar:
    dark = st.toggle("🌙 Dark mode", value=True, key="dark_mode")
theme = THEMES["dark" if dark else "light"]
apply_theme(theme)

st.markdown(
    "<div class='hero'><h1>💸 My Expense Tracker</h1>"
    "<p>Track your spending across currencies, beautifully.</p></div>",
    unsafe_allow_html=True,
)

if not check_password():
    st.stop()

codes = list(CURRENCIES)

with st.sidebar:
    st.markdown("### Settings")
    display_cur = st.selectbox("Display currency", codes, format_func=currency_label, key="display_cur")

    with st.expander("Exchange rates"):
        st.caption("Approximate starting values. Update them to the rates you want. "
                   "They are used only to convert totals into your display currency.")
        RATES = {"INR": 1.0}
        for code in codes[1:]:
            RATES[code] = st.number_input(
                f"1 {code} = ₹", min_value=0.0001, value=DEFAULT_RATES_INR[code],
                format="%.4f", key=f"rate_{code}",
            )

    st.markdown("### Add expense")
    with st.form("add_form", clear_on_submit=True):
        d = st.date_input("Date", value=date.today())
        category = st.selectbox("Category", list(CATEGORIES), format_func=lambda c: f"{CATEGORIES[c]} {c}")
        description = st.text_input("Description")
        c_amt, c_cur = st.columns([3, 2])
        amount = c_amt.number_input("Amount", min_value=0.0, step=10.0, format="%.2f")
        currency = c_cur.selectbox("Currency", codes, index=codes.index(display_cur))
        payment = st.selectbox("Payment method", PAYMENTS)
        submitted = st.form_submit_button("Add expense")
    if submitted:
        if amount <= 0:
            st.error("Enter an amount greater than 0")
        else:
            add_expense(d, category, description, amount, payment, currency)
            st.success("Expense saved")
            st.rerun()

if not sheets_enabled():
    st.caption("⚠️ Using local CSV storage. On Streamlit Cloud this resets on restart. "
               "Connect Google Sheets for permanent storage.")

df = load_data()

if df.empty:
    st.info("No expenses yet. Add your first one from the sidebar.")
    st.stop()

symbol = CURRENCIES[display_cur][0]
df["Converted"] = df["Amount"] * df["Currency"].map(RATES) / RATES[display_cur]
df["Month"] = df["Date"].dt.strftime("%Y-%m")

months = ["All time"] + sorted(df["Month"].dropna().unique(), reverse=True)
selected = st.selectbox("📅 Period", months)
view = df if selected == "All time" else df[df["Month"] == selected]

total = view["Converted"].sum()
count = len(view)
average = total / count if count else 0
by_cat = view.groupby("Category")["Converted"].sum().sort_values(ascending=False)
top_cat = by_cat.index[0] if len(by_cat) else "-"
top_cat_label = f"{CATEGORIES.get(top_cat, '✨')} {top_cat}" if top_cat != "-" else "-"

# ---- KPI cards ----
kpis = [
    ("Total spent", fmt(total, display_cur)),
    ("Transactions", f"{count}"),
    ("Average per entry", fmt(average, display_cur)),
    ("Top category", top_cat_label),
]
for col, (label, value) in zip(st.columns(4), kpis):
    col.markdown(
        f"<div class='kpi'><div class='label'>{label}</div><div class='value'>{value}</div></div>",
        unsafe_allow_html=True,
    )

st.write("")

# ---- Pie (donut) charts ----
left, right = st.columns(2)
with left:
    with st.container(key="card_category"):
        st.markdown("<div class='panel-title'>Where your money goes</div>"
                    "<div class='panel-sub'>Share of spending by category</div>", unsafe_allow_html=True)
        fig = donut(
            [f"{CATEGORIES.get(c, '✨')} {c}" for c in by_cat.index],
            by_cat.values,
            [CAT_COLORS.get(c, theme["accent"]) for c in by_cat.index],
            f"Total<br><b>{fmt(total, display_cur)}</b>", symbol, theme,
        )
        st.plotly_chart(fig, config={"displayModeBar": False})

with right:
    with st.container(key="card_payment"):
        st.markdown("<div class='panel-title'>How you pay</div>"
                    "<div class='panel-sub'>Share of spending by payment method</div>", unsafe_allow_html=True)
        by_pay = view.groupby("Payment")["Converted"].sum().sort_values(ascending=False)
        fig = donut(
            list(by_pay.index), by_pay.values,
            [PAY_COLORS.get(p, theme["accent"]) for p in by_pay.index],
            f"{count}<br>entries", symbol, theme,
        )
        st.plotly_chart(fig, config={"displayModeBar": False})

st.write("")

# ---- Monthly trend ----
with st.container(key="card_trend"):
    st.markdown("<div class='panel-title'>Monthly spending</div>"
                f"<div class='panel-sub'>Total per month in {display_cur}</div>", unsafe_allow_html=True)
    monthly = df.dropna(subset=["Month"]).groupby("Month")["Converted"].sum().sort_index()
    st.plotly_chart(monthly_bar(monthly.index, monthly.values, symbol, theme),
                    config={"displayModeBar": False})

st.write("")

# ---- Recent transactions (themed HTML table) ----
st.markdown("<div class='panel-title'>Recent transactions</div>"
            "<div class='panel-sub'>Amounts are shown in the currency they were entered in</div>",
            unsafe_allow_html=True)
recent = view.sort_values("Date", ascending=False).head(100)
rows = []
for _, r in recent.iterrows():
    date_txt = r.Date.strftime("%d %b %Y") if pd.notna(r.Date) else "-"
    emoji = CATEGORIES.get(r.Category, "✨")
    rows.append(
        f"<tr><td>{date_txt}</td>"
        f"<td><span class='pill'>{emoji} {html.escape(str(r.Category))}</span></td>"
        f"<td>{html.escape(str(r.Description))}</td>"
        f"<td>{html.escape(str(r.Payment))}</td>"
        f"<td class='amt'>{fmt(r.Amount, r.Currency)}</td></tr>"
    )
table_html = (
    "<div class='table-wrap'><table><thead><tr><th>Date</th><th>Category</th><th>Description</th>"
    "<th>Payment</th><th style='text-align:right'>Amount</th></tr></thead><tbody>"
    + "".join(rows) + "</tbody></table></div>"
)
st.markdown(table_html, unsafe_allow_html=True)

st.write("")

# ---- Manage data ----
with st.expander("🗑️ Delete an entry"):
    options = {
        f"{(r.Date.strftime('%d %b %Y') if pd.notna(r.Date) else '-')} | {r.Category} | "
        f"{r.Description} | {fmt(r.Amount, r.Currency)}": i
        for i, r in df.iterrows()
    }
    choice = st.selectbox("Pick entry", list(options.keys()))
    if st.button("Delete selected"):
        delete_expense(options[choice])
        st.rerun()

st.download_button(
    "⬇️ Download all data (CSV)",
    df[COLUMNS].to_csv(index=False),
    file_name="expenses.csv",
    mime="text/csv",
)
