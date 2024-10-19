import sys 
import os
import requests as req
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# TODO: Repetitive code in go_to_account and fetch_information. Merge it

class Backend:
    def __init__(self, login_callback=None):
        
        app_directory = os.path.join(os.getenv('APPDATA'), 'ErpSnap')
        if not os.path.exists(app_directory):
            os.makedirs(app_directory)

        self.credentials_file = os.path.join(app_directory, 'credentials.txt')
        # self.credentials_file = 'credentials.txt' # comment this line when building app 💥💥💥💥

        self.username = None
        self.password = None
        self.login_callback = login_callback

        self.thread = None #thread from where it is called
    
    def read_credentials(self):
        if os.path.exists(self.credentials_file):
            with open(self.credentials_file, "r") as f:
                lines = f.readlines()
                if len(lines) >= 2:
                    self.username = lines[0].strip()
                    self.password = lines[1].strip()

    def save_credentials(self, username, password):
        with open(self.credentials_file, "w") as f:
            f.write(username + "\n")
            f.write(password)

    def credentials_present(self): #booleanCheck
        self.read_credentials()
        if not self.username or not self.password:
            return False
        return True

    # reads credentials from file, then fetches
    def read_cred_then_execute(self, task):
        print("Button clicked!")
        print(task)
        print(self.thread)

        try:
            self.read_credentials()
            return task()
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
    

    def go_to_account(self):
        req.packages.urllib3.disable_warnings()
        session = req.Session()
        base_url = f"https://103.120.30.61"
        headers = {'host': 'erp.psit.ac.in', 'Cookie': ''}
        login_data = {"username": self.username, "password": self.password}

        # LOGIN-----------------------------------------------------------------------------------
        login_url = f"{base_url}/Erp/Auth"
        login_res = make_request(session, 'post',login_url, headers=headers, data=login_data)
        if login_res['status'] == 'error':
            base_url = f"https://erp.psit.ac.in"
            login_url = f"{base_url}/Erp/Auth"
            login_res = make_request(session, 'post',login_url, headers=headers, data=login_data)
            if login_res['status'] == 'error':
                return f'Error: {login_res["msg"]}'
        
        session_id = login_res['data'].cookies.get("PHPSESSID")
        headers["Cookie"] = f"PHPSESSID={session_id}"
        print('Login Sucesss')
        print(headers)
        
        # GOTO ACCOUNT----------------------------------------------------------------------------
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_experimental_option("detach", True)
        browser = webdriver.Chrome(service=Service(), options=chrome_options)

        browser.get('https://erp.psit.ac.in')
        browser.add_cookie({ 'name': 'PHPSESSID', 'value': session_id, 'domain': 'erp.psit.ac.in' })
        browser.get('https://erp.psit.ac.in/Student/Dashboard')

        return 'success'

    # direct HTTP call from class variables
    def fetch_information(self):
        req.packages.urllib3.disable_warnings()
        session = req.Session()
        base_url = f"https://103.120.30.61"
        headers = {'host': 'erp.psit.ac.in', 'Cookie': ''}
        login_data = {"username": self.username, "password": self.password}

        # LOGIN-----------------------------------------------------------------------------------
        login_url = f"{base_url}/Erp/Auth"
        login_res = make_request(session, 'post',login_url, headers=headers, data=login_data)
        if login_res['status'] == 'error':
            base_url = f"https://erp.psit.ac.in"
            login_url = f"{base_url}/Erp/Auth"
            login_res = make_request(session, 'post',login_url, headers=headers, data=login_data)
            if login_res['status'] == 'error':
                return f'Error: {login_res["msg"]}'
        
        session_id = login_res['data'].cookies.get("PHPSESSID")
        headers["Cookie"] = f"PHPSESSID={session_id}"
        print('Login Sucesss')

        # ATTENDENCE------------------------------------------------------------------------------
        attendance_url = f"{base_url}/Student/MyAttendanceDetail"
        attendance_res = make_request(session, 'get', attendance_url, headers=headers)
        if attendance_res['status'] == 'error':
            return f'Error: {attendance_res["msg"]}'
        
        data = attendance_res['data'].text
        total_lecture = extract_info(data, "Total Lecture : ([0-9]*)")
        total_absent = extract_info(data, "Total Absent \+ OAA: ([0-9]*)")
        attendance_percentage = extract_info(data, "Attendance Percentage : ([0-9.]*)\s%")
        # self.thread.progress.emit(['AttenTab',f'{total_lecture}\n{total_absent}\n{attendance_percentage}'])
        # TODO: Move this to frontend
        BASE_DIR = getattr(sys, '_MEIPASS', os.getcwd())
        percentIcon = os.path.join(BASE_DIR, 'assets/percentage.png')
        presentIcon = os.path.join(BASE_DIR, 'assets/present.png')
        absentIcon = os.path.join(BASE_DIR, 'assets/absent.png')

        self.thread.progress.emit(['Attendance',f'''
                                   <center>
                                   <img src="{presentIcon}" height=25>{total_lecture:>8}
                                   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                                   <img src="{absentIcon}" height=25>{total_absent:>8}
                                   <br>
                                   <img src="{percentIcon}" height=25>{attendance_percentage}
                                   </center>
                                   '''])
        
        # TIMETABLE-------------------------------------------------------------------------------
        timetable_url = f"{base_url}/Student/MyTimeTable"
        timetable_res = make_request(session, 'get', timetable_url, headers=headers)
        if timetable_res['status'] == 'error':
            return f'Error: {timetable_res["msg"]}'

        soup = BeautifulSoup(timetable_res['data'].text, 'html.parser')
        ttable = soup.select('.danger h5')
        ttlist = []
        if not ttable:
            print('No time table for today')
            self.thread.progress.emit(['TimeTable','No timetable for today'])
        else:
            pattern = re.compile(r'\[\s*(.*?)\s*\]')
            for i in range(8):
                matches = pattern.findall(ttable[i].get_text())
                ttlist.append([matches[0],matches[1],matches[2]])
            
            # print(ttlist)
            data = ''
            for i in range(len(ttlist)):
                data += f'{i+1}. {ttlist[i][1]:<14} {shorten_name(ttlist[i][0])}\n'
            self.thread.progress.emit(['TimeTable',data])

        # NOTICES---------------------------------------------------------------------------------
        notices_url = f"{base_url}/Student"
        notices_res = make_request(session, 'get', notices_url, headers=headers)
        if notices_res['status'] == 'error':
            return f'Error: {notices_res["msg"]}'
        
        soup = BeautifulSoup(notices_res['data'].text,'html.parser')
        ntcHTML = soup.select('.table2 > tbody tr')
        notices = []
        for i in range(5):
            ntc = ntcHTML[i].find("a")
            notices.append([ntc.get_text(),ntc['href']])

        # print(notices)
        data = ''
        for notice in notices:
            data += f'<li><strong>★</strong><a href="{notice[1]}">{notice[0].capitalize()}</a><br></li>'
        
        self.thread.progress.emit(['Notices',data])

        return 'success'
    
def shorten_name(full_name):
    match = re.match(r'^(\S+)', full_name)
    if match:
        first_word = match.group(1)
        return first_word + " " + ' '.join(word[0] + '.' for word in full_name.split()[1:])
    return full_name

def make_request(session, method,url, **kwargs):
    try: 
        res = session.request(method, url, verify=False, timeout=8, **kwargs)
        if res.status_code == 200:
            return {'status': 'success','data':res}
        else:
            return {'status': 'error','msg':f'HTTPError: {res.status_code}'}
    except req.ConnectionError:
        return {'status': 'error','msg':'No Internet Connection'}
    except req.Timeout:
        return {'status': 'error','msg':'Request timed out.\nSlow internet connection'}

def extract_info(data, pattern):
    match = re.search(pattern, data)
    return match.group(1) if match else "Not found"