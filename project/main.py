import argparse
import os
import shutil

from tqdm import tqdm, tqdm_pandas

from detect import load_model, run
from plotter import phenology_plot
from scrapers.flickr import flickr_images_query



def main(species, 
         img_dir="images",
         metadata_dir="output",
         plot_dir="output",
         limit=200, 
         threads=15,
         weights="weights/best.pt", 
         conf_thres=0.4,
         save_predicted="False"):
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

    # create predicted dir
    if save_predicted == "True":
        nosave = False
        pred_dir = os.path.join("output/predicted")
        shutil.rmtree(pred_dir)
        if not os.path.exists(pred_dir):
            os.mkdir(pred_dir)
            os.mkdir(os.path.join(pred_dir, "flower"))
            os.mkdir(os.path.join(pred_dir, "noflower"))

    # func for running prediction in pandas apply
    def run_prediction(url):
        img_name = url.split("/")[-1]
        img_path = os.path.join(img_dir, img_name)
        
        if os.path.isfile(img_path):
            prediction = run(model_params,
                            source=img_path,
                            conf_thres=conf_thres,
                            nosave=nosave,
                            project=pred_dir)
            return prediction
        else:
            return 0
    
    tqdm.pandas(desc="classifying flowers")
    model_params = load_model(weights=weights)
    df["flower"] = df["url"].progress_apply(lambda x: run_prediction(x))

    if len(df[df["flower"]==1]) > 0:
        phenology_plot(df, species, save_dir=plot_dir, display=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Captcha Prediction')
    parser.add_argument('-s','--species', help='plant species name', required=True)
    parser.add_argument('-l','--limit', help='how many photos to extract', type=int, default=200)
    parser.add_argument('-t','--threads', help='number of threads to query API & download photos', type=int, default=15)
    parser.add_argument('-p','--save_predicted', help='save predicted images', type=str, default=False)
    args = vars(parser.parse_args())

    main(**args)