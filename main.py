# Import modules
import csv, os, time, psutil
import threading

# Import functions
import SetEnviron
import setup_db
from app import app
import funcs as funcs

# Setup Environments
SetEnviron.SetEnviron()

# Setup Database
setup_db.setup_table()


# Start Flask
if __name__ == '__main__':
    tr = threading.Thread(target=app.run)
    tr.start()


LEADS_FILE_NAME = os.environ['LEADS_FILE_NAME']
STREET_COL = int(os.environ["STREET_COL"]) - 1
ZIP_COL = int(os.environ["ZIP_COL"]) - 1
STATE_COL = ZIP_COL - 1
CITY_COL = STATE_COL -1


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



# Start operations
lines = []


with open(LEADS_FILE_NAME, 'r') as csv_file:
    csv_render = csv.reader(csv_file)
    for line in csv_render:
        lines.append(f"{line[STREET_COL]},,{line[CITY_COL]}, {line[STATE_COL]} {line[ZIP_COL]}")


for line in lines:
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
                funcs.input_search(street_search, city_state_search)
                time.sleep(10)
                results = funcs.get_links(street, state)
                return results
            except Exception as e:
                print(e)
                exit_chrome_linux()
                print("Failed opening browser")
                time.sleep(2)


    results = get_search_results()
    print(results)


    # for result in results:
    #     print(result)
    #     funcs.open_persons(result['link'], street, result['name'], result['address'], True)
    #     exit_chrome_linux()
    #     time.sleep(5)

    exit_chrome_linux()
    time.sleep(3)