import pandas as pd
import os

def dummpy(wd):

    output_rch = pd.read_csv(
        os.path.join(wd, "output.rch"),
        delim_whitespace=True,
        skiprows=9,
        usecols=[1, 3, 6],
        names=["date", "filter", "stf_sim"],
        index_col=0
    )
    # try:
    df = output_rch.loc[58]
    # df = df[df['filter'] < 13]
    # print(len(df))
    date_range_freq(df, "1/1/1980")
    # print(df.index)
    # print(df.stf_sim)


def date_range_freq(df, startDate):
    # if self.dlg.radioButton_day.isChecked():
    #     return pd.date_range(startDate, periods=len(df.stf_sim))
    # elif self.dlg.radioButton_month.isChecked():
    df = df[df['filter'] < 13]
    df.index = pd.date_range(startDate, periods=len(df.stf_sim), freq="M")
    print(df)
    # else:
    #     return pd.date_range(startDate, periods=len(df.stf_sim), freq="A")




if __name__ == "__main__":
    wd = "D:\\Projects\\Watersheds\\MiddleBosque\\Analysis\\SWAT-MODFLOWs\\qsm_300\\SWAT-MODFLOW"
    dummpy(wd)