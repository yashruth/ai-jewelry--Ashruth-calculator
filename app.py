import streamlit as st
st.title("Gold & Silver Jewelry Price Calculator")
purity = st.number_input("Purity (Example: 92.5 for silver, 22 for gold)")
weight = st.number_input("Weight (grams)")
rate = st.number_input("Metal Rate per gram")
making = st.number_input("Making Charge %")
wastage = st.number_input("Wastage %")
stone_price = st.number_input("Stone Price")
if st.button("Calculate Price"):
    metal_value = weight * rate
    making_charge = metal_value * making / 100
    wastage_charge = metal_value * wastage / 100
    subtotal = metal_value + making_charge + wastage_charge + stone_price
    gst = subtotal * 0.03   # 3% GST
    final_price = subtotal + gst
    st.success(f"Final Jewelry Price (including GST): ₹{final_price:.2f}")
