import os
import json
from utils.env import razorpay_username, razorpay_password
from tqdm import tqdm

def login_to_razorpay(page):
    page.goto("https://payroll.razorpay.com/login")

    # Fill in the email field
    email_selector = 'input[type="email"]'
    page.fill(email_selector, razorpay_username)
    # Fill in the password field
    password_selector = 'input[type="password"]'
    page.fill(password_selector, razorpay_password)
    page.press(password_selector, 'Enter')

    page.wait_for_load_state("networkidle")

    save_cookies(page)

    print("logged in to razorpay dashboard")

def save_cookies(page):
    cookies = page.context.cookies()
    with open("cookies.json", "w") as f:
        json.dump(cookies, f)

def load_cookies(page):
    with open("cookies.json", "r") as f:
        cookies = json.load(f)
    page.context.add_cookies(cookies)

def init_playwright(playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()

    page = context.new_page()

    if not os.path.exists("cookies.json"):
        login_to_razorpay(page)
    else:
        load_cookies(page)
        page.reload()            
    return browser, page

def terminate_playwright(browser):
    browser.close()

def submit_reimbursements(page, reimbursements):

    with tqdm(total=len(reimbursements), desc="Submitting reimbursements on razorpay") as pbar:
        for reimbursement in reimbursements:
            pbar.update(1)
            # Go to the reimbursements submission page
            page.goto('https://payroll.razorpay.com/reimbursements')

            # Fill in the date and amount fields
            page.select_option('#type', reimbursement['category'].value)
            page.click('.datepicker-past.picker__input')
            page.select_option('#expense-date-past >> .picker__select--year',f'{reimbursement["date"].year}')
            page.select_option('#expense-date-past >> .picker__select--month',f'{reimbursement["date"].month - 1}')
            selector = f'[aria-label="{reimbursement["date"].strftime("%-d %B, %Y")}"]'
            page.click(selector)
            
            page.fill('#reason', reimbursement["reason"])
            page.fill('#amount', f'{reimbursement["cost"]}')

            # Upload the attachment
            file_input = page.query_selector('input[type="file"]')
            file_input.set_input_files(reimbursement["filepath"])

            # Submit the form
            page.click('input[type="submit"]')
            page.wait_for_load_state('networkidle')
    
