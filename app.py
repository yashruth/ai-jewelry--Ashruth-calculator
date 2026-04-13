import streamlit as st
from fpdf import FPDF
import pandas as pd
from datetime import datetime
from io import BytesIO
import random
st.title("Jewelry Shop Billing System")
# Shop details
shop_name = st.text_input("Shop Name","Ashruth Jewelry Shop")
shop_phone = st.text_input("Shop Phone","9876543210")
shop_address = st.text_input("Shop Address","Your City")
st.subheader("Customer Details")
customer = st.text_input("Customer Name")
st.subheader("Jewelry Details")
item = st.selectbox("Item",["Gold","Silver"])
purity = st.number_input("Purity")
weight = st.number_input("Weight (grams)")
rate = st.number_input("Rate per gram")
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
    st.success(f"Total Amount: Rs {final_price:.2f}")
    invoice_no = "INV"+str(random.randint(1000,9999))
    date = datetime.now().strftime("%d-%m-%Y")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial","B",16)
    pdf.cell(190,10,shop_name,ln=True,align="C")
    pdf.set_font("Arial","",10)
    pdf.cell(190,6,shop_address,ln=True,align="C")
    pdf.cell(190,6,"Phone: "+shop_phone,ln=True,align="C")
    pdf.ln(5)
    pdf.set_font("Arial","B",11)
    pdf.cell(95,8,"Invoice No: "+invoice_no)
    pdf.cell(95,8,"Date: "+date,ln=True)
    pdf.cell(95,8,"Customer: "+customer)
    pdf.cell(95,8,"Item: "+item,ln=True)
    pdf.ln(5)
    pdf.set_font("Arial","B",11)
    pdf.cell(40,8,"Purity",1)
    pdf.cell(40,8,"Weight",1)
    pdf.cell(40,8,"Rate",1)
    pdf.cell(40,8,"Amount",1,ln=True)
    pdf.set_font("Arial","",11)
    pdf.cell(40,8,str(purity),1)
    pdf.cell(40,8,str(weight),1)
    pdf.cell(40,8,str(rate),1)
    pdf.cell(40,8,str(round(metal_value,2)),1,ln=True)
    pdf.ln(3)
    pdf.cell(150,8,"Making Charge",1)
    pdf.cell(40,8,str(round(making_charge,2)),1,ln=True)
    pdf.cell(150,8,"Wastage Charge",1)
    pdf.cell(40,8,str(round(wastage_charge,2)),1,ln=True)
    pdf.cell(150,8,"GST 3%",1)
    pdf.cell(40,8,str(round(gst,2)),1,ln=True)
    pdf.set_font("Arial","B",12)
    pdf.cell(150,10,"Total Amount",1)
    pdf.cell(40,10,str(round(final_price,2)),1,ln=True)
    pdf_bytes = pdf.output(dest="S").encode("latin1")
    st.download_button(
        label="Download PDF Bill",
        data=pdf_bytes,
        file_name="jewelry_invoice.pdf",
        mime="application/pdf"
    )

    data = {
        "Customer":[customer],
        "Item":[item],
        "Purity":[purity],
        "Weight":[weight],
        "Rate":[rate],
        "Metal Value":[metal_value],
        "Making Charge":[making_charge],
        "Wastage":[wastage_charge],
        "GST":[gst],
        "Total":[final_price]
    }

    df = pd.DataFrame(data)
    excel_file = BytesIO()
    with pd.ExcelWriter(excel_file, engine="openpyxl") as writer:
        df.to_excel(writer,index=False,startrow=4)
        sheet = writer.sheets["Sheet1"]
        sheet["A1"] = shop_name
        sheet["A2"] = "Invoice No: "+invoice_no
        sheet["A3"] = "Customer: "+customer
        sheet["D2"] = "Date: "+date
    excel_file.seek(0)
    st.download_button(
        label="Download Excel Bill",
        data=excel_file,
        file_name="jewelry_invoice.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
