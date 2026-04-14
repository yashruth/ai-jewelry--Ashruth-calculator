import streamlit as st
import pandas as pd
import requests
import os
import random
import numpy as np

from datetime import datetime
from fpdf import FPDF
from sklearn.linear_model import LinearRegression
import plotly.express as px


st.title("AI Jewelry Billing & Market Analytics System")


# ---------------- LIVE METAL RATES (SAFE) ---------------- #

def get_live_rates():

    try:

        url = "https://api.metals.live/v1/spot"

        response = requests.get(url, timeout=10)

        data = response.json()

        gold_oz = data[0]["gold"]
        silver_oz = data[1]["silver"]

        gold_price = gold_oz / 31.1035
        silver_price = silver_oz / 31.1035

        return round(gold_price,2), round(silver_price,2)

    except:

        return None, None


gold_rate, silver_rate = get_live_rates()

st.subheader("Live Metal Market Rates")

if gold_rate is None or silver_rate is None:

    st.warning("Unable to fetch market rates. Using default values.")

    gold_rate = 7200
    silver_rate = 90

st.success(f"Gold Price per gram: ₹{gold_rate}")
st.success(f"Silver Price per gram: ₹{silver_rate}")


# ---------------- STORE DAILY METAL PRICE ---------------- #

today = datetime.now().strftime("%Y-%m-%d")

price_data = {
    "Date":today,
    "Gold":gold_rate,
    "Silver":silver_rate
}

df_price = pd.DataFrame([price_data])

if os.path.exists("metal_prices.csv"):

    old = pd.read_csv("metal_prices.csv")

    if today not in old["Date"].values:

        df_price.to_csv("metal_prices.csv",mode="a",header=False,index=False)

else:

    df_price.to_csv("metal_prices.csv",index=False)


# ---------------- SHOP DETAILS ---------------- #

shop_name = st.text_input("Shop Name","Ashruth Jewelry Shop")

customer = st.text_input("Customer Name")

st.subheader("Jewelry Details")

item = st.selectbox("Item",["Gold","Silver"])

weight = st.number_input("Weight (grams)",min_value=0.0)

if item == "Gold":
    rate = st.number_input("Rate per gram",value=float(gold_rate))

else:
    rate = st.number_input("Rate per gram",value=float(silver_rate))

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

    date = datetime.now().strftime("%Y-%m-%d %H:%M")


    # SAVE SALES

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
    pdf.cell(40,8,str(rate),1)
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


# ---------------- SALES DASHBOARD ---------------- #

st.subheader("Sales Dashboard")

if os.path.exists("sales.csv"):

    sales = pd.read_csv("sales.csv")

    total_sales = sales["Total"].sum()

    total_orders = len(sales)

    st.metric("Total Orders",total_orders)

    st.metric("Total Revenue",round(total_sales,2))

    item_sales = sales.groupby("Item")["Total"].sum().reset_index()

    fig = px.pie(item_sales,names="Item",values="Total")

    st.plotly_chart(fig)


# ---------------- AI PRICE PREDICTION ---------------- #

st.subheader("AI Metal Price Prediction")

if os.path.exists("metal_prices.csv"):

    data = pd.read_csv("metal_prices.csv")

    if len(data) > 3:

        X = np.arange(len(data)).reshape(-1,1)

        gold_model = LinearRegression()

        silver_model = LinearRegression()

        gold_model.fit(X,data["Gold"])

        silver_model.fit(X,data["Silver"])

        next_day = np.array([[len(data)]])

        pred_gold = gold_model.predict(next_day)[0]

        pred_silver = silver_model.predict(next_day)[0]

        st.write("Predicted Gold Tomorrow:",round(pred_gold,2))
        st.write("Predicted Silver Tomorrow:",round(pred_silver,2))

        today_gold = data.iloc[-1]["Gold"]

        if pred_gold > today_gold:

            st.success("AI Market Direction: Gold likely UP")

        else:

            st.error("AI Market Direction: Gold likely DOWN")

    else:

        st.write("Collecting data for prediction...")


# ---------------- 30 DAY TREND ---------------- #

st.subheader("30 Day Metal Price Trend")

if os.path.exists("metal_prices.csv"):

    df = pd.read_csv("metal_prices.csv")

    df["Date"] = pd.to_datetime(df["Date"])

    last_30 = df.tail(30)

    fig = px.line(last_30,x="Date",y=["Gold","Silver"])

    st.plotly_chart(fig)
