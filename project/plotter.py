import calendar
import os

import matplotlib.pyplot as plt
import pandas as pd


def phenology_df(df):
    """generate phenology df"""
    
    df = df[df["flower"]==1]
    df["taken"] = pd.to_datetime(df["taken"])
    df["year"] = df["taken"].dt.year
    df["month"] = df["taken"].dt.month

    # count years for each month
    df_year = df.groupby("month")["year"].unique()
    df_year = pd.DataFrame(df_year).reset_index()
    df_year["year_count"] = df_year["year"].apply(lambda x: len(list(x)))
    del df_year["year"]
    df_year.columns = ["month", "year_count"]

    # count photos each month
    df_photo = df["month"].value_counts()
    df_photo = pd.DataFrame(df_photo).reset_index()
    df_photo.columns = ["month", "photo_count"]

    # append missing months & join 
    df = pd.merge(df_year, df_photo, how='outer', on='month')
    missing_mths = list(set([1,2,3,4,5,6,7,8,9,10,11,12]) ^ set(df["month"]))
    missing_mths = [(i,0,0) for i in missing_mths]
    df_miss = pd.DataFrame(missing_mths, columns=["month", "year_count", "photo_count"])

    # convert to month names
    df = df.append(df_miss).sort_values("month").reset_index(drop=True)
    df['month'] = df['month'].apply(lambda x: calendar.month_abbr[x])

    return df
    

def phenology_plot(df, species, save_dir=None, display=True):
    """plot line graph of when images were taken each mth"""
    df = phenology_df(df)

    # plot phenology
    plt.style.use('seaborn')
    plt.figure(figsize=(12,5), dpi=150)
    plt.plot(df["month"], df["count"])
    plt.xlabel('Month')
    plt.ylabel('Count')
    plt.title(species)

    if save_dir:
        save_path = os.path.join(save_dir, species+".png")
        plt.savefig(save_path)
    if display:
        plt.show()