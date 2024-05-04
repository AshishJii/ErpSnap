# ErpSnap2

>[!IMPORTANT]
>Known bug: window is not scrolling.

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
| Implement loading animation |  |
| Check internet connectivity |  |
| Show last synced time |  |
| Auto-sync data on startup if info exists |  |
| Check if login info is incorrect |  |
| Add option to exit |  |
| Add option to re-enter info |  |

>[!NOTE]
>Consider using `urllib3` instead of `requests` library to reduce third party dependency requirements.

## Installation

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

## Usage

1. Launch the application.
2. If prompted, enter your login credentials and click "Submit".
3. Click the "Refresh" button to fetch data from the backend server.
4. The application will display the fetched data on the screen.

## Contributing

Contributions are welcome! If you'd like to contribute to ErpSnap2, please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the Apache-2.0 License - see the [LICENSE](LICENSE) file for details.

