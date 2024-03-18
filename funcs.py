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
    subprocess.call(['google-chrome', '--no-sandbox', '--hide-crash-restore-bubble', '--remote-debugging-port=9001', url], stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
    # command = f'start chrome --hide-crash-restore-bubble --remote-debugging-port=9222 "{url}"'
    # os.system(command)


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