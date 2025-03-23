# OpenHCI 2024 - LINE BOT Backend

> [Demo Video](https://www.youtube.com/shorts/0jSNehWpa8o)

This repository contains the backend for a LINE chatbot developed as part of the 2024 OpenHCI project.



## Setup

### Prerequisites

- A LINE Developers account with a Messaging API channel
- A Firebase project (Realtime DB + Cloud Messaging enabled)
- [Ngrok](https://ngrok.com/) for local webhook testing

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/lynu1818/openhci_linebot.git
   cd openhci_linebot
   ```
2. Install dependencies:
    ```
    pip install -r requirements.txt
    ```
3. Create a .env file in the root directory and set the required environment variables
4. Run the server locally:
    ```
    python app/main.py
    ```
5. Start ngrok:
    ```
    ngrok http http://localhost:8080
    ```
    Then set the ngrok URL as your webhook endpoint in the LINE Developers Console.


## License

This project is licensed under the MIT License – see the [LICENSE](./LICENSE) file for details.
