import requests
import os


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
            print("saving: " + file_name)
            f.write(response.content)


if __name__ == "__main__":
    url = "https://picsum.photos/256/256/?random"
    dir_ = "data/flower_not"

    from joblib import Parallel, delayed
    Parallel(n_jobs=20, backend="threading")(
            delayed(save_random_image)(url, dir_, i) for i in range(8000))
