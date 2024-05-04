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

        # LOGIN-----------------------------------------------------------------------------------
        # slower, with dns resolution
        # login_url = "https://erp.psit.ac.in/Erp/Auth"
        # login_data = {"username": roll, "password": passwd}
        # login_res = req.post(login_url, data=login_data)
        
        login_url = "https://103.120.30.61/Erp/Auth"
        headers = {'host': 'erp.psit.ac.in'}
        login_data = {"username": self.username, "password": self.password}
        login_res = req.post(login_url, data=login_data, headers=headers, verify=False)

        if login_res.status_code != 200:
            print("Login failed!")
            return login_res.status_code
        
        session_id = login_res.cookies.get("PHPSESSID")
        print('Login Sucesss')

        # ATTENDENCE------------------------------------------------------------------------------
        # slower, with dns resolution
        # attendance_url = "https://erp.psit.ac.in/Student/MyAttendanceDetail"
        # url_headers = {"Cookie": f"PHPSESSID={session_id}"}
        # attendance_res = req.get(attendance_url, headers=url_headers)

        attendance_url = "https://103.120.30.61/Student/MyAttendanceDetail"
        url_headers = {'host': 'erp.psit.ac.in',"Cookie": f"PHPSESSID={session_id}"}
        attendance_res = req.get(attendance_url, headers=url_headers, verify=False)

        if attendance_res.status_code != 200:
            print("Failed to fetch attendance data.")
            return attendance_res.status_code
        
        data = attendance_res.text
        total_lecture = extract_info(data, "Total Lecture : [0-9]*")
        total_absent = extract_info(data, "Total Absent : [0-9]*")
        attendance_percentage = extract_info(data, "Attendance Percentage : [0-9.]*\s%")
        self.thread.progress.emit(['AttenTab',f'{total_lecture}\n{total_absent}\n{attendance_percentage}'])
        
        # TIMETABLE-------------------------------------------------------------------------------
        timetable_url = "https://103.120.30.61/Student/MyTimeTable"
        url_headers = {'host': 'erp.psit.ac.in',"Cookie": f"PHPSESSID={session_id}"}
        timetable_res = req.get(timetable_url, headers=url_headers, verify=False)

        if timetable_res.status_code != 200:
            print("Failed to fetch Timetable data.")
            return timetable_res.status_code

        soup = BeautifulSoup(timetable_res.text, 'html.parser')

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
            for tt in ttlist:
                data += f'{tt[0]}\t{tt[1]}\n'
            self.thread.progress.emit(['TtTab',data])

        # NOTICES---------------------------------------------------------------------------------
        # self.thread.progress.emit("Getting latest Notices...")
        notices_url = "https://103.120.30.61/Student"
        url_headers = {'host': 'erp.psit.ac.in',"Cookie": f"PHPSESSID={session_id}"}
        notices_res = req.get(notices_url, headers=url_headers, verify=False)

        if notices_res.status_code != 200:
            print("Failed to fetch notices data.")
            return notices_res.status_code
        
        soup = BeautifulSoup(notices_res.text,'html.parser')
        ntcHTML = soup.select('.table2 > tbody tr')
        notices = []
        for i in range(5):
            ntc = ntcHTML[i].find("a")
            notices.append([ntc.get_text(),ntc['href']])

        print(notices)

        data = ''
        for notice in notices:
            data += f'<li><a href="{notice[1]}">{notice[0]}</a><br></li>'
        self.thread.progress.emit(['NtcTab',data])

        return 'success'

def extract_info(data, pattern):
    match = re.search(pattern, data)
    return match.group(0) if match else "Not found"