import streamlit as st
from fpdf import FPDF
st.title("Gold & Silver Jewelry Price Calculator")
customer = st.text_input("Customer Name")
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
    gst = subtotal * 0.03
    final_price = subtotal + gst
    st.success(f"Final Jewelry Price: Rs. {final_price:.2f}")
    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200,10,"Jewelry Shop Bill",ln=True,align="C")
    pdf.cell(200,10,"Customer: " + str(customer),ln=True)
    pdf.cell(200,10,"Purity: " + str(purity),ln=True)
    pdf.cell(200,10,"Weight: " + str(weight) + " g",ln=True)
    pdf.cell(200,10,"Metal Rate: Rs. " + str(rate),ln=True)
    pdf.cell(200,10,"Making Charge: " + str(making) + " %",ln=True)
    pdf.cell(200,10,"Wastage: " + str(wastage) + " %",ln=True)
    pdf.cell(200,10,"Stone Price: Rs. " + str(stone_price),ln=True)
    pdf.cell(200,10,"GST (3%): Rs. " + str(round(gst,2)),ln=True)
    pdf.cell(200,10,"Total Price: Rs. " + str(round(final_price,2)),ln=True)
    # Convert PDF to bytes
    pdf_bytes = pdf.output(dest="S").encode("latin1")
    st.download_button(
        label="Download Bill",
        data=pdf_bytes,
        file_name="jewelry_bill.pdf",
        mime="application/pdf"
    )
