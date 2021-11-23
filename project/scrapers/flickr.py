import argparse
import json
import os
import urllib

import pandas as pd
import requests
from joblib import Parallel, delayed
from tqdm import tqdm


def parse_flickr_json(api):
    """parse json return into dict"""
    contents = requests.get(api).content.decode()
    contents = contents.replace("jsonFlickrApi","").replace("(","").replace(")","")
    contents = json.loads(contents)
    return contents


def get_photo_info(content, flickr_url):
    """get more photo details by using getInfo flickr method"""
    photoid = content["id"]
    conditions = f"&method=flickr.photos.getInfo&photo_id={photoid}"
    flickr_photo_getinfo_search = flickr_url + conditions
    result = parse_flickr_json(flickr_photo_getinfo_search)
    
    username = result["photo"]["owner"]["username"]
    location = result["photo"]["owner"]["location"]
    posted = result["photo"]["dates"]["posted"]
    taken = result["photo"]["dates"]["taken"]

    result = {"photoid": photoid, "username": username, 
                "location": location, "ownerid": content["owner"],
                "title": content["title"], "url": content.get("url_l"),
                "posted": posted, "taken": taken}
    return result


def download_photo(url, download_folder):
    """download image from flickR"""
    img_name = url.split("/")[-1]
    img_path = os.path.join(download_folder, img_name)
    urllib.request.urlretrieve(url, img_path)


def flickr_images_query(query, limit, 
        metadata_folder="data", 
        download_folder="../img", 
        njobs=10):
    """Download flickr images into local drive
    Read from FLICKR official API Docs:
    1) API Docs on Search: https://www.flickr.com/services/api/flickr.photos.search.html
    2) API Testing Site: https://www.flickr.com/services/api/explore/flickr.photos.search
    3) Sample API Query: https://api.flickr.com/services/rest/?format=json&api_key=<apikey>&method=flickr.photos.search&sort=relevance&text=<text>&extras=url_l&per_page=100
    
    Args
    ----
    text (str): keyword to search photos
    folder (str): folder where images will be downloaded & stored in
    limit (int): set limit on how many photos to extract
    njobs (int): number of threads
    """

    FLICKR_ACCESS_KEY = os.environ["FLICKR_ACCESS_KEY"]

    # search photo based on species
    flickr_url = f"https://api.flickr.com/services/rest/?format=json&sort=relevance&api_key={FLICKR_ACCESS_KEY}"
    conditions = f"&method=flickr.photos.search&text={query}&extras=url_l&per_page={limit}"
    flickr_photo_search = flickr_url + conditions
    contents = parse_flickr_json(flickr_photo_search)
    contents = contents["photos"]["photo"]

    # get more details for each photo
    # multi-threading
    compile_list = Parallel(n_jobs=njobs, backend="threading")(
            delayed(get_photo_info)(content, flickr_url) for content in tqdm(contents, desc="get photo details"))

    df = pd.DataFrame(compile_list)
    # download metadata
    if metadata_folder:
        df.dropna(subset=["url"],inplace=True) 
        df.to_csv("test.csv", index=False)

    # download images
    if download_folder:
        urls = df["url"].tolist()
        compile_list = Parallel(n_jobs=njobs, backend="threading")(
            delayed(download_photo)(url, download_folder) for url in tqdm(urls, desc="download images"))
    
    print("FlickR download complete")
    


if __name__ == "__main__":

    # query = args["query"]
    # output = args["output"]
    # limit = args["limit"]
    query = "Cratoxylum formosum"
    limit = 50

    flickr_images_query(query, limit)
    