# Import modules
import csv, os, time, psutil
import threading
import customtkinter as ctk

# Import API Modules
from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS

# Import Scraping Modules
import threading, os, sys, time, subprocess, requests
from twocaptcha import TwoCaptcha

from subprocess import Popen
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

operating_system = "linux"

# Import functions
import setup_db
import sqlite3, os

# Setup Database
if os.path.exists('db.sqlite'):
    os.remove('db.sqlite')
conn = sqlite3.connect('db.sqlite')
cursor = conn.cursor()
sql_query = """ CREATE TABLE browser (
    id integer PRIMARY KEY,
    status integer NOT NULL
) """
try:
    cursor.execute(sql_query)
except sqlite3.OperationalError as e:
    print(e)
def setup_table():
    sql = """INSERT INTO browser (status) 
                VALUES (?)"""
    conn.execute(sql, (0,))
    conn.commit()
setup_table()



# Flask API Functions

app = Flask(__name__)
CORS(app)

def db_connection():
    conn = None
    try:
        conn = sqlite3.connect('db.sqlite')
    except sqlite3.error as e:
        print(e)
    return conn

@app.route('/browsers', methods=['GET', 'POST'])
def browsers():
    conn = db_connection()
    cursor = conn.cursor()
    if request.method == 'GET':
        cursor = conn.execute("SELECT * FROM browser")
        browsers = [
            dict(id=row[0])
            for row in cursor.fetchall()
        ]
        if browsers is not None:
            return jsonify(browsers)
    
    elif request.method == 'POST':
        status = request.form['status']
        sql = """INSERT INTO browser (status)
                 VALUES (?, ?)"""
        cursor = cursor.execute(sql, (status))
        conn.commit()
        return f"Browser with the id: {cursor.lastrowid} created successfully"

@app.route('/browser/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def single_browser(id):
    # print(f"Request 1: {id}")
    conn = db_connection()
    cursor = conn.cursor()
    browser = None
    if request.method == 'GET':
        cursor.execute("SELECT * FROM browser WHERE id=?", (id,))
        rows = cursor.fetchall()
        for row in rows:
            browser = row
        if browser is not None:
            return jsonify(browser), 200
        else:
            return "Something wrong", 404

    elif request.method == 'PUT':
        # print(f"Reuqest PUT Initiated {id}")
        sql = """UPDATE browser
                SET status=?
                WHERE id=? """
        # print(f"Request: {request.json}")
        status = request.json['status']
        updated_browser = {
            "id": id,
            "status": status
        }
        # print(f"Update Browser: {updated_browser}")
        conn.execute(sql, (status, id))
        conn.commit()
        response = jsonify(updated_browser)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    elif request.method == 'DELETE':
        sql = """ DELETE FROM browser WHERE id=?"""
        conn.execute(sql, (id,))
        conn.commit()
        return f"The browser with id: {id} has been deleted", 200

@app.route('/id/<int:id>', methods=['GET', 'PUT'])
def browser_port(id):
    browser = None
    if request.method == 'GET':
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM browser WHERE id=?", (id,))
        rows = cursor.fetchall()
        for row in rows:
            browser = row
        if browser is not None:
            return jsonify(browser), 200
        else:
            return "Something wrong", 404
    elif request.method == 'PUT':
        sql = """UPDATE browser
                SET status=? """
        status = 0
        updated_browser = {
            "status": status
        }
        # print(f"Update Browser: {updated_browser}")
        conn = db_connection()
        conn.execute(sql, (status,))
        conn.commit()

        response = jsonify(updated_browser)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


# Start Flask
if __name__ == '__main__':
    tr = threading.Thread(target=app.run)
    tr.start()


# Required functions
def exit_chrome():
    subprocess.call("TASKKILL /f  /IM  CHROME.EXE")


def exit_chrome_linux():
    def get_chrome_pid():
        chrome_procs = []
        for proc in psutil.process_iter(['pid', 'name']):
            if 'chrome' in proc.info['name'].lower():
                chrome_procs.append(proc.info['pid'])
        return chrome_procs
    chrome_pids = get_chrome_pid()
    for pid in chrome_pids:
        os.system(f'kill -9 {pid}')


def remove_old_file():
    if os.path.exists('Extract.txt'):
        os.remove('Extract.txt')
remove_old_file()



# Scraping Functions

chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "localhost:9001")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--log-level=0')


def create_driver():
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    wait = WebDriverWait(driver, 15)
    return driver, wait


def browser_open(url, page):
    # time.sleep(2)
    print("\n", f"INFO: Opening Page: {page}", "\n")
    print(f"URL To Open: {url}, Page: {page}")
    if operating_system == "linux":
        subprocess.call(['google-chrome', '--no-sandbox', '--hide-crash-restore-bubble', '--remote-debugging-port=9001', url], stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
    else:
        command = f'start chrome --hide-crash-restore-bubble --remote-debugging-port=9222 "{url}"'
        os.system(command)


def solve_hcaptcha(driver, wait):
    def solvehCaptcha():
        api_key = os.getenv('APIKEY_2CAPTCHA', 'd43384a8f2d585914afff28fa097c287')
        solver = TwoCaptcha(api_key)
        try:
            print("Trying to solve cpatcha")
            result = solver.hcaptcha(
                sitekey='8c6693a8-2959-420f-ba6c-474f2460a6cf',
                url='https://www.truepeoplesearch.com/InternalCaptcha?',
            )
        except Exception as e:
            print("Could not solve captcha.")
            print(e)
            return False
        else:
            return result

    while True:
        result = solvehCaptcha()
        print("Solved Cpatcha...")
        if result:
            code = result['code']
            driver.execute_script(
                "document.querySelector(" + "'" + '[name="h-captcha-response"]' + "'" + ").innerHTML = " + "'" + code + "'")
            driver.find_element(
                By.XPATH, '//button[@type="submit"]').click()
            print("Cpatcha bypassed...")
            return True
        else:
            time.sleep(2)



def input_search(street, city_state):

    url = f"https://www.truepeoplesearch.com/resultaddress?streetaddress={street.strip()}&citystatezip={city_state.strip()}"
    tr = threading.Thread(target=browser_open, args=(url, 'search addresses',))
    tr.start()



def get_links(street, state):
    print("Started get_links function")
    requests.put("http://localhost:5000/id/1")
    print("Push request executed.")
    while True:
        db_state_dict = requests.get("http://localhost:5000/browser/1").json()
        print(f"DB Status: {db_state_dict[1]}")
        if db_state_dict[1] == 1:
            print("Browser Ready")
            requests.put("http://localhost:5000/id/1")
            break
        elif db_state_dict[1] == 2:
            break
        print("Browser Not Ready")
        time.sleep(1)

    start_time = time.time()
    driver, wait = create_driver()
    print("Driver connected")
    driver.execute_script("window.stop();")
    if db_state_dict[1] == 2:
        solve_hcaptcha(driver, wait)
        requests.put("http://localhost:5000/id/1")
    
    print("Browser check passed")
    wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="card card-body shadow-form card-summary pt-3"]')))
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    results = soup.findAll('div', {'class', 'card card-body shadow-form card-summary pt-3'})
    print(f"Total Results: {len(results)}")
    results_json = []

    for result in results:
        link = result['data-detail-link']
        texts = result.findAll('span', {'class': 'content-value'})
        text = texts[1].text

        print(f"Result: {link} SITE STATE: {text.strip()} SEARCH STATE: {state}")

        if text.strip() == state:
            data = {
                'name': result.find('div', {'class', 'h4'}).text.strip("\n"),
                'address': f"{street.strip()}, {texts[1].text}",
                'link': "https://www.truepeoplesearch.com" + link,
                }
            results_json.append(data)
    
    end_time = time.time()
    execution_time = end_time - start_time
    print("----------------------Total execution time:", execution_time, "seconds")
    return results_json




def open_persons(url, street, name, address, browser):
    if browser:
        tr = threading.Thread(target=browser_open, args=(url, 'to scrap people',))
        tr.start()

    requests.put("http://localhost:5000/id/1")
    while True:
        db_state_dict = requests.get("http://localhost:5000/id/1").json()
        if db_state_dict[1] == 1:
            print("Browser Ready")
            requests.put("http://localhost:5000/id/1")
            break
        elif db_state_dict[1] == 2:
            break
        print("Browser Not Ready")
        time.sleep(1)



    start_time = time.time()
    driver, wait = create_driver()
    print("Driver connected")
    driver.execute_script("window.stop();")

    if db_state_dict[1] == 2:
        solve_hcaptcha(driver, wait)
        requests.put("http://localhost:5000/id/1")
    
    print("Browser check passed")
    def check_matches(url, street):
        street_address = wait.until(EC.presence_of_element_located((By.XPATH, '//span[@itemprop="streetAddress"]'))).text
        if street_address.strip() == street.strip():

            wireless = driver.find_elements(By.XPATH,'//span[text()="Wireless"]')
            if len(wireless) > 0:
                print("Wireless", len(wireless))
                wireless = True
            else:
                wireless = False
            
            email = driver.find_elements(By.XPATH, "//i[@class='fa fa-envelope text-center']")
            if len(email) > 0:
                email = True
            else:
                email = False
        
            if wireless or email:
                return True
            else:
                return False
            
        else:
            print("\n", f"Street didnt match {street} - {street_address}", "\n")


    searchable = check_matches(url, street)

    if searchable:
        print("SCRAPABLE")
        page_source = driver.page_source
        person_soup = BeautifulSoup(page_source, 'html.parser')

        spans = person_soup.findAll('span', {'class': 'smaller'})

        wireless_list = []
        for span in spans:
            if span.text == 'Wireless':
                number = span.find_previous_sibling('a')
                wireless_list.append(number.text)
        wireless_numbers = ', '.join(str(e) for e in wireless_list)

        landline_list = []
        for span in spans:
            if span.text == 'Landline':
                number = span.find_previous_sibling('a')
                landline_list.append(number.text)
        landline_numbers = ', '.join(str(e) for e in landline_list)

        print(wireless_list)
        print(landline_list)

        try:
            age_obj = person_soup.find('div', {'class', 'row pl-md-1'}).find('span').text
            age = age_obj.split("(")[0].split('Age')[1]
        except:
            age = person_soup.find('div', {'class', 'row pl-md-1'}).find('span').text

        mail_exists = person_soup.findAll('i', {'class': 'fa fa-envelope fa-2x text-center'})

        print(f"Email length: {len(mail_exists)}")

        mail_list = ""

        if len(mail_exists) > 0:
            envelope = person_soup.find('i', {'class': 'fa fa-envelope fa-2x text-center'})
            envelope_parent = envelope.parent
            all_emails = envelope_parent.find_next_sibling()
            email_list = []
            emails = all_emails.findAll('div', {'class', 'row pl-sm-2'})
            for email in emails:
                email_list.append(email.div.div.text.strip())
            mail_list = ', '.join(str(e) for e in email_list)
        else:
            mail_list = ""

        data = f"Name: {name}, Address: {address}, Age: {age}, Wireless Numbers: {wireless_numbers}, Landline Numbers: {landline_numbers}, Emails: {mail_list}"
        print(data)
        with open('results.txt', 'a') as f:
            f.write(data + "\n")
        # update.spreadsheet(name, address, age, wireless_numbers, landline_numbers, mail_list)
    end_time = time.time()
    execution_time = end_time - start_time
    print("----------------------Total execution time:", execution_time, "seconds")



# Start operations


def start():
    spreadsheet_id = spreadsheet_id_entry.get()
    spreadsheet_name = spreadsheet_name_entry.get()
    leads_file_name = leads_file_name_entry.get()
    street_column = int(street_column_entry.get()) - 1
    zip_column = int(zip_column_entry.get()) - 1
    state_col = zip_column - 1
    city_col = state_col - 1
    license_key = license_key_entry.get()

    if os.path.exists('.env'):
        os.remove(".env")

    with open(".env", "a") as f:
        f.write(f"SPREADSHEET_ID = {spreadsheet_id} \n")
        f.write(f"SPREADSHEET_NAME = {spreadsheet_name} \n")
        f.write(f"LEADS_FILE_NAME = {leads_file_name} \n")
        f.write(f"STREET_COL = {street_column_entry.get()} \n")
        f.write(f"ZIP_COL = {zip_column_entry.get()} \n")

    lines = []

    with open(leads_file_name, 'r') as csv_file:
        csv_render = csv.reader(csv_file)
        for line in csv_render:
            lines.append(f"{line[street_column]},,{line[city_col]}, {line[state_col]} {line[zip_column]}")


    for line in lines:
        print(line)
        print(f"Line Length: {len(line)}")
        if len(line) < 10:
            continue
        address = line.split(",,")

        street = address[0]
        city_state = address[1]

        splited = city_state[:-6].split()
        state = " ".join(splited)

        street_chars = street.split()
        street_search = '%20'.join(street_chars)
        city_state_chars = city_state.split()
        city_state_search = '%20'.join(city_state_chars)

        print("\n\n", f"Searching: {street.strip()}, {city_state.strip()}", "\n\n")

        def get_search_results():
            while True:
                try:
                    input_search(street_search, city_state_search)
                    print("Trying to get links")
                    results = get_links(street, state)
                    if operating_system == "linux":
                        exit_chrome_linux()
                    else:
                        exit_chrome()
                    return results
                except Exception as e:
                    print(e)
                    if operating_system == "linux":
                        exit_chrome_linux()
                    else:
                        exit_chrome()
                    print("Failed opening browser")

        results = get_search_results()
        print(results)

        for result in results:
            try:
                open_persons(result['link'], street, result['name'], result['address'], True)
                if operating_system == "linux":
                    exit_chrome_linux()
                else:
                    exit_chrome()
            except Exception as e:
                print(f'Error: {e}')
                def get_person():
                    while True:
                        try:
                            print("Trying exit browser and restart")
                            if operating_system == "linux":
                                exit_chrome_linux()
                            else:
                                exit_chrome()
                            open_persons(result['link'], street, result['name'], result['address'], True)
                            if operating_system == "linux":
                                exit_chrome_linux()
                            else:
                                exit_chrome()
                            return
                        except Exception as e:
                            print(e)
                get_person()



if os.path.exists(".env"):
    with open('.env', 'r') as f:
        values = f.readlines()
    
try:
    spreadsheet_id_default = values[0].split("=")[1].strip()
    spreadsheet_name_default = values[1].split("=")[1].strip()
    leads_file_name_default = values[2].split("=")[1].strip()
    street_column_default = values[3].split("=")[1].strip()
    zip_column_default = values[4].split("=")[1].strip()
except:
    spreadsheet_id_default = ""
    spreadsheet_name_default = "Date"
    leads_file_name_default = ""
    street_column_default = 16
    zip_column_default = 20

def stop():
    if operating_system == "linux":
        exit_chrome_linux()
    else:
        exit_chrome()
    
    if operating_system == "linux":
        scraper_procs = []
        for proc in psutil.process_iter(['pid', 'name']):
            print(proc.info['name'].lower())
            if 'python' in proc.info['name'].lower():
                scraper_procs.append(proc.info['pid'])
        print(f"PIDS: {scraper_procs}")
        for pid in scraper_procs:
            os.system(f'kill -9 {pid}')
    else:
        subprocess.call("TASKKILL /f  /IM  python")


def safe_start():
    tr = threading.Thread(target=start)
    tr.start()


ctk.set_appearance_mode("pitch-black")
ctk.set_default_color_theme("dark-blue")
root = ctk.CTk()
root.title('Truepeoplesearch Scraper')
root.geometry("500x550")
root.protocol("WM_DELETE_WINDOW", stop)
frame = ctk.CTkFrame(master=root)
frame.pack(pady=25, padx=50, fill="both", expand=True)
label = ctk.CTkLabel(master=frame, text="Settings", font=("Roboto", 24))
label.pack(pady=15, padx=15)
spreadsheet_id_entry = ctk.CTkEntry(master=frame, placeholder_text="Spreadsheet ID")
spreadsheet_id_entry.insert(0, spreadsheet_id_default)
spreadsheet_id_entry.pack(pady=12, padx=10)
spreadsheet_name_entry = ctk.CTkEntry(master=frame, placeholder_text="Spreadsheet Name")
spreadsheet_name_entry.insert(0, spreadsheet_name_default)
spreadsheet_name_entry.pack(pady=12, padx=10)
leads_file_name_entry = ctk.CTkEntry(master=frame, placeholder_text="CSV File Name")
leads_file_name_entry.insert(0, leads_file_name_default)
leads_file_name_entry.pack(pady=12, padx=10)
street_column_entry = ctk.CTkEntry(master=frame, placeholder_text="Street Column")
street_column_entry.insert(0, street_column_default)
street_column_entry.pack(pady=12, padx=10)
zip_column_entry = ctk.CTkEntry(master=frame, placeholder_text="Street Column")
zip_column_entry.insert(0, zip_column_default)
zip_column_entry.pack(pady=12, padx=10)
license_key_entry = ctk.CTkEntry(master=frame, placeholder_text="License Key", show="*")
license_key_entry.pack(pady=12, padx=10)
button_entry = ctk.CTkButton(master=frame, text="Start", command=safe_start)
button_entry.pack(pady=12, padx=10)
root.mainloop()