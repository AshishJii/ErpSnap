import os
import requests as req
from bs4 import BeautifulSoup
import re

class Backend:
    def __init__(self, login_callback=None):
        
        app_directory = os.path.join(os.getenv('APPDATA'), 'ErpSnap2')
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
    def get_data(self):
        print("Button clicked!")
        print(self.thread)

        try:
            self.read_credentials()
            res = self.fetch_information()
            return res
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
    
    # direct HTTP call from class variables
    def fetch_information(self):
        req.packages.urllib3.disable_warnings()
        login_url = "https://103.120.30.61/Erp/Auth"
        attendance_url = "https://103.120.30.61/Student/MyAttendanceDetail"
        timetable_url = "https://103.120.30.61/Student/MyTimeTable"
        notices_url = "https://103.120.30.61/Student"
        headers = {'host': 'erp.psit.ac.in', 'Cookie': ''}
        login_data = {"username": self.username, "password": self.password}

        # LOGIN-----------------------------------------------------------------------------------  
        login_res = make_request('post',login_url, headers=headers, data=login_data)
        if login_res['status'] == 'error':
            return f'Error: {login_res["msg"]}'
        
        session_id = login_res['data'].cookies.get("PHPSESSID")
        headers["Cookie"] = f"PHPSESSID={session_id}"
        print('Login Sucesss')

        # ATTENDENCE------------------------------------------------------------------------------
        attendance_res = make_request('get', attendance_url, headers=headers)
        if attendance_res['status'] == 'error':
            return f'Error: {attendance_res["msg"]}'
        
        data = attendance_res['data'].text
        total_lecture = extract_info(data, "Total Lecture : [0-9]*")
        total_absent = extract_info(data, "Total Absent : [0-9]*")
        attendance_percentage = extract_info(data, "Attendance Percentage : [0-9.]*\s%")
        self.thread.progress.emit(['AttenTab',f'{total_lecture}\n{total_absent}\n{attendance_percentage}'])
        
        # TIMETABLE-------------------------------------------------------------------------------
        timetable_res = make_request('get', timetable_url, headers=headers)
        if timetable_res['status'] == 'error':
            return f'Error: {timetable_res["msg"]}'

        soup = BeautifulSoup(timetable_res['data'].text, 'html.parser')
        ttable = soup.select('.danger h5')
        ttlist = []
        if not ttable:
            print('No time table for today')
            self.thread.progress.emit(['TtTab','No timetable for today'])
        else:
            pattern = re.compile(r'\[\s*(.*?)\s*\]')
            for i in range(8):
                matches = pattern.findall(ttable[i].get_text())
                ttlist.append([matches[0],matches[1],matches[2]])
            
            print(ttlist)
            data = ''
            for i in range(len(ttlist)):
                data += f'{i+1}. {ttlist[i][1]:<14} {shorten_name(ttlist[i][0])}\n'
            self.thread.progress.emit(['TtTab',data])

        # NOTICES---------------------------------------------------------------------------------
        notices_res = make_request('get', notices_url, headers=headers)
        if notices_res['status'] == 'error':
            return f'Error: {notices_res["msg"]}'
        
        soup = BeautifulSoup(notices_res['data'].text,'html.parser')
        ntcHTML = soup.select('.table2 > tbody tr')
        notices = []
        for i in range(5):
            ntc = ntcHTML[i].find("a")
            notices.append([ntc.get_text(),ntc['href']])

        print(notices)
        data = ''
        for notice in notices:
            data += f'<li><strong>★</strong><a href="{notice[1]}">{notice[0].capitalize()}</a><br></li>'
        
        self.thread.progress.emit(['NtcTab',data])

        return 'success'
    
def shorten_name(full_name):
    match = re.match(r'^(\S+)', full_name)
    if match:
        first_word = match.group(1)
        return first_word + " " + ' '.join(word[0] + '.' for word in full_name.split()[1:])
    return full_name

def make_request(method,url, **kwargs):
    try: 
        res = req.request(method, url, verify=False, timeout=5, **kwargs)
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
    return match.group(0) if match else "Not found"