import requests
from bs4 import BeautifulSoup
import re,os
from twilio.rest import Client

URL = "https://unomaha.peopleadmin.com/postings/search?sort=225+desc"

def get_posting_ids():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36"
    }
  
    response = requests.get(URL, headers=headers)
    if response.status_code != 200:
        print("Failed to fetch the page.")
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

def read_last_posting_id():
    current_directory = os.getcwd()
    
    file_path = os.path.join(current_directory, 'last_posting_id.txt')
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return int(file.read().strip())
    return 0

def save_latest_posting_id(posting_id):
    current_directory = os.getcwd()
    
    file_path = os.path.join(current_directory, 'last_posting_id.txt')
    
    with open(file_path, 'w') as file:
        file.write(str(posting_id))

def send_whatsapp_message(messages):
    account_sid = 'ACb485a2c596addad78e5e7208f9bdd1b4'
    auth_token = '26019843a148ec22daf93120306fc433'
    client = Client(account_sid, auth_token)
    message = client.messages.create(
      from_='whatsapp:+14155238886',
      to='whatsapp:+919489762119',
      body=messages
    )
    print("WhatsApp message sent:", message.sid)

def get_job_details(posting_id):
    job_url = f"https://unomaha.peopleadmin.com/postings/{posting_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36"
    }
    
    # Send HTTP request to fetch the job details page
    response = requests.get(job_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch job details for posting ID {posting_id}")
        return None
    
    # Parse the job details page
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract Job Title
    job_title_tag = soup.find('th', text='Job Title')
    job_title = job_title_tag.find_next('td').get_text(strip=True) if job_title_tag else 'Not available'
    
    # Extract Essential Functions
    essential_functions_tag = soup.find('th', text='Essential Functions')
    essential_functions = essential_functions_tag.find_next('td').get_text(strip=True) if essential_functions_tag else 'Not available'
    
    # Extract Required Qualifications
    required_qualifications_tag = soup.find('th', text='Required Qualifications')
    required_qualifications = required_qualifications_tag.find_next('td').get_text(strip=True) if required_qualifications_tag else 'Not available'
    
    # Extract Salary
    salary_tag = soup.find('th', text='Salary')
    salary = salary_tag.find_next('td').get_text(strip=True) if salary_tag else 'Not available'
    
    return {
        'job_title': job_title,
        'essential_functions': essential_functions,
        'required_qualifications': required_qualifications,
        'salary': salary,
        'job_url': job_url
    }

def format_job_message(job_details):
    message = f"""
*Job Link:* 
{job_details['job_url']}

*Job Title:* 
{job_details['job_title']}

*Required Qualifications:*
{job_details['required_qualifications']}

*Salary:*
{job_details['salary']}
"""
    return message

def monitor_site():
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
                message=format_job_message(job_details)
                send_whatsapp_message(message)
        
        save_latest_posting_id(current_posting_ids[0])
    else:
        print("No new postings.")

monitor_site()