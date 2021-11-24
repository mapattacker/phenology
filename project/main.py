import argparse
import os

from tqdm import tqdm, tqdm_pandas

from detect import load_model, run
from plotter import plot_phenology
from scrapers.flickr import flickr_images_query



def main(species, 
         img_dir="images",
         metadata_dir="output",
         plot_dir="output",
         limit=200, 
         threads=15,
         weights="model/best.pt", 
         conf_thres=0.4):
    """download flickr plant species photos, detect flower, plot phenology graph
    
    species (str): keyword to search photos
    metadata_dir (str): folder where metadata will be stored in csv
    image_dir (str): folder where images will be downloaded to
    plot_dir (str): folder where phenology graph will be downloaded to
    limit (int): set limit on how many photos to extract
    threads (int): number of threads to query API & download photos
    weights (pt): path to yolov5 pytorch model
    conf_thres (float): confidence threshold for object detection"""

    df = flickr_images_query(species, limit=limit, 
            metadata_dir=metadata_dir, image_dir=img_dir, 
            njobs=threads)

    def run_prediction(url):
        img_name = url.split("/")[-1]
        img_path = os.path.join(img_dir, img_name)
        prediction = run(model_params,
                        source=img_path,
                        conf_thres=conf_thres,
                        nosave=True)
        return prediction
    
    tqdm.pandas(desc="classifying flowers")
    model_params = load_model(weights=weights)
    df["flower"] = df["url"].progress_apply(lambda x: run_prediction(x))
    plot_phenology(df, species, save_dir=plot_dir, display=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Captcha Prediction')
    parser.add_argument('-s','--species', help='plant species name', required=True)
    parser.add_argument('-l','--limit', help='how many photos to extract')
    parser.add_argument('-t','--threads', help='number of threads to query API & download photos')
    args = vars(parser.parse_args())

    # species = "Tabebuia rosea"
    # limit = 500
    main(**args)