import requests
from bs4 import BeautifulSoup
import concurrent.futures
import requests
import json

#insert auth tokens and together.ai API key
rails_root = ''
amzn_sso_rfp = ''
amzn_sso_token = ''
csm_sid = ''
sortC = ''
alias = ''
apiKey = ""

initial_instruction = """
Based off of the following prupose of the award write a concise reason on my behalf as to why I am requesting the award with a valid reason:

"""

def login():
    session = requests.Session()
    cookies = {
        '_rails-root_session': rails_root,
        'amzn_sso_rfp': amzn_sso_rfp,
        'amzn_sso_token': amzn_sso_token,
        'csm-sid': csm_sid,
        'sort': sortC
    }
    session.cookies.update(cookies)
    return session

def extract_csrf_token(session, url):
    # Fetch the page that contains the CSRF token
    response = session.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract CSRF token from the meta tag
    csrf_token = soup.find('meta', {'name': 'csrf-token'})['content']
    return csrf_token


def fetch_award_details(session, link):
    href_parts = link.split('/')
    # Check if href_parts has the expected number of elements
    if len(href_parts) < 5:
        print(f"Unexpected link format: {link}")
        return None

    award_id = href_parts[2]
    icon_id = href_parts[4]

    award_url = f'https://phonetool.amazon.com{link}'
    award_page = session.get(award_url)
    award_soup = BeautifulSoup(award_page.content, 'html.parser')
    award_purpose = award_soup.find('p', class_='description').text.strip()

    return award_id, icon_id, award_purpose

def list_awards(session):
    base_url = 'https://phonetool.amazon.com/awards'
    page = 1
    awards = []

    while True:
        response = session.get(f'{base_url}?page={page}')
        soup = BeautifulSoup(response.content, 'html.parser')
        award_links = [a['href'] for a in soup.find_all('a', href=True) if '/awards/' in a['href']]

        if not award_links:
            print(f"No more awards found on page {page}. Stopping.")
            break

        with concurrent.futures.ThreadPoolExecutor() as executor:
            awards = [result for result in executor.map(lambda link: fetch_award_details(session, link), award_links) if result]
        
        print(f"Collected awards on page {page}: {awards}")

        # Process each award on the current page
        process_awards(session, awards)

        page += 1

# Making the API call for LLM 
def togetherAPIcall(prompt_with_instruction):
    url = "https://api.together.xyz/inference"

    payload = {
        "model": "togethercomputer/llama-2-70b-chat",
        "prompt": prompt_with_instruction,
        "max_tokens": 80,
        "temperature": 0.7,
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": apiKey
    }

    response = requests.post(url, json=payload, headers=headers)

    response_data = json.loads(response.text)

    # Navigate through the dictionary to extract the text
    bot_response = response_data.get('output', {}).get('choices', [{}])[0].get('text', '').strip()

    return bot_response

def process_awards(session, awards):
    for award_id, icon_id, award_purpose in awards:
        prompt_with_instruction = f"{initial_instruction}\n{award_purpose}"

        request_reason = togetherAPIcall(prompt_with_instruction)

        submit_award_request(session, award_id, icon_id, request_reason)



def submit_award_request(session, award_id, icon_id, request_reason):
    csrf_token_url = f'https://phonetool.amazon.com/awards/{award_id}/award_icons/{icon_id}'
    
    csrf_token = extract_csrf_token(session, csrf_token_url)

    url = f'https://phonetool.amazon.com/users/{alias}/icon_images/{icon_id}/icon_requests'

    data = {
        'utf8': '✓',
        'authenticity_token': csrf_token,
        'icon_request[request_reason]': request_reason
    }

    print(request_reason)

    response = session.post(url, data=data)
    
    if response.status_code == 200:
        print(f"Successfully submitted award request for {award_id} with icon {icon_id}")
    else:
        print(f"Failed to submit award request for {award_id} with icon {icon_id}. Status code: {response.status_code}")
        print("Response:", response.text)


session = login()

# # Test with a single award link (replace with an actual link from your output)
# test_link = '/awards/220017/award_icons/257568'
# award_details = fetch_award_details(session, test_link)
# print(award_details)

list_awards(session)
