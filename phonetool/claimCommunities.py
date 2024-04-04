import requests
from bs4 import BeautifulSoup
import re

# Insert auth tokens
rails_root = ''
amzn_sso_rfp = ''
amzn_sso_token = ''
csm_sid = ''
sortC = ''
alias = ''

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

def is_community_owned(session, community_url):
    response = session.get(community_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    owned_by_label = soup.find('b', string=re.compile(r'Owned By:?', re.I))
    if not owned_by_label:
        print(f"Unable to find ownership information for community {community_url}")
        return False, None, None

    owned_by = owned_by_label.find_next_sibling()

    # Check if the community has an owner
    if owned_by and owned_by.name == 'a':
        owner_name = owned_by.get_text(strip=True)
        owner_link = owned_by['href']
        return True, owner_name, owner_link
    else:
        return False, None, None

def takeOwnership(session, community_id):
    community_url = f'https://phonetool.amazon.com/communities/{community_id}'
      
    # Check if the community is already owned
    is_owned, owner_name, owner_link = is_community_owned(session, community_url)
    if is_owned:
        print(f"Community {community_id} already has an owner: {owner_name} ({owner_link})")
        return
    
    takeOwnership_url = f'https://phonetool.amazon.com/users/{alias}/icons/{community_id}/add_administrator'
    csrf_token = extract_csrf_token(session, community_url)

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {
        'authenticity_token': csrf_token,
    }

    response = session.post(takeOwnership_url, headers=headers, data=data, allow_redirects=True)
    
    # Check if the request was successful
    if response.status_code == 200:
        print(f"Successfully took ownership of community {community_id}")
    else:
        print(f"Failed to take ownership of community {community_id}. Status code: {response.status_code}")
        print("Response:", response.text)

def list_and_claim_communities(session):
    base_url = 'https://phonetool.amazon.com/communities'
    page = 1

    while True:
        community_ids = []
        response = session.get(f'{base_url}?page={page}')
        soup = BeautifulSoup(response.content, 'html.parser')

        community_divs = soup.find_all('div', class_='community-preview')

        if not community_divs:
            print(f"No more communities found on page {page}. Stopping.")
            break

        for div in community_divs:
            link = div.find('a', href=True)
            if link and '/communities/' in link['href']:
                community_id = link['href'].split('/')[-1]
                community_ids.append(community_id)

        print(f"Collected community IDs on page {page}:", community_ids)

        for community_id in community_ids:
            takeOwnership(session, community_id)

        page += 1

session = login()
list_and_claim_communities(session)
