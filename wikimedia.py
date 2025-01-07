import requests
from urllib.parse import urlparse, unquote


def get_wikimedia_url_via_api(commons_url):
    path = urlparse(commons_url).path
    filename = path.split('File:')[-1]
    filename = unquote(filename)
    
    api_url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "imageinfo",
        "iiprop": "url",
        "titles": f"File:{filename}"
    }
    
    try:
        response = requests.get(api_url, params=params)
        data = response.json()      
        pages = data['query']['pages']
        for page_id in pages:
            if 'imageinfo' in pages[page_id]:
                return pages[page_id]['imageinfo'][0]['url']
        return None
    except Exception as e:
        print(f"API hiba: {e}")
        return None