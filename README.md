# ErpSnap2

ErpSnap2 is a widget application that provides a one-click interface to view the latest information from the PSIT ERP. It saves time by directly fetching data from APIs, allowing users to quickly access the information they need.

## Features

| Feature | Status |
|-|-|
| Draggable widget | ✔️ |
| Does not appears in taskbar | ✔️ |
| Installation file created | ✔️ |
| Aut0ostarts on Windows boot | ✔️ |
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
>Consider using `urllib3` instead of `requests` library to reduce third party dependency requirements.

## Installation FAQ

#### How do I install ErpSnap2?

1. Download the Latest Release: Visit the [latest release](https://github.com/ashishjii/ErpSnap/releases/latest) page on GitHub and download the ErpSnap setup file.
2. Run the Setup: Double-click the downloaded file (ErpSnapSetup.exe) to start installation.
3. Once the installation is complete, you can launch ErpSnap from the Start menu or desktop shortcut.
4. On initial launch, click the refresh button in the top-right corner to enter credentials.

#### I'm seeing a Windows Defender SmartScreen warning. What should I do?

If you encounter a Windows Defender SmartScreen warning, click on "More info" and then click "Run anyway". This warning appears because the program is not digitally signed with an **Extended Validation (EV) code signing certificate**, which costs around $300-$800. Rest assured, ErpSnap is not a virus.

#### How do I exit the app?

To exit the application, click on the info button located at the top right corner of the screen, then click "Exit application".

#### I entered my username and details incorrectly. What should I do?

If you've entered your username and/or details incorrectly, you can reset them by deleting the credentials file located at `%AppData%/ErpSnap`. To do this, open your file manager and copy-paste the provided location into the address bar. After deleting the file, restart the application, and you will be prompted to enter your credentials again.

## Contributing

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

## License

This project is licensed under the Apache-2.0 License - see the [LICENSE](LICENSE) file for details.

