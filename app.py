import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
from fpdf import FPDF

st.set_page_config(page_title="Silver Shop ERP")

st.title("Silver Shop ERP System")

# ---------------- LOGIN ---------------- #

users = {
    "admin": "1234",
    "staff1": "1111",
    "staff2": "2222"
}

st.sidebar.header("Login")

username = st.sidebar.text_input("ashruth")
password = st.sidebar.text_input("12345", type="password")

if username not in users or users[username] != password:
    st.warning("Enter valid login in sidebar")
    st.stop()

st.sidebar.success(f"Welcome {username}")

# ---------------- RATE SETTINGS ---------------- #

st.header("Silver Rate Settings")

buy_rate = st.number_input("Buy Rate per KG (₹)", min_value=0.0)
sell_rate = st.number_input("Sell Rate per KG (₹)", min_value=0.0)

buy_gram = 0
sell_gram = 0
profit_per_gram = 0

if buy_rate > 0 and sell_rate > 0:

    buy_gram = buy_rate / 1000
    sell_gram = sell_rate / 1000
    profit_per_gram = sell_gram - buy_gram

    st.success(f"Sell per gram ₹{round(sell_gram,2)}")
    st.info(f"Profit per gram ₹{round(profit_per_gram,2)}")

# ---------------- INVENTORY ---------------- #

st.header("Inventory")

stock_file = "stock.csv"

add_stock = st.number_input("Add Stock (grams)", min_value=0.0)

if st.button("Add Stock"):

    df = pd.DataFrame([{"stock": add_stock}])

    if os.path.exists(stock_file):
        df.to_csv(stock_file, mode="a", header=False, index=False)
    else:
        df.to_csv(stock_file, index=False)

    st.success("Stock added")

total_stock = 0

if os.path.exists(stock_file):

    stock = pd.read_csv(stock_file)
    total_stock = stock["stock"].sum()

    st.metric("Available Stock (g)", round(total_stock,2))

# ---------------- CALCULATOR ---------------- #

st.header("Silver Calculator")

col1, col2, col3, col4, col5 = st.columns(5)

if sell_gram > 0:

    if col1.button("1g"):
        st.success(f"₹{round(1*sell_gram,2)}")

    if col2.button("2g"):
        st.success(f"₹{round(2*sell_gram,2)}")

    if col3.button("5g"):
        st.success(f"₹{round(5*sell_gram,2)}")

    if col4.button("10g"):
        st.success(f"₹{round(10*sell_gram,2)}")

    if col5.button("100g"):
        st.success(f"₹{round(100*sell_gram,2)}")

weight = st.number_input("Custom Weight (grams)", min_value=0.0)

price = 0
profit = 0

if weight > 0 and sell_gram > 0:

    price = weight * sell_gram
    profit = weight * profit_per_gram

    st.success(f"Customer Price ₹{round(price,2)}")
    st.info(f"Profit ₹{round(profit,2)}")

# ---------------- SALE ---------------- #

st.header("Record Sale")

customer = st.text_input("Customer Name")
phone = st.text_input("Customer WhatsApp Number")

if st.button("Save Sale"):

    if weight > 0 and weight <= total_stock:

        sale_data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "customer": customer,
            "weight": weight,
            "sale": price,
            "profit": profit
        }

        df = pd.DataFrame([sale_data])

        if os.path.exists("sales.csv"):
            df.to_csv("sales.csv", mode="a", header=False, index=False)
        else:
            df.to_csv("sales.csv", index=False)

        st.success("Sale saved")

        # reduce stock
        new_stock = total_stock - weight
        pd.DataFrame([{"stock": new_stock}]).to_csv(stock_file, index=False)

        # -------- PDF BILL -------- #

        pdf = FPDF()
        pdf.add_page()

        pdf.set_font("Arial","B",16)
        pdf.cell(200,10,"Silver Shop Bill",ln=True)

        pdf.set_font("Arial","",12)

        pdf.cell(200,10,f"Customer: {customer}",ln=True)
        pdf.cell(200,10,f"Weight: {weight} g",ln=True)
        pdf.cell(200,10,f"Amount: ₹{round(price,2)}",ln=True)

        pdf.output("bill.pdf")

        with open("bill.pdf","rb") as f:
            st.download_button("Download Bill",f,"bill.pdf")

        if phone:
            link = f"https://wa.me/{phone}?text=Your silver bill amount ₹{price}"
            st.link_button("Send WhatsApp Bill", link)

# ---------------- DASHBOARD ---------------- #

if os.path.exists("sales.csv"):

    st.header("Sales Dashboard")

    sales = pd.read_csv("sales.csv")

    total_sales = sales["sale"].sum()
    total_profit = sales["profit"].sum()
    avg_sale = sales["sale"].mean()

    col1,col2,col3 = st.columns(3)

    col1.metric("Total Sales",f"₹{round(total_sales,2)}")
    col2.metric("Total Profit",f"₹{round(total_profit,2)}")
    col3.metric("Average Sale",f"₹{round(avg_sale,2)}")

    st.subheader("Sales History")
    st.dataframe(sales)

    # delete sale
    st.subheader("Delete Sale")

    idx = st.number_input("Row number", min_value=0, step=1)

    if st.button("Delete"):

        if idx < len(sales):
            sales = sales.drop(idx)
            sales.to_csv("sales.csv", index=False)
            st.success("Sale deleted")

# ---------------- DAILY GRAPH ---------------- #

    sales["date"] = pd.to_datetime(sales["date"])

    daily = sales.groupby("date")["profit"].sum().reset_index()

    fig = px.line(daily, x="date", y="profit", markers=True, title="Daily Profit")

    st.plotly_chart(fig)

# ---------------- MONTHLY REPORT ---------------- #

    st.header("Monthly Report")

    sales["month"] = sales["date"].dt.to_period("M")

    monthly = sales.groupby("month")[["sale","profit"]].sum()

    st.dataframe(monthly)

# ---------------- CUSTOMER LEDGER ---------------- #

    st.header("Customer Ledger")

    ledger = sales.groupby("customer")[["sale","profit"]].sum()

    st.dataframe(ledger)
