
from datetime import date, timedelta
from bs4 import BeautifulSoup
import requests
import json
import pandas as pd

userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0'
addresses = ['8808 Mountain Ridge Dr B, Austin']
def getID(address = '8808 Piney Point Dr B'):
    cookies = {
        'plack_session': 's3~1695581235.46339%3ABQoDAAAAAA%3D%3D%3Aebf9ed2f1c5e196b3f8008f8711d7904db1ce371',
        'recollect-locale': 'en-US',
        'temp-client-id': 'C7CB788A-5B0A-11EE-A0AE-8B242EB98042',
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/json',
        'X-Recollect-Place': 'null',
        'X-Widget-Instance': 'C7CB788A-5B0A-11EE-A0AE-8B242EB98042',
        'X-Widget-Version': '0.11.1695160329',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
        'Referer': 'https://api.recollect.net/w/start?area=Austin&design=logan&service_id=323&api_host=https://api.recollect.net&js_host=https://api.recollect.net&css_host=undefined&service=waste&root_page=place_calendar&parent_url=https%3A%2F%2Fwww.austintexas.gov%2Fmyschedule&locale=en-US&support_mode=false&name=undefined&api_key=&widget_config=%7B%22area%22%3A%22Austin%22%2C%22name%22%3A%22calendar%22%2C%22base%22%3A%22https%3A%2F%2Frecollect.net%22%2C%22third_party_cookie_enabled%22%3Anull%7D&widget_layout=default&cookie=recollect-place&env=prod-us&version=0.11.1695160329',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }

    params = {
        'q': address,
        'locale': 'en-US',
        '_': '1695581235789',
    }

    response = requests.get(
        'https://api.recollect.net/api/areas/Austin/services/323/address-suggest',
        params=params,
        cookies=cookies,
        headers=headers,
    )
    try:
        data = json.loads(response.text)
        place_id = data[0]['place_id']
    except Exception as e:
        try:
            response = json.loads(response.text)
            json.loads(response.text)[0].get('name', None)
        except Exception as e:
            print(e)
            return ""
    
    print(place_id) 
    return place_id

def getSchedule(id = "67054DEA-DF5A-11E8-B930-1A2C682931C6", start = date.today(), end = date.today() + timedelta(days=90)):
    # print(start)
    # print(end)
    cookies = {
    'plack_session': 's2~1695582000.94701%3ABQoDAAAAAA%3D%3D%3Aebf9ed2f1c5e196b3f8008f8711d7904db1ce371',
    'recollect-locale': 'en-US',
    'temp-client-id': '8C303A0C-5B0C-11EE-B396-3D8B80FBCF9F',
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/json',
        'X-Recollect-Place': '67054DEA-DF5A-11E8-B930-1A2C682931C6:323:Austin',
        'X-Widget-Instance': '8C303A0C-5B0C-11EE-B396-3D8B80FBCF9F',
        'X-Widget-Version': '0.11.1695160329',
        'X-Recollect-Locale': 'en-US',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
        'Referer': 'https://api.recollect.net/w/areas/Austin/services/323/pages/place_calendar',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }

    params = {
        'after': str(start),
        'before': str(end),
        'locale': 'en-US',

    }

    response = requests.get(
        'https://api.recollect.net/api/places/'+id+'/services/323/events',
        params=params,
        cookies=cookies,
        headers=headers,
    )
    open("schedule.json", "w").write(response.text)
    try:
        data = json.loads(response.text)
        for event in data["events"]:
            if "BulkItemCollection" in [f["name"] for f in event["flags"]]:
                if "dates" in event["options"]:
                    return event["options"]["dates"]
    except Exception as e:
        print(e)
        return None


def sampleAddresses(file_name,file_name_2, count=20):
    address_df = pd.read_csv(file_name)
    sample_df = address_df.sample(n=count)
    sample_df.insert(loc=0, column='TRASH_DATE', value=None)
    for i, row in sample_df.iterrows():
        address_s = row['FULL_STREET_NAME']
        trash_date = getSchedule(getID(address_s))
        sample_df.at[i, 'TRASH_DATE'] = trash_date
    sample_df = sample_df.dropna(subset=['TRASH_DATE'])    
    sample_df.to_csv(file_name_2)


def main():
    # print(getSchedule(getID('2103 Robinhood Trl, Austin')))
    sampleAddresses("Addresses.csv","sample.csv", 1000)

if __name__ == "__main__":
    main()
    