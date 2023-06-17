### Razorpay Reimbursements Uploader

A simple tool which will read all your utility bills and upload them on razorpay. It uses ocr to read text from the image/pdf and then sends it to openai apis to parse the kind of bill, date of purchase and the cost of purchase. Prepares the reimbursements data based on this parsing, then uses playwright to login to the razorpay dashboards, and upload reimbursements.

#### The Setup

Install python 3 if you don't have it already

```
brew install python
```

Install python dependencies

```
pip install -r requirements
```

Install playwright browsers

```
playwright install
```

Create .env file in the root of the project, add your openai api key and razorpay credentials

```
RAZORPAY_USERNAME=
RAZORPAY_PASSWORD=
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4-0613
DEFAULT_MONTH=May
DEFAULT_YEAR=2023
```

If you don't have access to gpt-4 apis, you can use gpt-3.5-0613 instead

#### The Action

Create a new directory named `files` in root folder

Dump all your utility bills you want to submit to razorpay inside `files/` folder. Currently it supports only images [jpg/jpeg/png] and pdf formats

Now run the script in debug mode to see if the parsing is doing fine for all your files

Since this is the first version and tested manually only, do always run it in the debug mode first to see the results are acceptable. Otherwise you might end up with faulty data uploaded to your razorpay dashboard

```
python run.py
```

It will print parsed information about your bills, just take a glance to make sure everything checks out, if its showing incorrect results for any bills, feel free to open an issue, and for now, remove that files from the `files/` folder to continue uploading bills on razorpay

You'd see screen like this
```
Proceed with upload on razorpay (y/n) ? 
```

Once you are satisfied with the results on console, you can respond with y and hit enter to start uploading your reimbursements on razorpay

#### Known Issues

If you are stuck on the razorpay login screen and see error on console after some time, your saved cookies for razorpay dashboard are probably expired

Remove `cookies.json` file from root and run sript again, should work fine

#### Todo

- Reduce gpt-calls by adding inputs in batch to the prompt and getting responses in bulk for same, this will reduce cost and increase performance

##### PS

- You can modify the budgets according to your requirements in `const/parser.py` file
