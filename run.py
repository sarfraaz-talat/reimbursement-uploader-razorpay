import time
from utils.playwright import init_playwright, submit_reimbursements, terminate_playwright
from utils.parser import parse_reimbursement_data_from_images
from playwright.sync_api import sync_playwright
from tabulate import tabulate

def print_table(reimbursements):
    table = []
    for reimbursement in reimbursements:
        table.append([reimbursement["category"], reimbursement["date"], reimbursement["cost"], reimbursement["filepath"]])

    print(tabulate(table, headers=["Category", "Date", "Cost", "FilePath"], tablefmt="fancy_grid"))

def upload_to_razorpay(playwright, reimbursements):
    browser, page = init_playwright(playwright)
    submit_reimbursements(page, reimbursements)
    terminate_playwright(browser)

def main():
    start_time = time.time()
    with sync_playwright() as playwright:
        reimbursements = parse_reimbursement_data_from_images('files/may')
        print_table(reimbursements)
        user_input = input("Proceed with upload on razorpay (y/n) ?")
        if user_input.lower() == "y":
            upload_to_razorpay(playwright, reimbursements)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Overall time to submit all reimbursements: {elapsed_time} seconds")

if __name__ == '__main__':
    main()
