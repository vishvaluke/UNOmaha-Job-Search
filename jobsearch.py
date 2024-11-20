import os
import re
import requests
from bs4 import BeautifulSoup
from twilio.rest import Client
from typing import List, Optional, Dict

# Constants
URL = "https://unomaha.peopleadmin.com/postings/search?sort=225+desc"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36"
LAST_POSTING_FILE = "last_posting_id.txt"

def get_posting_ids() -> List[int]:
    """Fetch and parse posting IDs from the job portal."""
    headers = {"User-Agent": USER_AGENT}
    try:
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching job postings: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a', href=True)
    
    posting_ids = set()
    for link in links:
        href = link.get('href', '')
        if 'posting_id=' in href:
            match = re.search(r'postings\?posting_id=(\d+)', href)
            if match:
                posting_ids.add(int(match.group(1)))
        
        id_attr = link.get('id', '')
        if id_attr.startswith('bookmark_posting_'):
            posting_id = int(id_attr.split('_')[-1])
            posting_ids.add(posting_id)
    
    return sorted(posting_ids, reverse=True)

def read_last_posting_id() -> int:
    """Read the last saved posting ID from a file."""
    if os.path.exists(LAST_POSTING_FILE):
        try:
            with open(LAST_POSTING_FILE, 'r') as file:
                return int(file.read().strip())
        except (IOError, ValueError):
            print("Error reading last posting ID. Defaulting to 0.")
    return 0

def save_latest_posting_id(posting_id: int):
    """Save the latest posting ID to a file."""
    try:
        with open(LAST_POSTING_FILE, 'w') as file:
            file.write(str(posting_id))
    except IOError as e:
        print(f"Error saving last posting ID: {e}")

def send_whatsapp_message(message: str):
    """Send a WhatsApp message using Twilio."""
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    from_whatsapp = os.environ['TWILIO_WHATSAPP_FROM']
    to_whatsapp = os.environ['TWILIO_WHATSAPP_TO']

    if not all([account_sid, auth_token, from_whatsapp, to_whatsapp]):
        print("Twilio credentials are not properly set.")
        return

    try:
        client = Client(account_sid, auth_token)
        msg = client.messages.create(
            from_=from_whatsapp,
            to=to_whatsapp,
            body=message
        )
        print("WhatsApp message sent:", msg.sid)
    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")

def get_job_details(posting_id: int) -> Optional[Dict[str, str]]:
    """Fetch and extract details of a job posting."""
    job_url = f"https://unomaha.peopleadmin.com/postings/{posting_id}"
    headers = {"User-Agent": USER_AGENT}
    
    try:
        response = requests.get(job_url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching job details for posting ID {posting_id}: {e}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    def get_text(tag: str) -> str:
        th = soup.find('th', text=tag)
        return th.find_next('td').get_text(strip=True) if th else 'Not available'

    return {
        'job_title': get_text('Job Title'),
        'essential_functions': get_text('Essential Functions'),
        'required_qualifications': get_text('Required Qualifications'),
        'salary': get_text('Salary'),
        'job_url': job_url
    }

def format_job_message(job_details: Dict[str, str]) -> str:
    """Format the job details into a WhatsApp message."""
    return f"""
*Job Link:* 
{job_details['job_url']}

*Job Title:* 
{job_details['job_title']}

*Required Qualifications:*
{job_details['required_qualifications']}

*Salary:*
{job_details['salary']}
"""

def monitor_site():
    """Monitor the site for new job postings and notify via WhatsApp."""
    current_posting_ids = get_posting_ids()
    if not current_posting_ids:
        print("No job postings found.")
        return
    
    last_posting_id = read_last_posting_id()
    new_postings = [pid for pid in current_posting_ids if pid > last_posting_id]

    if new_postings:
        for posting_id in new_postings:
            job_details = get_job_details(posting_id)
            if job_details:
                message = format_job_message(job_details)
                send_whatsapp_message(message)
        
        save_latest_posting_id(current_posting_ids[0])
    else:
        print("No new postings.")

if __name__ == "__main__":
    monitor_site()
