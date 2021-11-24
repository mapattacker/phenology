import os

import altair as alt
import streamlit as st
from stqdm import stqdm as tqdm

from detect import load_model, run
from plotter import phenology_df
from scrapers.flickr import flickr_images_query


def sidebar():
    st.sidebar.title("Change Parameters")
    limit = st.sidebar.slider("No. of Photos", min_value=50, max_value=500, value=100, step=10)
    return limit

def altair_chart(df, species):
    c = alt.Chart(df, title=species, height=400
            ).mark_line().encode(
                x=alt.X('month', sort=df["month"].tolist()),
                y='count', 
                tooltip=['month', 'count']
            )
    return c

def main(model_params):
    st.title("Phenology Generator Demo")
    key = st.text_input("Flickr Access Key", type="password")
    species = st.text_input("Species Name")
    limit = st.slider("No. of Photos", min_value=10, max_value=500, value=100, step=10)

    # limit = sidebar()
    threads = max(10, int(limit/10))
    img_dir = "images"
    output_dir = "output"

    # func for running prediction in pandas apply
    tqdm.pandas(desc="classifying flowers")
    def run_prediction(url):
        img_name = url.split("/")[-1]
        img_path = os.path.join(img_dir, img_name)
        prediction = run(model_params,
                        source=img_path,
                        conf_thres=0.4,
                        nosave=True)
        return prediction

    if st.button("Start"):
        with st.spinner("Downloading images..."):
            df = flickr_images_query(species, 
                    metadata_dir=output_dir, image_dir=img_dir,
                    limit=limit, njobs=threads,
                    FLICKR_ACCESS_KEY=key)
        df["flower"] = df["url"].progress_apply(lambda x: run_prediction(x))

        df = phenology_df(df)
        c = altair_chart(df, species)
        st.altair_chart(c, use_container_width=True)

        

if __name__ == "__main__":
    model_params = load_model(weights="weights/best.pt")
    main(model_params)