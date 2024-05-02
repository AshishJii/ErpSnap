import os
import requests as req

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
        # slower, with dns resolution
        # login_url = "https://erp.psit.ac.in/Erp/Auth"
        # login_data = {"username": roll, "password": passwd}
        # login_res = req.post(login_url, data=login_data)
        
        self.thread.progress.emit("Logging in...")

        login_url = "https://103.120.30.61/Erp/Auth"
        headers = {'host': 'erp.psit.ac.in'}
        login_data = {"username": self.username, "password": self.password}
        login_res = req.post(login_url, data=login_data, headers=headers, verify=False)

        if login_res.status_code != 200:
            print("Login failed!")
            return None
        
        print('Login Sucesss')
        self.thread.progress.emit("Fetching Attendance...")
        session_id = login_res.cookies.get("PHPSESSID")

        # slower, with dns resolution
        # attendance_url = "https://erp.psit.ac.in/Student/MyAttendanceDetail"
        # url_headers = {"Cookie": f"PHPSESSID={session_id}"}
        # attendance_res = req.get(attendance_url, headers=url_headers)

        attendance_url = "https://103.120.30.61/Student/MyAttendanceDetail"
        url_headers = {'host': 'erp.psit.ac.in',"Cookie": f"PHPSESSID={session_id}"}
        attendance_res = req.get(attendance_url, headers=url_headers, verify=False)

        if attendance_res.status_code != 200:
            print("Failed to fetch attendance data.")
            return None
        
        data = attendance_res.text
        total_lecture = extract_info(data, "Total Lecture : [0-9]*")
        total_absent = extract_info(data, "Total Absent : [0-9]*")
        attendance_percentage = extract_info(data, "Attendance Percentage : [0-9.]*\s%")

        return f'{total_lecture}\n{total_absent}\n{attendance_percentage}'

def extract_info(data, pattern):
    import re
    match = re.search(pattern, data)
    return match.group(0) if match else "Not found"