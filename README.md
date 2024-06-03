# ErpSnap

A widget application that provides a one-click interface to view the latest info from PSIT ERP. It saves time by directly fetching data from APIs, allowing users to quickly access the information they need.

## Installation FAQ

<details open>
<summary>How to install ErpSnap?</summary>
  
1. Download the [latest release](https://github.com/ashishjii/ErpSnap/releases/latest) and install it.
3. After installation, find ErpSnap in the Start menu or use the desktop shortcut.
4. On initial launch, click the refresh button in the top-right corner to input credentials.
</details>

<details>
<summary>I'm seeing a Windows Defender SmartScreen warning. What should I do?</summary>
If you encounter a Windows Defender SmartScreen warning, click on "More info" and then click "Run anyway". This warning appears because the program is not digitally signed with an **Extended Validation (EV) code signing certificate**, which costs around $300-$800. Rest assured, ErpSnap is not a virus.
</details>

<details>
<summary>How do I exit the app?</summary>
To exit the application, click on the info button located at the top right corner of the screen, then click "Exit application".
</details>

<details>
<summary>I entered my username and details incorrectly. What should I do?</summary>
If you've entered your username and/or details incorrectly, you can reset them by deleting the credentials file located at `%AppData%/ErpSnap`. To do this, open your file manager and copy-paste the provided location into the address bar. After deleting the file, restart the application, and you will be prompted to enter your credentials again.
</details>

## Features

| Feature | Status |
|-|-|
| Draggable widget | ✔️ |
| Does not appear in taskbar | ✔️ |
| Installation file created | ✔️ |
| Autostarts on Windows boot | ✔️ |
| Prompt for roll/pass on initial run | ✔️ |
| Move request call to dedicated worker thread | ✔️ |
| Provide progress indicators for logging and data retrieval | ✔️ |
| Start widget on the right side | ✔️ |
| Retrieve absent days and notices(HTML parsing) | ⏳80% |
| Check internet connectivity/slow internet | ✔️ |
| Implement loading animation | ✔️ |
| Add option to exit | ✔️ |
| Show last synced time |  |
| Auto-sync data on startup if info exists | ✔️ |
| Check if login info is incorrect |  |
| Add option to re-enter info |  |

>[!NOTE]
>Consider using `urllib3` instead of `requests` library to reduce third-party dependency requirements.

## Contributing

<details>
<summary>Contribution Guidelines</summary>  

1. Clone the repository:
```bash
git clone https://github.com/AshishJii/ErpSnap.git
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run the application:
```bash
python main.py
```
4. Convert to exe file:
```bash
pyinstaller --noconfirm --onefile --windowed --icon "assets/logo.ico" --name "ErpSnap" --add-data "assets;assets/"  "main.py"
```

#### How to Contribute

- Fork the repository.
- Make your changes in a feature branch.
- Submit a pull request with your changes.
</details>

## License

This project is licensed under the Apache-2.0 License - see the [LICENSE](LICENSE) file for details.
