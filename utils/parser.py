import os
from datetime import datetime
from utils.ocr import process_image, process_pdf
from utils.const import Category, budgets, reasons
from utils.env import openai_model, default_month, default_year
import shutil
from tqdm import tqdm
import openai
import json
from tenacity import retry, stop_after_attempt

@retry(stop=stop_after_attempt(3))
def content_parser(text):
    try:
        response = openai.ChatCompletion.create(
            model=openai_model,
            messages=[
                {
                    "role": "user",
                    "content": text
                }
            ],
            functions=[
                {
                    "name": "upload_reimbursement",
                    "description": "Upload reimbursements",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {
                                "type": "string",
                                "description": f"The date in DD-MM-YYYY format string, use {default_year} for default year value & {default_month} for default month value when unable to extract those values from the input"
                            },
                            "category": {
                                "type": "string",
                                "enum": [
                                    "TRAVEL", "TELEPHONE", "INTERNET", "HEALTH"
                                ]
                            },
                            "cost": {
                                "type": "number",
                                "description": "Cost extracted from content, should not be greater than 2000 for cab rides, if you see cost greater than 2000 for cost its probably rupee icon misunderstood by ocr, so costs like 2140 for cabs, consider as Rupee 140"
                            }
                        },
                        "required": [
                            "category","date","cost"
                        ]
                    }
                }
            ]
        )
        return json.loads(response.choices[0].message.function_call.arguments)
    except openai.error.Timeout as e:
        #Handle timeout error, e.g. retry or log
        print(f"OpenAI API request timed out: {e}")
        pass
    except openai.error.APIError as e:
        #Handle API error, e.g. retry or log
        print(f"OpenAI API returned an API Error: {e}")
        pass
    except openai.error.APIConnectionError as e:
        #Handle connection error, e.g. check network or log
        print(f"OpenAI API request failed to connect: {e}")
        pass
    except openai.error.InvalidRequestError as e:
        #Handle invalid request error, e.g. validate parameters or log
        print(f"OpenAI API request was invalid: {e}")
        pass
    except openai.error.AuthenticationError as e:
        #Handle authentication error, e.g. check credentials or log
        print(f"OpenAI API request was not authorized: {e}")
        pass
    except openai.error.PermissionError as e:
        #Handle permission error, e.g. check scope or log
        print(f"OpenAI API request was not permitted: {e}")
        pass
    except openai.error.RateLimitError as e:
        #Handle rate limit error, e.g. wait or log
        print(f"OpenAI API request exceeded rate limit: {e}")
        pass
def prepare_reimbursement(cost, date, category, filepath):
    return {
        'filepath': filepath,
        'date': datetime.strptime(date, "%d-%m-%Y").date(),
        'cost': cost,
        'category':Category[category],
        'reason':reasons[Category[category]],
        'filepath':filepath
    }


def parse_reimbursement_data_from_images(dir_name):

    directory = os.path.join(os.path.dirname(os.path.abspath(__file__)),'../', dir_name)
    unprocessed_fies = []
    success_reimbursements = []
    over_budget_reimbursements = []
    files = os.listdir(directory)

    with tqdm(total=len(files), desc="Processing files") as pbar:
        for filename in files:
            pbar.update(1)
            if filename.endswith('.png') or filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.pdf'):
                image_path = os.path.join(directory, filename)
                try:
                    if filename.endswith('.pdf'):
                        text = process_pdf(image_path)
                    else:
                        text = process_image(image_path)
                    filepath = os.path.join(directory, filename)
                    parsed_data = content_parser(text)
                    reimbursement = prepare_reimbursement(parsed_data["cost"], parsed_data["date"], parsed_data["category"], filepath)
                except Exception as e:
                    print("Error",e)
                    unprocessed_fies.append(image_path)
                    continue
                
                budget = budgets[Category[parsed_data["category"]]]
                total_cost = sum([float(o["cost"]) for o in success_reimbursements if o["category"] == reimbursement['category']])

                if total_cost >= budget:
                    over_budget_reimbursements.append(reimbursement)
                    continue

                success_reimbursements.append(reimbursement)

    directory = os.path.join(os.path.dirname(os.path.abspath(__file__)),'../', 'unprocessed-files')
    for filepath in unprocessed_fies:
        file_name = os.path.basename(filepath)
        destination_path = os.path.join(directory, file_name)
        shutil.copy(filepath, destination_path)

    directory = os.path.join(os.path.dirname(os.path.abspath(__file__)),'../', 'overbudget-bills')
    for reimbursement in over_budget_reimbursements:
        file_name = os.path.basename(reimbursement["filepath"])
        destination_path = os.path.join(directory, file_name)
        shutil.copy(reimbursement["filepath"], destination_path)

    total_over_budget_cost = sum([float(o["cost"]) for o in over_budget_reimbursements])
    print(f'Overbudget total : {total_over_budget_cost}')
    print(f'Unprocessed files : {len(unprocessed_fies)}')
    print(f'Successful files : {len(success_reimbursements)}')

    return success_reimbursements