import requests

db_state_dict = requests.get("http://localhost:5000/browser/1").json()
if db_state_dict[1] == 1:
    print("Browser Ready")
else:
    print("Browser not ready")
#     requests.put("http://localhost:5000/port/1")
#     break
# print("Browser Not Ready")
# time.sleep(1)