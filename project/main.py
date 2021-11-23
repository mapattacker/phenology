from plotter import plot_phenology
from scrapers.flickr import flickr_images_query

species = "Cratoxylum maingayi"
df = flickr_images_query(species, limit=200, njobs=20)
plot_phenology(df, species, save_dir="output", display=False)