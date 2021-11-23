import calendar
import os
import matplotlib.pyplot as plt
import pandas as pd


def plot_phenology(df, species, save_dir=None, display=True):
    """plot line graph of when images were taken each mth"""

    # count photos each month
    df = df["taken"].dt.month.value_counts()
    df = pd.DataFrame(df).reset_index()
    df.columns = ["month", "count"]

    # append missing months
    missing_mths = list(set([1,2,3,4,5,6,7,8,9,10,11,12]) ^ set(df["month"]))
    missing_mths = [(i,0) for i in missing_mths]
    df_miss = pd.DataFrame(missing_mths, columns=["month", "count"])

    # convert to month names
    df = df.append(df_miss).sort_values("month").reset_index(drop=True)
    df['month'] = df['month'].apply(lambda x: calendar.month_abbr[x])

    # plot phenology
    plt.style.use('seaborn')
    plt.figure(figsize=(12,5), dpi=150)
    plt.plot(df["month"], df["count"])
    plt.xlabel('Month')
    plt.ylabel('Count')

    if save_dir:
        save_path = os.path.join(save_dir, species+".png")
        plt.savefig(save_path)
    if display:
        plt.show()
    