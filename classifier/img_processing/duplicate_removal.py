import os

import imagehash
import pandas as pd
from PIL import Image
from tqdm import tqdm


def gen_hash_table(dir):
    """generate hash list and delete duplicate images"""

    df = pd.DataFrame(columns=["imgpath", "hash"])

    print("generating hash table")
    for path in tqdm(os.listdir(dir)):
        if path.endswith(".jpg"):
            imgpath = os.path.join(dir, path) 
            imageopen = Image.open(imgpath)
            dhash = imagehash.dhash(imageopen)
            df = df.append({'imgpath':imgpath, 'hash':dhash}, ignore_index=True)
    return df


def remove_dup(df):
    """delete images which have same hash"""
    df = df[df["hash"].duplicated(keep="first")]
    del_list = df["imgpath"].tolist()
    print("deleting files")
    for i in tqdm(del_list):
        os.remove(i)



if __name__ == "__main__":
    dir = "../data" 
    df = gen_hash_table(dir)
    remove_dup(df)