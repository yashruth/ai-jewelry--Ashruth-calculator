import streamlit as st
from fpdf import FPDF
st.title("Jewelry Price Calculator")
customer = st.text_input("Customer Name")
purity = st.number_input("Purity")
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
    gst = subtotal * 0.03
    final_price = subtotal + gst
    st.success(f"Final Price: ₹{final_price:.2f}")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200,10,"Jewelry Shop Bill",ln=True,align="C")
    pdf.cell(200,10,f"Customer: {customer}",ln=True)
    pdf.cell(200,10,f"Weight: {weight} g",ln=True)
    pdf.cell(200,10,f"Rate: ₹{rate}",ln=True)
    pdf.cell(200,10,f"Final Price: ₹{final_price:.2f}",ln=True)
    pdf.output("bill.pdf")
    with open("bill.pdf","rb") as file:
        st.download_button("Download Bill",file,"bill.pdf")
