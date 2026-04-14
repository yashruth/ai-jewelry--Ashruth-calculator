import streamlit as st
import pandas as pd
import requests
import os
import random
from datetime import datetime
from fpdf import FPDF

st.title("Jewelry Billing System")

# ---------------- LIVE METAL RATES ---------------- #

def get_live_rates():

    try:

        url = "https://api.metals.live/v1/spot"

        r = requests.get(url, timeout=10)

        data = r.json()

        gold_oz = data[0]["gold"]
        silver_oz = data[1]["silver"]

        gold = gold_oz / 31.1035
        silver = silver_oz / 31.1035

        return round(gold,2), round(silver,2)

    except:

        return None, None


gold_rate, silver_rate = get_live_rates()

st.subheader("Live Metal Market Rates")

if gold_rate and silver_rate:

    st.success(f"24K Gold Price: ₹{gold_rate} / gram")
    st.success(f"Silver Price: ₹{silver_rate} / gram")

else:

    st.error("Unable to fetch live metal rates")


# ---------------- SHOP DETAILS ---------------- #

shop_name = st.text_input("Shop Name","Ashruth Jewelry Shop")

customer = st.text_input("Customer Name")

st.subheader("Jewelry Details")

item = st.selectbox("Item",["Gold","Silver"])

weight = st.number_input("Weight (grams)",min_value=0.0)


# ---------------- PURITY ---------------- #

if item == "Gold" and gold_rate:

    purity = st.selectbox("Gold Purity",["24K","22K","18K","14K"])

    purity_values = {
        "24K":1.0,
        "22K":0.916,
        "18K":0.75,
        "14K":0.585
    }

    rate = gold_rate * purity_values[purity]

    st.write(f"{purity} Gold Rate: ₹{round(rate,2)} / gram")

elif item == "Silver" and silver_rate:

    rate = silver_rate

else:

    rate = 0


making = st.number_input("Making Charge %")

wastage = st.number_input("Wastage %")

stone_price = st.number_input("Stone Price")


# ---------------- BILL GENERATION ---------------- #

if st.button("Generate Bill") and rate > 0:

    metal_value = weight * rate

    making_charge = metal_value * making / 100

    wastage_charge = metal_value * wastage / 100

    subtotal = metal_value + making_charge + wastage_charge + stone_price

    gst = subtotal * 0.03

    final_price = subtotal + gst

    st.success(f"Total Amount: ₹{round(final_price,2)}")

    invoice = "INV"+str(random.randint(1000,9999))

    date = datetime.now().strftime("%Y-%m-%d %H:%M")


    sale = {
        "Customer":customer,
        "Item":item,
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


    # PDF BILL

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
