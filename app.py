import streamlit as st
import pandas as pd
import joblib

model = joblib.load("jewelry_model.pkl")

st.title("AI Gold & Silver Jewelry Price Calculator")

purity = st.number_input("Purity (18/22/24)")
weight = st.number_input("Weight (grams)")
rate = st.number_input("Metal Rate")
making = st.number_input("Making Charge %")
wastage = st.number_input("Wastage %")
stone_price = st.number_input("Stone Price")

if st.button("Calculate Price"):

    input_data = pd.DataFrame({
        "purity":[purity],
        "weight":[weight],
        "rate":[rate],
        "making":[making],
        "wastage":[wastage],
        "stone_price":[stone_price]
    })

    prediction = model.predict(input_data)

    st.success(f"Predicted Price: ₹{prediction[0]:.2f}")