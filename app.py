import streamlit as st
import pandas as pd
from datetime import date
from pathlib import Path

st.set_page_config(page_title="Expense Tracker", page_icon="💸", layout="wide")

COLUMNS = ["Date", "Category", "Description", "Amount", "Payment"]
CATEGORIES = ["Food", "Groceries", "Transport", "Rent", "Bills", "Shopping",
              "Health", "Entertainment", "Travel", "Education", "Other"]
PAYMENTS = ["UPI", "Cash", "Card", "Net Banking"]
CSV_PATH = Path("expenses.csv")


# ---------- Optional password (set app_password in secrets to enable) ----------
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


# ---------- Storage layer: Google Sheets if configured, else local CSV ----------
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
    if sheet.row_values(1) != COLUMNS:
        sheet.insert_row(COLUMNS, 1)
    return sheet


def load_data():
    if sheets_enabled():
        df = pd.DataFrame(get_sheet().get_all_records(), columns=COLUMNS)
    elif CSV_PATH.exists():
        df = pd.read_csv(CSV_PATH)
    else:
        df = pd.DataFrame(columns=COLUMNS)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
    return df.reset_index(drop=True)


def add_expense(d, category, description, amount, payment):
    row = [d.isoformat(), category, description, float(amount), payment]
    if sheets_enabled():
        get_sheet().append_row(row, value_input_option="USER_ENTERED")
    else:
        new = pd.DataFrame([row], columns=COLUMNS)
        new.to_csv(CSV_PATH, mode="a", header=not CSV_PATH.exists(), index=False)


def delete_expense(index):
    if sheets_enabled():
        get_sheet().delete_rows(index + 2)  # +1 header, +1 for 1-based rows
    else:
        df = pd.read_csv(CSV_PATH).drop(index=index)
        df.to_csv(CSV_PATH, index=False)


# ---------- UI ----------
st.title("💸 My Expense Tracker")

if not check_password():
    st.stop()

if not sheets_enabled():
    st.caption("⚠️ Using local CSV storage. On Streamlit Cloud this resets on restart — "
               "connect Google Sheets for permanent storage.")

with st.sidebar:
    st.header("Add expense")
    with st.form("add_form", clear_on_submit=True):
        d = st.date_input("Date", value=date.today())
        category = st.selectbox("Category", CATEGORIES)
        description = st.text_input("Description")
        amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0, format="%.2f")
        payment = st.selectbox("Payment method", PAYMENTS)
        submitted = st.form_submit_button("Add")
    if submitted:
        if amount <= 0:
            st.error("Enter an amount greater than 0")
        else:
            add_expense(d, category, description, amount, payment)
            st.success("Expense saved")
            st.rerun()

df = load_data()

if df.empty:
    st.info("No expenses yet. Add your first one from the sidebar.")
    st.stop()

df["Month"] = df["Date"].dt.strftime("%Y-%m")
months = ["All"] + sorted(df["Month"].dropna().unique(), reverse=True)
selected = st.selectbox("Filter by month", months)
view = df if selected == "All" else df[df["Month"] == selected]

c1, c2, c3 = st.columns(3)
c1.metric("Total spent", f"₹{view['Amount'].sum():,.2f}")
c2.metric("Transactions", len(view))
c3.metric("Average per transaction", f"₹{view['Amount'].mean():,.2f}" if len(view) else "₹0")

left, right = st.columns(2)
with left:
    st.subheader("By category")
    st.bar_chart(view.groupby("Category")["Amount"].sum())
with right:
    st.subheader("Monthly trend")
    st.line_chart(df.groupby("Month")["Amount"].sum())

st.subheader("All expenses")
st.dataframe(
    view.sort_values("Date", ascending=False).drop(columns=["Month"]),
    use_container_width=True,
)

with st.expander("Delete an entry"):
    options = {
        f"{r.Date:%d %b %Y} | {r.Category} | {r.Description} | ₹{r.Amount:,.2f}": i
        for i, r in df.iterrows()
    }
    choice = st.selectbox("Pick entry", list(options.keys()))
    if st.button("Delete selected"):
        delete_expense(options[choice])
        st.rerun()

st.download_button(
    "Download all data (CSV)",
    df.drop(columns=["Month"]).to_csv(index=False),
    file_name="expenses.csv",
    mime="text/csv",
)
