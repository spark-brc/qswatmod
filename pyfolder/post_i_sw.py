# -*- coding: utf-8 -*-
from builtins import str
from qgis.PyQt import QtCore, QtGui, QtSql
from qgis.core import QgsProject
import datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.dates as mdates
# import numpy as np
import glob
import shutil
import posixpath
import ntpath
import os
import pandas as pd
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from qgis.PyQt.QtCore import QSettings, QFileInfo, QVariant


def plot_stf(self, selected_ts):
    dark_theme = self.dlg.checkBox_darktheme.isChecked()
    plt.style.use('dark_background') if dark_theme else plt.style.use('default')

    QSWATMOD_path_dict = self.dirs_and_paths()
    stdate, eddate, stdate_warmup, eddate_warmup = self.define_sim_period()
    wd = QSWATMOD_path_dict['SMfolder']
    startDate = stdate_warmup.strftime("%m/%d/%Y")
    endDate = eddate_warmup.strftime("%m/%d/%Y")
    colNum = 6  # get flow_out
    outletSubNum = int(self.dlg.comboBox_sub_number.currentText())
    stf_obd_nam = self.dlg.comboBox_stf_obd.currentText()
    # selected_ts = self.dlg.comboBox_SD_timeStep.currentText()
    # plot
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.set_ylabel(r'Stream Discharge $[m^3/s]$', fontsize=8)
    ax.tick_params(axis='both', labelsize=8)
    if self.dlg.checkBox_stream_obd.isChecked():
        plot_stf_obd(self, ax, wd, stf_obd_nam, startDate, outletSubNum, selected_ts)
    else:
        plot_simulated(self, ax, wd, outletSubNum, startDate, selected_ts)
    plt.legend(fontsize=8, loc="lower right", ncol=2, bbox_to_anchor=(1, 1))
    plt.show()


def read_output_rch_stf(self, wd, colNum=6):
    output_rch = pd.read_csv(
        os.path.join(wd, "output.rch"),
        delim_whitespace=True,
        skiprows=9,
        usecols=[1, 3, colNum],
        names=["date", "filter", "stf_sim"],
        index_col=0
    )
    return output_rch

def read_stf_obd(self, wd, stf_obd_nam):
    stf_obd = pd.read_csv(
        os.path.join(wd, stf_obd_nam),
        index_col=0,
        header=0,
        parse_dates=True,
        na_values=[-999, ""]
    )
    return stf_obd

def plot_stf_obd(self, ax, wd, stf_obd_nam, startDate, outletSubNum, selected_ts):
    strObd = read_stf_obd(self, wd, stf_obd_nam)
    output_rch = read_output_rch_stf(self, wd)
    sub_ob = self.dlg.comboBox_SD_obs_data.currentText()
    try:
        df = output_rch.loc[outletSubNum]
        df = update_index(self, df, startDate)
        df = time_cvt(self, df, selected_ts)
        ax.plot(df.index.values, df.stf_sim.values, c='limegreen', lw=1, label="Simulated")
        df2 = pd.concat([df, strObd[sub_ob]], axis=1)
        df3 = df2.dropna()
        plot_observed_data(self, ax, df3, sub_ob)
    except Exception as e:
        handle_exception(self, ax, str(e))

def plot_simulated(self, ax, wd, outletSubNum, startDate, selected_ts):
    
    output_rch = read_output_rch_stf(self, wd)
    df = output_rch.loc[outletSubNum]
    # try:
    df = update_index(self, df, startDate)
    df = time_cvt(self, df, selected_ts)
    ax.plot(df.index.values, df.stf_sim.values, c='g', lw=1, label="Simulated")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d\n%Y'))
    # except Exception as e:
    #     handle_exception(self, ax, str(e))

def update_index(self, df, startDate):
    if self.dlg.radioButton_day.isChecked():
        df.index = pd.date_range(startDate, periods=len(df.stf_sim))
    elif self.dlg.radioButton_month.isChecked():
        df = df[df['filter'] < 13]
        df.index = pd.date_range(startDate, periods=len(df.stf_sim), freq="M")
    else:
        df.index = pd.date_range(startDate, periods=len(df.stf_sim), freq="A")
    return df

def time_cvt(self, df, selected_ts):
    if self.dlg.radioButton_day.isChecked(): # daily format given
        if selected_ts == "Daily":
            self.df = df
        elif selected_ts == "Monthly":
            self.df = df
            self.df = self.df.resample('M').mean()
        elif selected_ts == "Annual":
            self.df = self.df.resample('A').mean()
        else:
            self.show_error_message()
        return self.df
    elif self.dlg.radioButton_month.isChecked(): # monthly given
        msgBox = QMessageBox()
        msgBox.setText("hoho")
        msgBox.exec_()    
        if selected_ts == "Monthly":
            self.df = df
        elif selected_ts == "Annual":
            self.df = self.df.resample('A').mean()
        else:
            self.show_error_message()
        return self.df
    elif self.dlg.radioButton_year.isChecked() and selected_ts == "Annual": # Annual given
        self.df = df
        return self.df
    else:
        msgBox = QMessageBox()
        msgBox.setText("There was a problem plotting the result!")
        msgBox.exec_()          

def plot_observed_data(self, ax, df3, sub_ob):
    if self.dlg.radioButton_str_obd_pt.isChecked():
        size = float(self.dlg.spinBox_str_obd_size.value())
        ax.scatter(
            df3.index.values, df3[sub_ob].values, c='m', lw=1, alpha=0.5, s=size, marker='x',
            label="Observed", zorder=3
        )
    else:
        ax.plot(
            df3.index.values, df3[sub_ob].values, c='m', lw=1.5, alpha=0.5,
            label="Observed", zorder=3
        )
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d\n%Y'))
    if len(df3[sub_ob]) > 1:
        calculate_metrics(self, ax, df3, sub_ob)
    else:
        display_no_data_message(self, ax)

# NOTE: metrics =======================================================================================
def calculate_metrics(self, ax, df3, sub_ob):
    r_squared = ((sum((df3[sub_ob] - df3[sub_ob].mean()) * (df3.stf_sim - df3.stf_sim.mean())))**2) / (
            (sum((df3[sub_ob] - df3[sub_ob].mean())**2) * (sum((df3.stf_sim - df3.stf_sim.mean())**2)))
    )

    dNS = 1 - (sum((df3.stf_sim - df3[sub_ob])**2) / sum((df3[sub_ob] - (df3[sub_ob]).mean())**2))

    PBIAS = 100 * (sum(df3[sub_ob] - df3.stf_sim) / sum(df3[sub_ob]))

    display_metrics(self, ax, dNS, r_squared, PBIAS)

def display_metrics(self, ax, dNS, r_squared, PBIAS):
    ax.text(
        .01, 0.95, f'Nash-Sutcliffe: {dNS:.4f}',
        fontsize=8, horizontalalignment='left', color='limegreen', transform=ax.transAxes
    )

    ax.text(
        .01, 0.90, f'$R^2$: {r_squared:.4f}',
        fontsize=8, horizontalalignment='left', color='limegreen', transform=ax.transAxes
    )

    ax.text(
        .99, 0.95, f'PBIAS: {PBIAS:.4f}',
        fontsize=8, horizontalalignment='right', color='limegreen', transform=ax.transAxes
    )

def display_no_data_message(self, ax):
    ax.text(
        .01, .95, 'Nash-Sutcliffe: ---',
        fontsize=8, horizontalalignment='left', transform=ax.transAxes
    )

    ax.text(
        .01, 0.90, '$R^2$: ---',
        fontsize=8, horizontalalignment='left', color='limegreen', transform=ax.transAxes
    )

    ax.text(
        .99, 0.95, 'PBIAS: ---',
        fontsize=8, horizontalalignment='right', color='limegreen', transform=ax.transAxes
    )

def handle_exception(self, ax, exception_message):
    ax.text(
        .5, .5, exception_message,
        fontsize=12, horizontalalignment='center', weight='extra bold', color='y', transform=ax.transAxes
    )

