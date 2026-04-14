import streamlit as st
import pandas as pd
import os
import random
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

st.title("Jewelry Billing System")

# ---------- SESSION STATE FIX ---------- #

if "items" not in st.session_state:
    st.session_state["items"] = []

# ---------- CUSTOMER DETAILS ---------- #

shop_name = st.text_input("Shop Name","Ashruth Jewelry Shop")
customer = st.text_input("Customer Name")

st.subheader("Add Jewelry Item")

item = st.selectbox("Item",["Gold","Silver"])
weight = st.number_input("Weight (grams)",min_value=0.0)
base_rate = st.number_input("Today's Metal Rate per gram")

# ---------- PURITY ---------- #

if item == "Gold":

    purity = st.selectbox("Gold Purity",["24K","22K","20K","18K","14K"])

    purity_values = {
        "24K":1.0,
        "22K":0.916,
        "20K":0.833,
        "18K":0.75,
        "14K":0.585
    }

else:

    purity = st.selectbox("Silver Purity",["99%","92%","85%"])

    purity_values = {
        "99%":0.99,
        "92%":0.92,
        "85%":0.85
    }

rate = base_rate * purity_values[purity]

making = st.number_input("Making Charge %")
wastage = st.number_input("Wastage %")
stone_price = st.number_input("Stone Price")

# ---------- ADD ITEM ---------- #

if st.button("Add Item"):

    metal_value = weight * rate
    making_charge = metal_value * making / 100
    wastage_charge = metal_value * wastage / 100

    subtotal = metal_value + making_charge + wastage_charge + stone_price

    st.session_state["items"].append({
        "Item":item,
        "Purity":purity,
        "Weight":weight,
        "Rate":rate,
        "Amount":subtotal
    })

# ---------- ITEMS TABLE ---------- #

st.subheader("Items in Bill")

if len(st.session_state["items"]) > 0:

    df_items = pd.DataFrame(st.session_state["items"])
    st.dataframe(df_items)

# ---------- FINAL BILL ---------- #

if st.button("Generate Final Bill"):

    if len(st.session_state["items"]) == 0:

        st.warning("Add items first")

    else:

        df = pd.DataFrame(st.session_state["items"])

        subtotal = df["Amount"].sum()
        gst = subtotal * 0.03
        final_price = subtotal + gst

        st.success(f"Total Bill Amount: ₹{round(final_price,2)}")

        invoice = "INV"+str(random.randint(1000,9999))
        date = datetime.now().strftime("%Y-%m-%d")

        sale = {
            "Customer":customer,
            "Total":final_price,
            "Date":date
        }

        df_sale = pd.DataFrame([sale])

        if os.path.exists("sales.csv"):
            df_sale.to_csv("sales.csv",mode="a",header=False,index=False)
        else:
            df_sale.to_csv("sales.csv",index=False)

        # ---------- PDF BILL ---------- #

        pdf = FPDF()
        pdf.add_page()

        pdf.set_font("Arial","B",16)
        pdf.cell(190,10,shop_name,ln=True,align="C")

        pdf.set_font("Arial","",12)
        pdf.cell(95,8,"Invoice: "+invoice)
        pdf.cell(95,8,"Date: "+date,ln=True)

        pdf.cell(95,8,"Customer: "+customer,ln=True)

        pdf.ln(5)

        pdf.cell(40,8,"Item",1)
        pdf.cell(40,8,"Purity",1)
        pdf.cell(40,8,"Weight",1)
        pdf.cell(40,8,"Amount",1,ln=True)

        for i in st.session_state["items"]:

            pdf.cell(40,8,str(i["Item"]),1)
            pdf.cell(40,8,str(i["Purity"]),1)
            pdf.cell(40,8,str(i["Weight"]),1)
            pdf.cell(40,8,str(round(i["Amount"],2)),1,ln=True)

        pdf.cell(120,8,"Subtotal",1)
        pdf.cell(40,8,str(round(subtotal,2)),1,ln=True)

        pdf.cell(120,8,"GST 3%",1)
        pdf.cell(40,8,str(round(gst,2)),1,ln=True)

        pdf.cell(120,10,"Total Amount",1)
        pdf.cell(40,10,str(round(final_price,2)),1,ln=True)

        pdf.output("bill.pdf")

        with open("bill.pdf","rb") as f:
            st.download_button("Download Bill",f,"bill.pdf")

        st.session_state["items"] = []

# ---------- SALES HISTORY ---------- #

st.subheader("Sales History")

if os.path.exists("sales.csv"):

    sales = pd.read_csv("sales.csv").reset_index(drop=True)

    st.dataframe(sales)

    # ---------- DELETE SALE ---------- #

    st.subheader("Delete Sale Entry")

    if len(sales) > 0:

        selected_row = st.selectbox(
            "Select sale to delete",
            sales.index,
            format_func=lambda x: f"{sales.iloc[x]['Customer']} | ₹{round(sales.iloc[x]['Total'],2)} | {sales.iloc[x]['Date']}"
        )

        if st.button("Delete Selected Sale"):

            sales = sales.drop(index=selected_row)
            sales = sales.reset_index(drop=True)

            sales.to_csv("sales.csv",index=False)

            st.success("Sale deleted successfully")

            st.rerun()

    # ---------- 30 DAY GRAPH ---------- #

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

    # ---------- DASHBOARD ---------- #

    st.subheader("Sales Dashboard")

    total_sales = sales["Total"].sum()
    total_orders = len(sales)

    st.metric("Total Revenue", f"₹{round(total_sales,2)}")
    st.metric("Total Orders", total_orders)

else:

    st.info("No sales recorded yet.")

        
    
