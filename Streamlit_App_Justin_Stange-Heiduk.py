"""
Studienarbeit
Name: Justin Stange-Heiduk
Matrikelnummer: 8149363
Modul: DBDA64
Datum: 14.10.2024
"""

import streamlit as st
from PIL import Image
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient

# Azure Form Recognizer API endpoint and key
form_recognizer_endpoint = "https://akaddi.cognitiveservices.azure.com/"
subscription_key = "59436e6182b64a3daa38e61aa5ece03e"

class AzureFormRecognizerClient:
    def __init__(self, form_recognizer_endpoint: str, form_recognizer_key: str)-> None:
        """
        This function initializes the Azure Form Recognizer client.

        Input:
        form_recognizer_endpoint: The endpoint of the Azure Form Recognizer API.
        form_recognizer_key: The subscription key for the Azure Form Recognizer API.
        """

        self.form_recognizer_endpoint = form_recognizer_endpoint
        self.form_recognizer_key = form_recognizer_key

    def analyze_receipt(self, document: bytes) -> dict:
        """
        This function analyzes the picture of a receipt using the Azure Form Recognizer API.

        Input:
        document: The picture to analyze (in bytes).

        Output:
        The analysis of the text in the receipt (as a dictionary).
        """

        # Create a client for the Azure Form Recognizer API
        document_analysis_client = DocumentAnalysisClient(
            endpoint=self.form_recognizer_endpoint, credential=AzureKeyCredential(self.form_recognizer_key)
        )
        
        # Analyze the document using the prebuilt receipt model
        poller = document_analysis_client.begin_analyze_document("prebuilt-receipt", document)
        # Wait for the analysis to complete
        result = poller.result()

        # Extract the information from the analysis result
        page_values = []
        for idx, receipt in enumerate(result.documents):
            value = {}
            receipt_type = receipt.doc_type
            # Check if the receipt type is available
            value['ReceiptType'] = receipt_type if receipt_type else ""
            # Extract the fields from the receipt
            merchant_name = receipt.fields.get("MerchantName")
            value['MerchantName'] = merchant_name.value if merchant_name else ""
            
            transaction_date = receipt.fields.get("TransactionDate")
            value['TransactionDate'] = transaction_date.value if transaction_date else ""
            
            # Extract the items from the receipt
            value['Items'] = []
            items = receipt.fields.get("Items")
            if items:
                for idx, item in enumerate(items.value):
                    row = {}
                    item_description = item.value.get("Description")
                    row['Description'] = item_description.value if item_description else ""
                    
                    item_quantity = item.value.get("Quantity")
                    row['Quantity'] = item_quantity.value if item_quantity else ""

                    quantity_unit = item.value.get("QuantityUnit")
                    row['QuantityUnit'] = quantity_unit.value if quantity_unit else ""
                    
                    item_price = item.value.get("Price")
                    row['Price'] = item_price.value if item_price else ""
                    
                    item_total_price = item.value.get("TotalPrice")
                    row['TotalPrice'] = item_total_price.value if item_total_price else ""
                    
                    value['Items'].append(row)

            subtotal = receipt.fields.get("Subtotal")
            value['Subtotal'] = subtotal.value if subtotal else ""
            
            tax = receipt.fields.get("TotalTax")
            value['TotalTax'] = tax.value if tax else ""
            
            tip = receipt.fields.get("Tip")
            value['Tip'] = tip.value if tip else ""
            
            total = receipt.fields.get("Total")
            value['Total'] = total.value if total else ""

            page_values.append(value)

        return page_values

def display_receipt_info(receipt_info: dict) -> None:
    """
    This function displays the receipt information in a structured format.

    Input:
    receipt_info: The analysis result from the Azure Form Recognizer API (as a dictionary).
    """
    st.subheader("Ergebnis")
    for receipt in receipt_info:
        st.write(f"**Receipt Type:** {receipt['ReceiptType']}")
        st.write(f"**Merchant Name:** {receipt['MerchantName']}")
        st.write(f"**Transaction Date:** {receipt['TransactionDate']}")
        st.write("**Items:**")
        for item in receipt['Items']:
            st.write(f"  - Description: {item['Description']}")
            st.write(f"    Quantity: {item['Quantity']}")
            st.write(f"    Quantity Unit: {item['QuantityUnit']}")
            st.write(f"    Price: {item['Price']}")
            st.write(f"    Total Price: {item['TotalPrice']}")
        st.write(f"**Subtotal:** {receipt['Subtotal']}")
        st.write(f"**Total Tax:** {receipt['TotalTax']}")
        st.write(f"**Tip:** {receipt['Tip']}")
        st.write(f"**Total:** {receipt['Total']}")
        st.write("---")

st.title("Receipt Analyzer")

# Image upload
uploaded_image = st.file_uploader("Upload a receipt image", type=["jpg", "jpeg", "png"])

# Initialize a variable to store the image
image = None

# Button to activate the camera
if st.button("Take a photo with your camera"):
    captured_image = st.camera_input("Capture a photo")
    if captured_image:
        image = captured_image.getvalue()
        st.image(image, caption="Captured Image", use_column_width=True)

if uploaded_image:
    image = uploaded_image.read()
    st.image(image, caption="Uploaded Image", use_column_width=True)

# Add a button to analyze the image
if image:
    if st.button("Analyse the receipt"):
        with st.spinner("Analyzing the receipt..."):
            try:
                client = AzureFormRecognizerClient(form_recognizer_endpoint, subscription_key)
                receipt_info = client.analyze_receipt(image)
                display_receipt_info(receipt_info)  # Display the structured receipt information
            except Exception as e:
                st.error(f"An error occurred: {e}")
else:
    st.write("Please upload an image or capture a photo to analyze the receipt.")