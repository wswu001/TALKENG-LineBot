# TALKENG-LineBot

Here’s a basic `README.md` file for your project based on the code you provided. This file explains the purpose of the project, setup instructions, and usage.

This project is a LINE bot application built using Flask, LINE Messaging API, and NLP models for language translation and audio transcription. It supports:
- Translating Chinese text to English.
- Transcribing audio messages.

---

## Features

- **Text Translation**: Users can translate Chinese text to English using the prefix `\en`.
- **Audio Transcription**: The bot transcribes audio messages into text using pre-trained models.

---

## Requirements

- Python 3.8 or later
- LINE Developer Account (to get your `access_token` and `channel_secret`)

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-repository/line-bot-nlp.git
cd line-bot-nlp
```

### 2. Install Dependencies
Use the provided `requirements.txt` file to install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the project root and add your LINE access token and channel secret:
```plaintext
LINE_ACCESS_TOKEN=your_line_access_token
LINE_CHANNEL_SECRET=your_line_channel_secret
```

### 4. Run the Application
Start the Flask app on your local machine:
```bash
python app.py
```

### 5. Expose the App to the Internet
Use a tunneling service like [ngrok](https://ngrok.com/) to expose your local server to the internet:
```bash
ngrok http 4000
```
Copy the generated public URL and add it as your webhook URL in the LINE Developer Console.

---

## Usage

1. **Text Translation**:
   - Send a text message starting with `\en` followed by Chinese text to translate it into English.

   Example:
   ```
   \en你好，世界
   ```
   Response:
   ```
   [EN] Hello, World
   ```

2. **Audio Transcription**:
   - Send an audio message, and the bot will reply with the transcribed text.
