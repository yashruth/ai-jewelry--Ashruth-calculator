import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
from fpdf import FPDF

st.set_page_config(page_title="Silver Shop ERP", layout="wide")
st.title("Silver Shop ERP System")

# ---------- FILES ----------
SALES_FILE = "sales.csv"
STOCK_FILE = "stock.csv"

# ---------- HELPERS ----------
def ensure_sales_file():
    cols = ["date", "customer", "weight", "sale"]
    if not os.path.exists(SALES_FILE):
        pd.DataFrame(columns=cols).to_csv(SALES_FILE, index=False)
    else:
        df = pd.read_csv(SALES_FILE)
        for c in cols:
            if c not in df.columns:
                df[c] = 0 if c == "sale" else ""
        df = df[cols]
        df.to_csv(SALES_FILE, index=False)

def ensure_stock_file():
    if not os.path.exists(STOCK_FILE):
        pd.DataFrame(columns=["stock"]).to_csv(STOCK_FILE, index=False)

def get_total_stock():
    ensure_stock_file()
    df = pd.read_csv(STOCK_FILE)
    if "stock" not in df.columns or df.empty:
        return 0.0
    return float(df["stock"].sum())

def add_stock(amount):
    ensure_stock_file()
    pd.DataFrame([{"stock": amount}]).to_csv(
        STOCK_FILE, mode="a", header=False, index=False
    )

def set_stock(new_total):
    pd.DataFrame([{"stock": new_total}]).to_csv(STOCK_FILE, index=False)

def load_sales():
    ensure_sales_file()
    return pd.read_csv(SALES_FILE)

def save_sales(df):
    df.to_csv(SALES_FILE, index=False)

# ---------- LOGIN ----------
users = {"admin": "1234", "staff": "1111"}

st.sidebar.header("Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if username not in users or users[username] != password:
    st.warning("Enter valid login in sidebar")
    st.stop()

st.sidebar.success(f"Welcome {username}")

# ---------- RATE SETTINGS ----------
st.header("Silver Rate Settings")

silver_rate = st.number_input(
    "Silver Rate per KG (₹)",
    min_value=0.0,
    step=100.0
)

making_percent = st.number_input(
    "Making Charges (%)",
    min_value=0.0,
    step=1.0
)

wastage_percent = st.number_input(
    "Wastage (%)",
    min_value=0.0,
    step=1.0
)

silver_per_gram = 0.0
making_amount = 0.0
wastage_amount = 0.0
final_gram_rate = 0.0

if silver_rate > 0:

    silver_per_gram = silver_rate / 1000

    making_amount = silver_per_gram * (making_percent / 100)

    wastage_amount = silver_per_gram * (wastage_percent / 100)

    final_gram_rate = (
        silver_per_gram +
        making_amount +
        wastage_amount
    )

    st.success(f"Silver Rate per gram ₹{silver_per_gram:.2f}")

    st.info(f"Making Charges Added ₹{making_amount:.2f}")

    st.info(f"Wastage Added ₹{wastage_amount:.2f}")

    st.success(f"Final Selling Rate per gram ₹{final_gram_rate:.2f}")

# ---------- INVENTORY ----------
st.header("Inventory")

colA, colB = st.columns(2)

with colA:
    add_amt = st.number_input(
        "Add Stock (grams)",
        min_value=0.0,
        step=1.0
    )

    if st.button("Add Stock"):
        add_stock(add_amt)
        st.success("Stock added successfully")

with colB:
    total_stock = get_total_stock()
    st.metric("Available Stock (g)", f"{total_stock:.2f}")

# ---------- CALCULATOR ----------
st.header("Silver Calculator")

btn_cols = st.columns(5)

quick_weights = [1, 2, 5, 10, 100]

for i, w in enumerate(quick_weights):

    if btn_cols[i].button(f"{w} g") and final_gram_rate > 0:

        total_price = w * final_gram_rate

        st.success(f"{w} g = ₹{total_price:.2f}")

weight = st.number_input(
    "Custom Weight (grams)",
    min_value=0.0,
    step=0.1
)

price = 0.0

if weight > 0 and final_gram_rate > 0:

    silver_total = weight * silver_per_gram

    making_total = weight * making_amount

    wastage_total = weight * wastage_amount

    price = weight * final_gram_rate

    st.subheader("Calculation Result")

    st.write(f"Silver Value : ₹{silver_total:.2f}")

    st.write(f"Making Charges : ₹{making_total:.2f}")

    st.write(f"Wastage Charges : ₹{wastage_total:.2f}")

    st.success(f"Final Total Amount : ₹{price:.2f}")

# ---------- RECORD SALE ----------
st.header("Record Sale")

customer = st.text_input("Customer Name")

phone = st.text_input("Customer WhatsApp Number (optional)")

if st.button("Save Sale"):

    if weight <= 0 or final_gram_rate <= 0:

        st.error("Enter valid silver rate and weight")

    else:

        total_stock = get_total_stock()

        if weight > total_stock:

            st.error("Not enough stock")

        else:

            sale_row = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "customer": customer,
                "weight": weight,
                "sale": price,
            }

            df = load_sales()

            df = pd.concat(
                [df, pd.DataFrame([sale_row])],
                ignore_index=True
            )

            save_sales(df)

            # update stock
            set_stock(total_stock - weight)

            st.success("Sale saved successfully")

            # ---------- PDF BILL ----------
            pdf = FPDF()

            pdf.add_page()

            pdf.set_font("Arial", "B", 16)

            pdf.cell(200, 10, "Silver Shop Bill", ln=True)

            pdf.set_font("Arial", "", 12)

            pdf.cell(200, 10, f"Customer: {customer}", ln=True)

            pdf.cell(200, 10, f"Weight: {weight} g", ln=True)

            pdf.cell(200, 10, f"Silver Amount: ₹{silver_total:.2f}", ln=True)

            pdf.cell(200, 10, f"Making Charges: ₹{making_total:.2f}", ln=True)

            pdf.cell(200, 10, f"Wastage Charges: ₹{wastage_total:.2f}", ln=True)

            pdf.cell(200, 10, f"Final Amount: ₹{price:.2f}", ln=True)

            pdf.output("bill.pdf")

            with open("bill.pdf", "rb") as f:

                st.download_button(
                    "Download Bill",
                    f,
                    "bill.pdf"
                )

            if phone:

                link = (
                    f"https://wa.me/{phone}"
                    f"?text=Your silver bill amount is ₹{price:.2f}"
                )

                st.link_button("Send WhatsApp Bill", link)

# ---------- DASHBOARD ----------
st.header("Sales Dashboard")

sales = load_sales()

if not sales.empty:

    total_sales = sales["sale"].astype(float).sum()

    avg_sale = sales["sale"].astype(float).mean()

    c1, c2 = st.columns(2)

    c1.metric("Total Sales", f"₹{total_sales:.2f}")

    c2.metric("Average Sale", f"₹{avg_sale:.2f}")

    st.subheader("Sales History")

    st.dataframe(sales)

    # ---------- DELETE SALE ----------
    st.subheader("Delete Sale")

    idx = st.number_input(
        "Row number",
        min_value=0,
        step=1
    )

    if st.button("Delete Sale"):

        if idx < len(sales):

            sales = sales.drop(idx).reset_index(drop=True)

            save_sales(sales)

            st.success("Sale deleted successfully")

        else:

            st.error("Invalid row index")

    # ---------- DAILY SALES CHART ----------
    st.subheader("Daily Sales Chart")

    sales["date"] = pd.to_datetime(
        sales["date"],
        errors="coerce"
    )

    daily = sales.groupby(
        "date",
        as_index=False
    )["sale"].sum()

    fig = px.line(
        daily,
        x="date",
        y="sale",
        markers=True,
        title="Daily Sales"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ---------- MONTHLY REPORT ----------
    st.subheader("Monthly Report")

    sales["month"] = sales["date"].dt.to_period("M").astype(str)

    monthly = sales.groupby("month")[["sale"]].sum().reset_index()

    st.dataframe(monthly)

    # ---------- CUSTOMER LEDGER ----------
    st.subheader("Customer Ledger")

    ledger = sales.groupby("customer")[["sale"]].sum().reset_index()

    st.dataframe(ledger)

    # ---------- DAILY CLOSING ----------
    st.subheader("Daily Closing Report")

    today = datetime.now().strftime("%Y-%m-%d")

    today_sales = sales[
        sales["date"].dt.strftime("%Y-%m-%d") == today
    ]

    st.metric(
        "Today's Sales",
        f"₹{today_sales['sale'].sum():.2f}"
    )

    # ---------- EXPORT EXCEL ----------
    st.subheader("Export Sales Report")

    excel_path = "report.xlsx"

    sales.to_excel(excel_path, index=False)

    with open(excel_path, "rb") as f:

        st.download_button(
            "Download Excel Report",
            f,
            "report.xlsx"
        )

else:

    st.info("No sales recorded yet.")
