import streamlit as st
import pandas as pd
import os
import random
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

st.title("Jewelry Billing System")

# ---------------- SHOP DETAILS ---------------- #

shop_name = st.text_input("Shop Name","Ashruth Jewelry Shop")
customer = st.text_input("Customer Name")

st.subheader("Jewelry Details")

item = st.selectbox("Item",["Gold","Silver"])
weight = st.number_input("Weight (grams)",min_value=0.0)

base_rate = st.number_input("Today's Metal Rate per gram")

# ---------------- PURITY ---------------- #

if item == "Gold":

    purity = st.selectbox("Gold Purity",["24K","22K","20K","18K","14K"])

    purity_values = {
        "24K":1.0,
        "22K":0.916,
        "20K":0.833,
        "18K":0.75,
        "14K":0.585
    }

    rate = base_rate * purity_values[purity]

    st.write(f"{purity} Gold Rate: ₹{round(rate,2)} / gram")

else:

    purity = st.selectbox("Silver Purity",["99%","92%","85%"])

    purity_values = {
        "99%":0.99,
        "92%":0.92,
        "85%":0.85
    }

    rate = base_rate * purity_values[purity]

    st.write(f"{purity} Silver Rate: ₹{round(rate,2)} / gram")

making = st.number_input("Making Charge %")
wastage = st.number_input("Wastage %")
stone_price = st.number_input("Stone Price")

# ---------------- BILL GENERATION ---------------- #

if st.button("Generate Bill"):

    metal_value = weight * rate
    making_charge = metal_value * making / 100
    wastage_charge = metal_value * wastage / 100

    subtotal = metal_value + making_charge + wastage_charge + stone_price
    gst = subtotal * 0.03
    final_price = subtotal + gst

    st.success(f"Total Amount: ₹{round(final_price,2)}")

    invoice = "INV"+str(random.randint(1000,9999))
    date = datetime.now().strftime("%Y-%m-%d")

    sale = {
        "Customer":customer,
        "Item":item,
        "Purity":purity,
        "Weight":weight,
        "Rate":rate,
        "Total":final_price,
        "Date":date
    }

    df_sale = pd.DataFrame([sale])

    if os.path.exists("sales.csv"):
        df_sale.to_csv("sales.csv",mode="a",header=False,index=False)
    else:
        df_sale.to_csv("sales.csv",index=False)

    # ---------------- PDF BILL ---------------- #

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial","B",16)
    pdf.cell(190,10,shop_name,ln=True,align="C")

    pdf.set_font("Arial","",12)
    pdf.cell(95,8,"Invoice: "+invoice)
    pdf.cell(95,8,"Date: "+date,ln=True)

    pdf.cell(95,8,"Customer: "+customer,ln=True)

    pdf.ln(5)

    pdf.cell(40,8,"Weight",1)
    pdf.cell(40,8,"Rate",1)
    pdf.cell(40,8,"Amount",1,ln=True)

    pdf.cell(40,8,str(weight),1)
    pdf.cell(40,8,str(round(rate,2)),1)
    pdf.cell(40,8,str(round(metal_value,2)),1,ln=True)

    pdf.cell(150,8,"Making Charge",1)
    pdf.cell(40,8,str(round(making_charge,2)),1,ln=True)

    pdf.cell(150,8,"Wastage",1)
    pdf.cell(40,8,str(round(wastage_charge,2)),1,ln=True)

    pdf.cell(150,8,"GST 3%",1)
    pdf.cell(40,8,str(round(gst,2)),1,ln=True)

    pdf.set_font("Arial","B",12)
    pdf.cell(150,10,"Total Amount",1)
    pdf.cell(40,10,str(round(final_price,2)),1,ln=True)

    pdf.output("bill.pdf")

    with open("bill.pdf","rb") as f:
        st.download_button("Download Bill",f,"bill.pdf")

# ---------------- SALES HISTORY ---------------- #

st.subheader("Sales History")

if os.path.exists("sales.csv"):

    sales = pd.read_csv("sales.csv")

    st.dataframe(sales)

    # ---------------- 30 DAY GRAPH ---------------- #

    st.subheader("Last 30 Days Sales Graph")

    sales["Date"] = pd.to_datetime(sales["Date"], errors="coerce")
    last_30 = sales.sort_values("Date").tail(30)

    fig = px.line(
        last_30,
        x="Date",
        y="Total",
        markers=True,
        title="Daily Sales (Last 30 Days)"
    )

    st.plotly_chart(fig)

    # ---------------- SALES DASHBOARD ---------------- #

    st.subheader("Sales Dashboard")

    total_sales = sales["Total"].sum()
    total_orders = len(sales)

    st.metric("Total Revenue", f"₹{round(total_sales,2)}")
    st.metric("Total Orders", total_orders)

    item_sales = sales.groupby("Item")["Total"].sum().reset_index()

    fig2 = px.pie(
        item_sales,
        names="Item",
        values="Total",
        title="Gold vs Silver Sales"
    )

    st.plotly_chart(fig2)
