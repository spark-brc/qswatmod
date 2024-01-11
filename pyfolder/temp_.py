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

if __name__ == "__main__":
    # wd = "/Users/seonggyu.park/Documents/projects/kokshila/analysis/koksilah_swatmf/SWAT-MODFLOW"
    wd = "D:/Projects/Watersheds/Koksilah/analysis/koksilah_swatmf/SWAT-MODFLOW"
    # outfd = "d:/Projects/Watersheds/Okavango/Analysis/2nd_cali"
    # get_rech_avg_m_df(wd).to_csv(os.path.join(outfd, 'test.csv'))
    obd_file = "dtw_day.obd.csv"
    startDate = "1/1/2009"
    strObd = read_stf_obd(wd, obd_file)
    # output_rch = read_output_rch_data(wd)
    # # try:
    # df = output_rch.loc[30]
    # df.index = pd.date_range(startDate, periods=len(df.stf_sim))
    # # df2 = pd.concat([df, strObd["sub03"]], axis=1)



    print(strObd[strObd.index.duplicated()])
    print(strObd.index)
    # print(strObd.loc[strObd.index.duplicated()==True])

