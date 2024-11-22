# Job Posting Notifier 🚀 [![Run Python Script and Commit Changes](https://github.com/vishvaluke/UNOmaha-Job-Search/actions/workflows/main.yml/badge.svg)](https://github.com/vishvaluke/UNOmaha-Job-Search/actions/workflows/main.yml)

This project is a Python-based automation tool that monitors job postings on the [UNOmaha Job Portal](https://unomaha.peopleadmin.com/postings/search?sort=225+desc), extracts new postings, and sends notifications via WhatsApp using Twilio.

---

## Features ✨

- Scrapes job postings and their details using **BeautifulSoup**.
- Tracks new postings and avoids duplicate notifications.
- Sends formatted job details to a WhatsApp number via Twilio.
- Modular, secure, and adheres to commercial coding standards.

---

## Prerequisites ✅

1. **Python**: Install Python 3.8 or higher.
2. **Twilio Account**:
   - Create an account on [Twilio](https://www.twilio.com/).
   - Get your `Account SID`, `Auth Token`, and a WhatsApp-enabled Twilio number.
3. **Environment Variables**:
   - Set the following variables in your system:
     ```bash
     TWILIO_ACCOUNT_SID=<Your Twilio Account SID>
     TWILIO_AUTH_TOKEN=<Your Twilio Auth Token>
     TWILIO_WHATSAPP_FROM=whatsapp:+<Your Twilio WhatsApp Number>
     TWILIO_WHATSAPP_TO=whatsapp:+<Your WhatsApp Number>
     ```
4. **Dependencies**:
   - Install required libraries by running:
     ```bash
     pip install -r requirements.txt
     ```

---

## Installation ⚙️

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/vishvaluke/UNOmaha-Job-Search.git
   cd UNOmaha-Job-Search
