import pandas as pd
import os

def read_stf_obd(wd, obd_file):
    return pd.read_csv(
        os.path.join(wd, obd_file),
        index_col=0,
        header=0,
        parse_dates=True,
        na_values=[-999, ""]
    )


def read_output_rch_data(wd, colNum=6):
    return pd.read_csv(
        os.path.join(wd, "output.rch"),
        delim_whitespace=True,
        skiprows=9,
        usecols=[1, 3, colNum],
        names=["date", "filter", "stf_sim"],
        index_col=0
    )
