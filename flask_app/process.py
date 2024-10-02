import openai 
import re
import fitz  # PyMuPDF PDF READ
import os
import csv
import time
import json
import pandas as pd
# from langchain_community.llms import Ollama
from llama_index.core.bridge.pydantic import BaseModel
from llama_index.llms.ollama import Ollama
from pdf2image import convert_from_path
import pytesseract
from PIL import Image


CONVERTED_FOLDER =  'converted'

# load tesseract location into program. 
pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"


#PDF READ
def read_pdf(file_path):
    try:
        # Open the PDF
        doc = fitz.open(file_path)

        # Extract text from the first page
        first_page_text = doc[2].get_text()
       
        # Close the document
        doc.close()

        return  first_page_text # Return the first page
    except Exception as e:
        print("Error opening PDF: " + str(e) + file_path)
        return "Error opening PDF: " + str(e) + file_path
    
def read_png(file_path):
    print(file_path)
    try: 
        text = pytesseract.image_to_string(Image.open(file_path))
        return text
    except Exception as e:
        print("Error opening PNG: " + str(e) + file_path)
        return "Error opening PNG: " + str(e) + file_path
    


def extract_data_with_llama(textOfCV):
    llm = Ollama(model="llama3.1:latest", json_mode=True)
    prompt = ("Based on the following text, please collect the account owner's transaction data and format them in JSON format. The data must include date, description, and amount. If any data is not available, do not add the transaction. The text is:" +  textOfCV + " \n{ Date: <DATE>, Description: <DESCRIPTION>, Amount: <AMOUNT> } \n,{...},{...} The response contains only the JSON structure.")

    prompt = (
        "<|begin_of_text|><|start_header_id|>system<|end_header_id|>"
        "You are a bookkeeping assistant, please collect the account owner's transaction data and format them in JSON format."
        "The data must include date, description, and amount. If any data is not available, do not add the transaction."
        "Your response contains only the JSON structure."
        "<|eot_id|><|start_header_id|>user<|end_header_id|>"
        "12/06/23 BKOFAMERICA ATM 12/06 #000004881 DEPOSIT WESTVIEW BALTIMORE MD 100.00"
        "12/11/23 BKOFAMERICA ATM 12/09 #000005866 DEPOSIT WESTVIEW BALTIMORE MD 200.00"
        "12/29/23 BKOFAMERICA ATM 12/29 #000002272 DEPOSIT WESTVIEW  BALTIMORE MD 100.00"
        "<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
        "{transactions: [{date: 12/06/23, description: BKOFAMERICA ATM 12/06 #000004881 DEPOSIT WESTVIEW BALTIMORE MD, amount: 100.00 },"
        "{date: 12/06/23, description: BKOFAMERICA ATM 12/06 #000005866 DEPOSIT WESTVIEW BALTIMORE MD, amount: 200.00 },"
        "{date: 12/06/23, description: BKOFAMERICA ATM 12/06 #000002272 DEPOSIT WESTVIEW BALTIMORE MD, amount: 100.00 }, {...} ]}"
        "<|eot_id|><|start_header_id|>user<|end_header_id|>"
        "%s"
        "<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
        % textOfCV
    )
    result = llm.complete(prompt)
    #print(result)
    return result


def post_process(response_text):
    # Parse the response text into a dictionary
    data_dict = json.loads(response_text)

    # Define the desired keys and their default values
    keys = ["Date", "Desription", "Amount"]
    default_value = ""

    # Create a new dictionary with the desired structure
    structured_data = {key: data_dict.get(key, default_value) for key in keys}

    # Convert the structured data back into a JSON string
    structured_json = json.dumps(structured_data)

    return structured_json

def process_document(file_path):
    try:
        pdf_convert(file_path) #converts page to PNG
        # textOfCV = read_pdf(file_path)
        files = os.listdir(CONVERTED_FOLDER) # Gets PNG files
        for filename in files: 
            file_path = os.path.join(CONVERTED_FOLDER, filename) # create path name for loading
            if os.path.exists(file_path):
                print("reading png")
                textOfCV = read_png(file_path) # Extract text from PNG
                print(textOfCV)
        response = extract_data_with_llama(textOfCV) # Call Llama to read text with prompt, returns json. 
        print("call llama")
        # response = test_prompt(textOfCV)
        print(response.text)
        text = response.text
        f = open('output.csv', 'a')
        writer = csv.writer(f)
        writer.writerows(text) # writes rows to CSV output

# double quotes are for the CMD reader... to show accurately for the reader, not an app to use. 


        print(type(response.))
        # data = json.loads(response)
        # print(data)
        # df = pd.DataFrame([response])
        # # df = 'test'
        # # print(df)
        # print('done')
        # if not os.path.isfile('output.csv'):
        #     df.to_csv('output.csv', mode='w', header=True, index=False)
        # else:
        #     df.to_csv('output.csv', mode='a', header=False, index=False)
    except Exception as e:
        print(f"An error occurred: {e}")


def pdf_convert(document):
    try: 
        images = convert_from_path(document, 500, poppler_path="C:/Program Files/poppler-24.07.0/Library/bin")

        for i in range(len(images)):
            images[i].save('converted/page' + str(i) + '.png', 'PNG')
    except Exception as e: 
        print(f"An error occurred: {e}")


process_document("uploads/testpdf.pdf")
# print(pytesseract.image_to_string(Image.open("uploads/testpdf.pdf")))

