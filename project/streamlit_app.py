import os
import shutil
from time import time

import altair as alt
import streamlit as st
from stqdm import stqdm as tqdm

from detect import load_model, run
from plotter import phenology_df
from scrapers.flickr import flickr_images_query


# load model
path = os.path.dirname(__file__)
weight_path = os.path.join(path, "weights/best.pt")
model_params = load_model(weights=weight_path)


def altair_chart(df, species):
    """set altair chart configs"""
    # define chart variables
    red = "red"; blue = "#5276A7"
    months = df["month"].tolist()
    max_year = max(df["year_count"].tolist())
    interpolate = "monotone"

    a = alt.Chart(df, title=species, height=400
            ).mark_area(
                point={"filled": True, "fill": blue},
                interpolate=interpolate,
                opacity=0.4,
                color=blue
            ).encode(
                x=alt.X('month', sort=months),
                y=alt.Y('year_count', 
                        axis=alt.Axis(tickMinStep=1,
                        # scale=alt.Scale(domain=[0, max_year+1]),
                        title='total flowering years',
                        titleColor=blue)),
                tooltip=['month', 'year_count']
            )
    b = alt.Chart(df, title=species, height=400
            ).mark_area(
                point={"filled": True, "fill": red},
                interpolate=interpolate,
                opacity=0.2,
                color=red, 
                # size=60
            ).encode(
                x=alt.X('month', sort=months),
                y=alt.Y('photo_count', 
                        axis=alt.Axis(tickMinStep=1, 
                        title='total flowering photos', 
                        titleColor=red)),
                tooltip=['month', 'photo_count']
            )
    c = alt.layer(a, b
            ).resolve_scale(
                y='independent'
            )
    return c


def main():
    st.title("Phenology Generator")
    st.markdown("""A demonstration site to generate phenology graphs from FlickR images.
        First, [generate](https://www.flickr.com/services/api/misc.api_keys.html) a FlickR API access key.
        Then, enter the full species name of the plant, and the number of photos you want to grab from FlickR.
        A classifier will differentiate if the photo contains flowers, 
        and their photo taken date will be used to generate the graph.""")

    key = st.text_input("Flickr API Access Key", type="password")
    species = st.text_input("Species Name")
    limit = st.slider("No. of Photos", min_value=10, max_value=500, value=100, step=10)

    threads = max(10, int(limit/10))
    img_dir = "images" + "_" + str(time()).replace(".","")
    output_dir = "output"

    # func for running prediction in pandas apply
    tqdm.pandas(desc="classifying flowers")
    def run_prediction(url):
        img_name = url.split("/")[-1]
        img_path = os.path.join(img_dir, img_name)

        if os.path.isfile(img_path):
            prediction = run(model_params,
                            source=img_path,
                            conf_thres=0.4,
                            nosave=True)
            return prediction
        else:
            return 0

    if st.button("Start"):
        with st.spinner("Downloading images. Please hold your horses..."):
            df = flickr_images_query(species, 
                    metadata_dir=output_dir, image_dir=img_dir,
                    limit=limit, njobs=threads,
                    FLICKR_ACCESS_KEY=key)
        df["flower"] = df["url"].progress_apply(lambda x: run_prediction(x))
        
        # delete all images after prediction
        shutil.rmtree(img_dir)
        
        total_img = df[df["flower"]==1]
        st.text(f"Total flower images: {len(total_img)}")

        df = phenology_df(df)
        c = altair_chart(df, species)
        st.altair_chart(c, use_container_width=True)
        

if __name__ == "__main__":
    main()