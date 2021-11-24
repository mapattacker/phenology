import os

from tqdm import tqdm, tqdm_pandas

from detect import load_model, run
from plotter import plot_phenology
from scrapers.flickr import flickr_images_query



def main(species, img_dir, weights, limit, njobs, conf_thres):
    """download flickr plant species photos, detect flower, plot phenology graph"""
    model_params = load_model(weights=weights)
    df = flickr_images_query(species, limit=limit, image_dir=img_dir, njobs=njobs)

    def run_prediction(url):
        img_name = url.split("/")[-1]
        img_path = os.path.join(img_dir, img_name)
        prediction = run(model_params,
                        source=img_path,
                        conf_thres=conf_thres,
                        nosave=True)
        return prediction
    
    tqdm.pandas(desc="classifying flowers")
    df["flower"] = df["url"].progress_apply(lambda x: run_prediction(x))
    plot_phenology(df, species, save_dir="output", display=False)


if __name__ == "__main__":
    species = "Cratoxylum cochinchinense"
    img_dir = "images"
    weights = "model/best.pt"
    njobs = 20
    limit = 250
    conf_thres = 0.4
    
    main(species, img_dir, weights, limit, njobs, conf_thres)