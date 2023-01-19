import os
import requests
from dotenv import load_dotenv

load_dotenv()

NETLIFY_TOKEN = os.getenv("NETLIFY_TOKEN")
NETLIFY_SITE_ID = os.getenv("NETLIFY_SITE_ID")
NETLIFY_API_URL = "https://api.netlify.com/api/v1"

headers = {
    'Authorization': f'Bearer {NETLIFY_TOKEN}',
    # 'User-Agent': 'MyApp (ryanccranfill@gmail.com)'
}


def make_script_string(url):
    return f"""<script>
        serverUrl = '{url}';
    </script>"""


def get_sites():
    res = requests.get(f"{NETLIFY_API_URL}/sites", headers=headers)
    return res.json()


def get_snippets(site_id=NETLIFY_SITE_ID):
    res = requests.get(f"{NETLIFY_API_URL}/sites/{site_id}/snippets", headers=headers)
    return res.json()


def update_snippet(content: dict, snippet_id=0, site_id=NETLIFY_SITE_ID):
    res = requests.put(
        f"{NETLIFY_API_URL}/sites/{site_id}/snippets/{snippet_id}",
        headers=headers,
        json=content,
    )
    return res


def update_server_url(url: str, snippet_id=None):
    print(f"Updating server url to {url}")
    if snippet_id is None:
        print('fetching snippets...')
        try:
            snippets = get_snippets()
            snippet = snippets[0]
        except Exception as e:
            print('error fetching snippets!!!')
            print(e)
            return
    else:
        snippet = {
            'id': snippet_id,
            'title': 'Update Server URL',
            'general': "",
            'general_position': 'head',
            'goal': None,
            'goal_position': 'footer'
        }

    new_content = make_script_string(url)
    snippet['general'] = new_content
    response = update_snippet(snippet)
    if response.status_code == 200:
        print('updating snippet success!')
    else:
        print('updating snippet failed!')
        print(response.json())
    return response


if __name__ == '__main__':
    print(update_server_url('http://beefcake.local:5000').json())
