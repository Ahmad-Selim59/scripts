import requests
from bs4 import BeautifulSoup

#insert auth tokens
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


def list_and_join_communities(session):
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
            join_community(community_id, session)

        page += 1

def join_community(community_id, session):
    community_url = f'https://phonetool.amazon.com/communities/{community_id}'
    join_url = f'https://phonetool.amazon.com/users/{alias}/communities/{community_id}/join'

    csrf_token = extract_csrf_token(session, community_url)

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {
        'authenticity_token': csrf_token,
    }

    response = session.post(join_url, headers=headers, data=data, allow_redirects=True)
    
    # Check if the request was successful
    if response.status_code == 200:
        print(f"Successfully joined community {community_id}")
    else:
        print(f"Failed to join community {community_id}. Status code: {response.status_code}")
        print("Response:", response.text)

session = login()
list_and_join_communities(session)
