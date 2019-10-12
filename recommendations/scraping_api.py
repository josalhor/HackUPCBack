from bs4 import BeautifulSoup
import requests
import requests_cache

requests_cache.install_cache()


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

def real_estate_location(json_location_segments, page_number):
    from recommendations.middle_to_model import RealEstate
    js = api_query(json_location_segments, page_number)
    return list(map(RealEstate, js['realEstates']))
