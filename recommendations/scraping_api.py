import os
from bs4 import BeautifulSoup
import requests
import requests_cache

requests_cache.install_cache(include_get_headers=False)


HEADERS = {
    "Host": "api.fotocasa.es",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    #"Referer": "https://www.fotocasa.es/es/comprar/viviendas/lleida-capital/todas-las-zonas/l/2",
    "Origin": "https://www.fotocasa.es"
}

def api_query(json_location_segments, page_number):
    ids = json_location_segments['ids']
    latitude = json_location_segments['coordinates']['latitude']
    longitude = json_location_segments['coordinates']['longitude']
    request_location = f"https://api.fotocasa.es/PropertySearch/Search?combinedLocationIds={ids}&culture=es-ES&hrefLangCultures=ca-ES%3Bes-ES%3Bde-DE%3Ben-GB&isMap=false&isNewConstruction=false&latitude={latitude}&longitude={longitude}&pageNumber=2&platformId=1&sortOrderDesc=true&sortType=bumpdate&transactionTypeId=1&propertyTypeId=2"
    out = requests.get(request_location, headers=HEADERS)
    return out.json()

def api_query_single(id):
    request_location = f"https://api.fotocasa.es/PropertySearch/Property?locale=es-ES&transactionType=1&periodicityId=0&id={id}"
    out = requests.get(request_location, headers=HEADERS)
    return out.json()

def request_location_segments(location):
    request_location = f"https://api.fotocasa.es/PropertySearch/UrlLocationSegments?location={location}&zone=todas-las-zonas"
    out = requests.get(request_location, headers=HEADERS)
    js = out.json()
    return js

def fotocasa_url_by_id(id):
    single_json = api_query_single(id)
    return f'https://www.fotocasa.es{single_json["detail"]["es"]}'

def real_estate_location(json_location_segments, page_number):
    from recommendations.middle_to_model import RealEstate
    js = api_query(json_location_segments, page_number)
    return list(map(RealEstate, js['realEstates']))


def get_features_photo(url):
    #We've removed real_estate_global_v2, since we're not using it yet
    request_location = f'https://api-eu.restb.ai/vision/v2/multipredict?model_id=re_features_v3,re_appliances&image_url={url}&client_key={os.environ["RESTBAI_API"]}'
    js = requests.get(request_location).json()
    assert js['error'] == 'false'
    solutions = js['response']['solutions']
    features = []
    for detection in solutions['re_features_v3']['detections']:
        content = detection['label']
        features.append(content)

    appliances = []
    for detection in solutions['re_appliances']['detections']:
        content = detection['label']
        appliances.append(content)
    
    return features, appliances

def count_feature_photos(urls):
    MAX_PER_IMAGE = 4
    TOTAL_MAX = 8
    features = 0
    appliances = 0
    url_with_errors = 0
    for url in urls:
        try:
            f, a = get_features_photo(url)
        except Exception:
            url_with_errors += 1
            print(f'Error on restbai on url {url}')
            continue
        features += min(len(f), MAX_PER_IMAGE)
        appliances += min(len(a), MAX_PER_IMAGE)
        return features, appliances
    number_succes_urls = len(urls) - url_with_errors
    assert number_succes_urls >= 0
    if number_succes_urls == 0:
        return 0, 0
    return min(features / number_succes_urls, TOTAL_MAX), min(appliances / number_succes_urls, TOTAL_MAX)