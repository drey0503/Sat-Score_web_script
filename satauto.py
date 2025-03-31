# Dreyson Clark
# 03/25/2025
# This script utilizes Selenium, an open source framework used for automating web applications in different browsers
# What is required for this script? Python installed, Selenium, and Chrome Webdriver as this script utilizes Chrome
# forewarning, if you change the credentials to this login, you will need to change the credentials in the code above.

# below are a list of modules from Selenium that allow me to utlizes the different parts of the website i'm accessing
import os
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import smtplib
import ssl
from email.message import EmailMessage

# Automatically installs the correct version of ChromeDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Set download directory for SAT files
download_dir = r"C:\Users\dreyson\Desktop\SAT_Files"

prefs = {"download.default_directory": download_dir,
         "download.prompt_for_download": False}

# Set Chrome options
chrome_options = Options()
# Update if needed
chrome_options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
chrome_options.add_experimental_option("prefs", prefs)

# Start the driver with the download directory set
# Service should have the path to the chrome driver executable
# Adjust the path
service = Service(
    "C:\\Users\\dreyson\\Downloads\\chromedriver-win32\\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)

# Email credentials (Use environment variables or a secrets manager instead of hardcoding!)
EMAIL_SENDER = "***REDACTED@gmail.com***"
EMAIL_PASSWORD = "***REDACTED***"  # Use an App Password if using Gmail
# Send email to yourself or another recipient
EMAIL_RECEIVER = "***REDACTED***"



# Get today's date in the format matching the website
today_date = datetime.today().strftime("%m/%d/%Y")  # Adjust format if needed


# need to pull the website using the webservice driver in chrome to go straight to login


def site_load():

    driver.get("https://prod.idp.collegeboard.org/oauth2/aus3koy55cz6p83gt5d7/v1/authorize?client_id=0oa3koxakyZGbffcq5d7&response_type=code&scope=openid+email+profile&redirect_uri=https://account.collegeboard.org/login/exchangeToken&state=cbAppDurl&login_hint=&nonce=MTc0MjkxNDM5Mjk0MA==")
    time.sleep(7)


# associate the email box with the portion of the XML on the collegeboard site that holds
# email and input in the email then click next
def login_box():
    email_box = driver.find_element(By.ID, "input28")
    email_box.send_keys("***REDACTED***")

# this had to be by class name because the next button didn't have an id but a class name
# add .click() at the end for the click action

    next_box = driver.find_element(By.CLASS_NAME, "button-primary").click()
# log count to see if process worked
# it runs process for 10 seconds. if it doesn't go through an error message will appear

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "input28")))
        print("Username field appeared!")
    except Exception as e:
        print("Username field did not appear. Login process might be broken.")

# select verify by password option instead of email code


def verify_by_password():
    password_select = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[@aria-label='Select Password.']"))
    )
    password_select.click()
    print("Password verify option clicked!")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "credentials.passcode")))

    print("Password element found!")


def login():
    password_box = driver.find_element(
        By.XPATH, "//input[@name='credentials.passcode']")
    driver.execute_script("arguments[0].scrollIntoView();", password_box)
    password_box.click()
    password_box.send_keys("***REDACTED!***")


def verify_button():
    # hit verify to the next page
    verify_box = driver.find_element(By.CLASS_NAME, "button-primary").click()
# try block to selct sign in button
    try:
        sign_in_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Sign In"))
        )
        sign_in_button.click()
    except:
        print("❌ Sign In button not found! Skipping or retrying...")

# send message if we were successful in logging in
    if "dashboard" in driver.current_url:
        print("✅ Login successful!")
    else:
        print("❌ Login failed!")


def navigate_to_files():
    # need to select the link where we can download the files
    link = driver.find_element(
        By.XPATH, "//a[@href='https://hedreports.collegeboard.org']")
    link.click()

    time.sleep(10)


def download_files():
    td_elements = driver.find_elements(By.TAG_NAME, "td")
    file_found = False
    # Loop through td elements and check for matching delivery dates
    for td in td_elements:
        try:
            # Wait for td to be visible (if needed)
            WebDriverWait(driver, 5).until(EC.visibility_of(td))
            # Locate span inside td
            spans = td.find_elements(By.TAG_NAME, "span")
            if not spans:  # If no span is found, skip
                print(f"Skipping TD: {td.get_attribute('outerHTML')}")
                continue

            # Extract the text from the first span (if multiple exist)
            delivery_date = spans[0].text.strip() if spans else None

            if delivery_date == today_date:
                file_found = True
                print(f"✅ Found file with delivery date {delivery_date}")

                # Find the parent row (tr)
                parent_tr = td.find_element(By.XPATH, "./ancestor::tr")

                # Locate the span holding the download link
                file_span = parent_tr.find_elements(
                    By.CLASS_NAME, "cb-btn-naked")
                if not file_span:
                    print(
                        f"❌ No download link found in row: {parent_tr.get_attribute('outerHTML')}")
                    continue
                # Click the span to trigger the download
                driver.execute_script("arguments[0].click();", file_span[0])
                print("✅ Clicked the download button")

        except Exception as e:
            print(f"❌ Error processing TD: {e}")
            send_email(status="failed", files_found=False,
                       today_date=today_date)  # Notify failure
    # send email success
    send_email(status="success", files_found=file_found,
               today_date=today_date)
    if not file_found:
        print(f"⚠️ No files found for the date {today_date}.")


def send_email(status, files_found, today_date):
    subject = "SAT Selenium Script Execution Report"
    if files_found:
        body = f"✅ The SAT Selenium script completed successfully. Files were found and downloaded for {today_date}."
    else:
        body = f"⚠️ The SAT Selenium script completed, but no files were found for {today_date}."

    # Add failure message if needed
    if status == "failed":
        subject = "🚨 Selenium Script Failed!"
        body = f"❌ The Selenium script encountered an error and failed to complete."

    # Create email message
    msg = EmailMessage()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = subject
    msg.set_content(body)

    # Send the email using SMTP
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        print("📧 Email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")


# running each method in the order they need to be ran for organization purposes
site_load()
login_box()
verify_by_password()
login()
verify_button()
navigate_to_files()
download_files()
print("Script Complete")
time.sleep(7)  # Optional, use WebDriverWait if needed


driver.quit()
