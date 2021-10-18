import os

import requests


def save_random_image(url, dir_, name):
    """ Generate & save random image

    Args:
        url (str): URL to get random images of a particular size
            https://source.unsplash.com/random/256x256 OR
            https://picsum.photos/256/256/?random
        dir_ (str): directory to store images
        name (str): file name
    """
    response = requests.get(url)
    if response.status_code == 200:
        file_name = f'{name}.jpg'
        file_path = os.path.join(dir_, file_name)
        with open(file_path, 'wb') as f:
            f.write(response.content)


if __name__ == "__main__":
    url = "https://source.unsplash.com/random/256x256"
    url = "https://picsum.photos/256/256/?random"
    dir_ = "../data"

    from joblib import Parallel, delayed
    from tqdm import tqdm
    Parallel(n_jobs=25, backend="threading")(
            delayed(save_random_image)(url, dir_, "picsum"+str(i)) for i in tqdm(range(1000)))
