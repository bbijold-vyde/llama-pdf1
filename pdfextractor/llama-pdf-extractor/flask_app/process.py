import openai 
import re
import fitz  # PyMuPDF PDF READ
import os
import time
import json
import pandas as pd
from langchain_community.llms import Ollama

#API KEY

#PDF READ
def read_pdf(file_path):
    try:
        # Open the PDF
        doc = fitz.open(file_path)

        # Extract text from the first page
        first_page_text = doc[2].get_text()
        # for page in doc:
        #     text = page.get_text()
        #     print(text)
            # Some transactions are wrong due to how a PDF to Text functions - highlight on pdf for proof. 

        # Close the document
        doc.close()

        return  first_page_text # Return the first page
    except Exception as e:
        print("Error opening PDF: " + str(e) + file_path)
        return "Error opening PDF: " + str(e) + file_path

# def extract_data_with_gpt(textOfCV):
#     # Replace this with an appropriate prompt for the GPT model based on your data
#     prompt = (
#     "A következő szöveg alapján kérlek, gyűjtsd ki a jelentkező adatait, és formázd őket JSON formátumba. "
#     "Az adatok között szerepelnie kell a névnek, email címnek, telefonszámnak, középiskola nevének, középiskolai szaknak, "
#     "egyetem nevének, egyetemi szaknak, idegen nyelvnek és annak szintjének. Ha valamelyik adat nem áll rendelkezésre, "
#     "az arra vonatkozó mezőt hagyd üresen. A szöveg a következő: \"" + textOfCV + "\"\n"
#     "A JSON formátum a következő legyen:\n"
#     "{\n"
#     "    \"nev\": \"<NÉV>\",\n"
#     "    \"email\": \"<EMAIL>\",\n"
#     "    \"telefonszam\": \"<TELEFONSZÁM>\",\n"
#     "    \"kozepiskola\": \"<KÖZÉPISKOLA>\",\n"
#     "    \"kozep_szak\": \"<KÖZÉPISKOLAI SZAK>\",\n"
#     "    \"egyetem\": \"<EGYETEM>\",\n"
#     "    \"egyetem_szak\": \"<EGYETEMI SZAK>\",\n"
#     "    \"nyelvvizsga\": \"<NYELVVIZSGA>\",\n"
#     "    \"nyelv_szintje\": \"<NYELV SZINTJE>\"\n"
#     "}"
#     )

#     response = openai.Completion.create(model="gpt-3.5-turbo-instruct", prompt=prompt, max_tokens=1024)
#     return response.choices[0].text.strip()

def extract_data_with_llama(textOfCV):
    llm = Ollama(model="llama3.1", format="json")
    prompt = (
 "Based on the following text, please collect the account owner's transaction data and format them in JSON format."
 "The data must include date, description, and amount. If any data is not available, "
 "do not add the transaction. The text is: \"" + textOfCV + "\"\n"
 "Format should be:"
 "\n{ Date: <DATE>, Description: <DESCRIPTION>, Amount: <AMOUNT> } \n,{...},{...}"
#  " \"Date\": \"<DATE>\",\n"
#  " \"Description\": \"<DESCRIPTION>\",\n"
#  " \"Amount\": \"<AMOUNT>\",\n"
#  "},{...},{...}"
#  "{Date: <DATE>,\n"
#  "Description: <DESCRIPTION>,\n"
#  " Amount: <AMOUNT>,\n"
#  "},{...},{...}"
#  "Using double quotes for the '{'\"Key\": \"Value\"'}' pairs. "
 "The response contains only the JSON structure."
    )
    result = llm.invoke(prompt)
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
        print(f"Processing {file_path}")
        textOfCV = read_pdf(file_path)
        response = extract_data_with_llama(textOfCV)
        print(response)
        # data = json.loads(response)
        # print(data)
        df = pd.DataFrame([response])
        print(df)
        print('done')
        if not os.path.isfile('output.csv'):
            df.to_csv('output.csv', mode='w', header=True, index=False)
        else:
            df.to_csv('output.csv', mode='a', header=False, index=False)
    except Exception as e:
        print(f"An error occurred: {e}")
