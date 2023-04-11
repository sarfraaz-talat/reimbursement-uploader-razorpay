import os
from datetime import datetime
from utils.ocr import process_image, process_pdf
from utils.const import Category, budgets, reasons
from utils.env import openai_model
import shutil
from tqdm import tqdm
import openai

def category_parser(text):
    response = openai.ChatCompletion.create(
    model=openai_model,
    messages=[
            {"role": "system", "content": f"You are a helpful assistant. Having deep knowledge of images and the ocr tools, how the text generation happens from the image. You will be given a text chunk which is generated from an image using ocr library. You need to read the text which understandably might contain some gibberish text and noise, but you need to read it and identify which category this text belongs to. The categories are TRAVEL, TELEPHONE, INTERNET, HEALTH. The response must contain only one of these category and nothing else. If you are not sure, give the category response as UNKNOWN."},
            {"role": "user", "content": f"The text of ocr start from next line\n{text}"}
        ]
    )
    return response.choices[0].message.content

def cost_date_parser(text):
    response = openai.ChatCompletion.create(
    model=openai_model,
    messages=[
            {"role": "system", "content": f"You are a helpful assistant. Having deep knowledge of images and the ocr tools, how the text generation happens from the image. You will be given a text chunk which is generated from an image using ocr library. The image is from a utility bill of any of these category TRAVEL, TELEPHONE, INTERNET, HEALTH. You need to read the text and parse the date and final cost from the same. The date might be in different formats in different types of bills you need to be mindful of that and try to parse date from the same still and sometimes some important characters ike / might be missing from the date since its ocr output, you need to work through these issues and figure out the date. Same goes for cost as well. One trick for cost is that for most of the bills, cost will be in 3 digits before fractions. The output should be `date:cost` and nothing else. date in the output must be strictly in this format `%d-%m-%Y` Example `25-04-2023` regardless of what format it was in the ocr text. In cases where there are multiple dates in the given text, look for text alongside same which suggests this might be the date of billing or date of order or something along the lines. Be very mindful of the output format, it strictly should be in the given date format then cost separated by collon without containing any single character extra in response, not even any text supporting date or any currency symbols in cost"},
            {"role": "user", "content": f"The text of ocr start from next line\n{text}"}
        ]
    )
    return response.choices[0].message.content.split(":")

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
                    category = category_parser(text)
                    if category == Category.UNKNOWN.name:
                        unprocessed_fies.append(image_path)
                        continue
                    filepath = os.path.join(directory, filename)
                    print(f"text : ${text}")
                    date, cost = cost_date_parser(text)
                    reimbursement = prepare_reimbursement(cost, date, category, filepath)
                except:
                    unprocessed_fies.append(image_path)
                    continue
                
                budget = budgets[Category[category]]
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