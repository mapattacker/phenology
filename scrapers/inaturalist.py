import requests
import json
from math import ceil
import pandas as pd

api = "https://api.inaturalist.org/v1/observations"


def get_pages(api, species_id):
    "get total number of pages for a species"
    api = "{}/?taxon_id={}".format(api, species_id)
    res = requests.get(api).content
    res = json.loads(res)
    total_results = res["total_results"]
    per_page = res["per_page"]
    return ceil(total_results / per_page)


def search_observations(api, species_id, pages):
    
    for page in range(1, pages):
        lat_list = []
        long_list = []
        obs_id_list = []
        obs_date_list = []
        photo_list = []

        api_ = "{}/?taxon_id={}&order=desc&order_by=created_at&page={}".format(api, species_id, page)
        res = requests.get(api_).content
        res = json.loads(res)
        observations = res["results"]
        for ob in observations:
            obs_id = ob["id"]
            obs_date = ob["observed_on"]
            lat = ob["geojson"]["coordinates"][1]
            long_ = ob["geojson"]["coordinates"][0]
            photo = ob["identifications"][0]["taxon"]["default_photo"]["medium_url"]
            
            obs_id_list.append(obs_id)
            obs_date_list.append(obs_date)
            lat_list.append(lat)
            long_list.append(long_)
            photo_list.append(photo)

        df = pd.DataFrame({"obs_id": obs_id_list,
                            "obs_date": obs_date_list,
                            "lat": lat_list,
                            "long": long_list,
                            "photo": photo_list})
        print(df)
        # append to dataframe
        # save to csv



if __name__ == "__main__":
    species_id = "209270"
    pages = get_pages(api, species_id)
    search_observations(api, species_id, pages)
