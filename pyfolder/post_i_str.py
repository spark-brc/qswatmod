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

# def read_sub_no(self):
#     for self.layer in list(QgsProject.instance().mapLayers().values()):
#         if self.layer.name() == ("sub (SWAT)"):
#             self.layer = QgsProject.instance().mapLayersByName("sub (SWAT)")[0]
#             feats = self.layer.getFeatures()
#             # get sub number as a list
#             unsorted_subno = [str(f.attribute("Subbasin")) for f in feats]
#             # Sort this list
#             sorted_subno = sorted(unsorted_subno, key=int)
#             ## a = sorted(a, key=lambda x: float(x)
#             self.dlg.comboBox_sub_number.clear()
#             # self.dlg.comboBox_sub_number.addItem('')
#             self.dlg.comboBox_sub_number.addItems(sorted_subno) # in addItem list should contain string numbers


# def read_stf_obd(self):
#     QSWATMOD_path_dict = self.dirs_and_paths()
#     if self.dlg.checkBox_stream_obd.isChecked():
#         self.dlg.frame_sd_obd.setEnabled(True)
#         self.dlg.radioButton_str_obd_line.setEnabled(True)
#         self.dlg.radioButton_str_obd_pt.setEnabled(True)
#         self.dlg.spinBox_str_obd_size.setEnabled(True)
#         get_stf_obds(self)
#         if self.dlg.comboBox_stf_obd.count()==0:
#             msgBox = QMessageBox()
#             msgBox.setWindowIcon(QtGui.QIcon(':/QSWATMOD2/pics/sm_icon.png'))
#             msgBox.setWindowTitle("No 'streamflow.obd' file found!")
#             msgBox.setText("Please, provide streamflow measurement files!")
#             msgBox.exec_()
#             self.dlg.checkBox_stream_obd.setChecked(0)  
#             self.dlg.frame_sd_obd.setEnabled(False)
#             self.dlg.radioButton_str_obd_line.setEnabled(False)
#             self.dlg.radioButton_str_obd_pt.setEnabled(False)
#             self.dlg.spinBox_str_obd_size.setEnabled(False)
#     else:
#         self.dlg.comboBox_stf_obd.clear()
#         self.dlg.comboBox_SD_obs_data.clear()
#         self.dlg.frame_sd_obd.setEnabled(False)
#         self.dlg.radioButton_str_obd_line.setEnabled(False)
#         self.dlg.radioButton_str_obd_pt.setEnabled(False)
#         self.dlg.spinBox_str_obd_size.setEnabled(False)


# def get_stf_obds(self):
#     QSWATMOD_path_dict = self.dirs_and_paths()
#     stf_obd_files = [
#         os.path.basename(file) for file in glob.glob(str(QSWATMOD_path_dict['SMfolder']) + '/stf*.obd.csv')
#         ]
#     self.dlg.comboBox_stf_obd.clear()
#     self.dlg.comboBox_stf_obd.addItems(stf_obd_files)

# def get_stf_cols(self):
#     if self.dlg.checkBox_stream_obd.isChecked():
#         QSWATMOD_path_dict = self.dirs_and_paths()
#         wd = QSWATMOD_path_dict['SMfolder']
#         stf_obd_nam = self.dlg.comboBox_stf_obd.currentText()

#         stf_obd = pd.read_csv(
#                         os.path.join(wd, stf_obd_nam),
#                         index_col=0,
#                         parse_dates=True)

#         stf_obd_list = stf_obd.columns.tolist()
#         self.dlg.comboBox_SD_obs_data.clear()
#         self.dlg.comboBox_SD_obs_data.addItems(stf_obd_list)


"""
Export data only selected
"""
def export_sd_daily(self):

    QSWATMOD_path_dict = self.dirs_and_paths()
    stdate, eddate, stdate_warmup, eddate_warmup = self.define_sim_period() 
    wd = QSWATMOD_path_dict['SMfolder']
    outfolder = QSWATMOD_path_dict['exported_files']
    startDate = stdate_warmup.strftime("%m/%d/%Y")
    endDate = eddate_warmup.strftime("%m/%d/%Y")
    colNum = 6 # get flow_out
    outletSubNum = int(self.dlg.comboBox_sub_number.currentText())
    stf_obd_nam = self.dlg.comboBox_stf_obd.currentText()

    # Add info
    from datetime import datetime
    version = "version 2.7."
    time = datetime.now().strftime('- %m/%d/%y %H:%M:%S -')

    if self.dlg.checkBox_stream_obd.isChecked():
        strObd = pd.read_csv(
                            os.path.join(wd, stf_obd_nam),
                            index_col = 0,
                            header = 0,
                            parse_dates=True,
                            na_values=[-999, ""])

        output_rch = pd.read_csv(
                                os.path.join(wd, "output.rch"),
                                delim_whitespace=True,
                                skiprows = 9,
                                usecols = [1, 3, colNum],
                                names = ["date", "filter", "streamflow_sim"],
                                index_col = 0)

        sub_ob = self.dlg.comboBox_SD_obs_data.currentText()

        try:
        # if (output_rch.index[0] == 1):
            df = output_rch.loc[outletSubNum]

            # Based on SWAT Time Step condition
            if self.dlg.radioButton_day.isChecked():
                df.index = pd.date_range(startDate, periods=len(df.streamflow_sim))
            elif self.dlg.radioButton_month.isChecked():
                df = df[df['filter'] < 13]
                df.index = pd.date_range(startDate, periods=len(df.streamflow_sim), freq="M")
            else:
                df.index = pd.date_range(startDate, periods=len(df.streamflow_sim), freq="A")

            df2 = pd.concat([df, strObd[sub_ob]], axis=1)
            df3 = df2.dropna()
    
            if (len(df3[sub_ob]) > 1):

                ## R-squared
                r_squared = (
                    (
                        (sum((df3[sub_ob] - df3[sub_ob].mean())*(df3.streamflow_sim-df3.streamflow_sim.mean())))**2
                    )
                    /
                    (
                        (sum((df3[sub_ob] - df3[sub_ob].mean())**2) * (sum((df3.streamflow_sim-df3.streamflow_sim.mean())**2))
                    ))
                )

                ##Nash–Sutcliffe (E) model efficiency coefficient ---used up in the class
                dNS = 1 - (sum((df3.streamflow_sim - df3[sub_ob])**2) /
                    sum((df3[sub_ob] - (df3[sub_ob]).mean())**2))

                ## PBIAS
                PBIAS = 100*(sum(df3[sub_ob] - df3.streamflow_sim) / sum(df3[sub_ob]))

            # ------------ Export Data to file -------------- #
            msgBox = QMessageBox()
            msgBox.setWindowIcon(QtGui.QIcon(':/QSWATMOD2/pics/sm_icon.png'))
            msgBox.setWindowTitle("Exported!") 

            if self.dlg.radioButton_day.isChecked():
                with open(os.path.join(outfolder, "swatmf_reach(" + str(outletSubNum) + ")"+"_ob("+ str(sub_ob)+")_daily.txt"), 'w') as f:
                    f.write("# swatmf_reach(" + str(outletSubNum) + ")"+"_ob("+ str(sub_ob)
                            +")_daily.txt is created by QSWATMOD2 plugin "+ version + time + "\n")
                    df3.drop('filter', 1).to_csv(f, index_label = "Date", sep = '\t', float_format='%10.4f', line_terminator='\n', encoding='utf-8')
                    f.write('\n')
                    f.write("# Statistics\n")
                    f.write("Nash–Sutcliffe: " + str('{:.4f}'.format(dNS) + "\n"))
                    f.write("R-squared: " + str('{:.4f}'.format(r_squared) + "\n"))
                    f.write("PBIAS: " + str('{:.4f}'.format(PBIAS) + "\n"))
                msgBox.setText(
                            "'swatmf_reach(" + str(outletSubNum) + ")"+"_ob("+ str(sub_ob)
                            + ")_daily.txt' file is exported to your 'exported_files' folder!")
                msgBox.exec_()
            elif self.dlg.radioButton_month.isChecked():
                with open(os.path.join(outfolder, "swatmf_reach(" + str(outletSubNum) + ")"+"_ob("+ str(sub_ob)+")_monthly.txt"), 'w') as f:
                    f.write("# swatmf_reach(" + str(outletSubNum) + ")"+"_ob("+ str(sub_ob)
                            + ")_monthly.txt is created by QSWATMOD2 plugin "+ version + time + "\n")
                    df3.drop('filter', 1).to_csv(f, index_label = "Date", sep = '\t', float_format='%10.4f', line_terminator='\n', encoding='utf-8')
                    f.write('\n')
                    f.write("# Statistics\n")
                    f.write("Nash–Sutcliffe: " + str('{:.4f}'.format(dNS) + "\n"))
                    f.write("R-squared: " + str('{:.4f}'.format(r_squared) + "\n"))
                    f.write("PBIAS: " + str('{:.4f}'.format(PBIAS) + "\n"))
                msgBox.setText(
                            "'swatmf_reach(" + str(outletSubNum) + ")"+"_ob("+ str(sub_ob)
                            + ")_monthly.txt' file is exported to your 'exported_files' folder!")
                msgBox.exec_()
            else:
                with open(os.path.join(outfolder, "swatmf_reach(" + str(outletSubNum) + ")"+"_ob("+ str(sub_ob)+")_annual.txt"), 'w') as f:
                    f.write("# swatmf_reach(" + str(outletSubNum) + ")"+"_ob("+ str(sub_ob)
                            + ")_monthly.txt is created by QSWATMOD2 plugin "+ version + time + "\n")
                    df3.drop('filter', 1).to_csv(f, index_label = "Date", sep = '\t', float_format='%10.4f', line_terminator='\n', encoding='utf-8')
                    f.write('\n')
                    f.write("# Statistics\n")
                    f.write("Nash–Sutcliffe: " + str('{:.4f}'.format(dNS) + "\n"))
                    f.write("R-squared: " + str('{:.4f}'.format(r_squared) + "\n"))
                    f.write("PBIAS: " + str('{:.4f}'.format(PBIAS) + "\n"))
                msgBox.setText(
                            "'swatmf_reach(" + str(outletSubNum) + ")"+"_ob("+ str(sub_ob)
                            + ")_annual.txt' file is exported to your 'exported_files' folder!")
                msgBox.exec_()
        except:
            msgBox = QMessageBox()
            msgBox.setWindowIcon(QtGui.QIcon(':/QSWATMOD2/pics/sm_icon.png'))
            msgBox.setWindowTitle("Not Ready!")
            msgBox.setText("Running the simulation for a warm-up period!")
            msgBox.exec_()
    else:
        output_rch = pd.read_csv(
                    os.path.join(wd, "output.rch"),
                    delim_whitespace=True,
                    skiprows=9,
                    usecols=[1, 3, colNum],
                    names=["date", "filter", "streamflow_sim"],
                    index_col=0)
        # try:
        df = output_rch.loc[outletSubNum]
        if self.dlg.radioButton_day.isChecked():
            df.index = pd.date_range(startDate, periods=len(df.streamflow_sim))
        elif self.dlg.radioButton_month.isChecked():
            df = df[df['filter'] < 13]
            df.index = pd.date_range(startDate, periods=len(df.streamflow_sim), freq="M")
        else:
            df.index = pd.date_range(startDate, periods=len(df.streamflow_sim), freq="A")

        # ------------ Export Data to file -------------- #
        with open(os.path.join(outfolder, "swatmf_reach(" + str(outletSubNum) + ")_daily"+".txt"), 'w') as f:
            f.write("# swatmf_reach(" + str(outletSubNum) + ")_daily"+".txt is created by QSWATMOD2 plugin "+ version + time + "\n")
            df.drop('filter', 1).to_csv(f, index_label="Date", sep='\t', float_format='%10.4f', line_terminator='\n', encoding='utf-8')
            f.write('\n')
            f.write("# Statistics\n")
            # f.write("Nash–Sutcliffe: " + str('{:.4f}'.format(dNS) + "\n"))
            f.write("Nash–Sutcliffe: ---\n")
            f.write("R-squared: ---\n")
            f.write("PBIAS: ---\n")

        msgBox = QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon(':/QSWATMOD2/pics/sm_icon.png'))
        msgBox.setWindowTitle("Exported!")
        msgBox.setText("'swatmf_reach(" + str(outletSubNum)+")_daily.txt' file is exported to your 'exported_files' folder!")
        msgBox.exec_()

        # except:
        #     msgBox = QMessageBox()
        #     msgBox.setWindowIcon(QtGui.QIcon(':/QSWATMOD2/pics/sm_icon.png'))
        #     msgBox.setWindowTitle("Not Ready!")
        #     msgBox.setText("Nothing to write down right now!")
        #     msgBox.exec_()


def export_sd_monthly(self):
    from qgis.PyQt import QtCore, QtGui, QtSql
    QSWATMOD_path_dict = self.dirs_and_paths()
    stdate, eddate, stdate_warmup, eddate_warmup = self.define_sim_period() 
    wd = QSWATMOD_path_dict['SMfolder']
    outfolder = QSWATMOD_path_dict['exported_files']
    startDate = stdate_warmup.strftime("%m/%d/%Y")
    endDate = eddate_warmup.strftime("%m/%d/%Y")
    colNum = 6 # get flow_out
    outletSubNum = int(self.dlg.comboBox_sub_number.currentText())
    stf_obd_nam = self.dlg.comboBox_stf_obd.currentText()
    # Add info
    from datetime import datetime
    version = "version 2.7."
    time = datetime.now().strftime('- %m/%d/%y %H:%M:%S -')

    if self.dlg.checkBox_stream_obd.isChecked():
        strObd = pd.read_csv(
                            os.path.join(wd, stf_obd_nam),
                            index_col = 0,
                            header = 0,
                            parse_dates=True,
                            na_values=[-999, ""])

        output_rch = pd.read_csv(
                            os.path.join(wd, "output.rch"),
                            delim_whitespace=True,
                            skiprows = 9,
                            usecols = [1,colNum],
                            names = ["date", "streamflow_sim"],
                            index_col = 0)
        
        sub_ob = self.dlg.comboBox_SD_obs_data.currentText()

        try:
        # if (output_rch.index[0] == 1):
            df = output_rch.loc[outletSubNum]
            df.index = pd.date_range(startDate, periods=len(df.streamflow_sim))
            dfm = df.resample('M').mean()
            strObdm = strObd.resample('M').mean()
            df2 = pd.concat([dfm, strObdm[sub_ob]], axis = 1)
            df3 = df2.dropna()

            if (len(df3[sub_ob]) > 1):

                ## R-squared
                r_squared = (
                    (
                        (sum((df3[sub_ob] - df3[sub_ob].mean())*(df3.streamflow_sim-df3.streamflow_sim.mean())))**2
                    ) 
                    /
                    (
                        (sum((df3[sub_ob] - df3[sub_ob].mean())**2)* (sum((df3.streamflow_sim-df3.streamflow_sim.mean())**2))
                    ))
                )

                ##Nash–Sutcliffe (E) model efficiency coefficient ---used up in the class
                dNS = 1 - (sum((df3.streamflow_sim - df3[sub_ob])**2) / 
                    sum((df3[sub_ob] - (df3[sub_ob]).mean())**2))

                ## PBIAS
                PBIAS = 100*(sum(df3[sub_ob] - df3.streamflow_sim) / sum(df3[sub_ob]))

            # ------------ Export Data to file -------------- #
            with open(os.path.join(outfolder, "swatmf_reach(" + str(outletSubNum) + ")"+"_ob("+ str(sub_ob)+")_monthly.txt"), 'w') as f:
                f.write("# swatmf_reach(" + str(outletSubNum) + ")"+"_ob("+ str(sub_ob)
                        +")_monthly.txt is created by QSWATMOD2 plugin "+ version + time + "\n")
                df3.to_csv(f, index_label = "Date", sep = '\t', float_format='%10.4f', line_terminator='\n', encoding='utf-8')
                f.write('\n')
                f.write("# Statistics\n")
                f.write("Nash–Sutcliffe: " + str('{:.4f}'.format(dNS) + "\n"))
                f.write("R-squared: " + str('{:.4f}'.format(r_squared) + "\n"))
                f.write("PBIAS: " + str('{:.4f}'.format(PBIAS) + "\n"))

            msgBox = QMessageBox()
            msgBox.setWindowIcon(QtGui.QIcon(':/QSWATMOD2/pics/sm_icon.png'))
            msgBox.setWindowTitle("Exported!")
            msgBox.setText(
                        "'swatmf_reach(" + str(outletSubNum) + ")"+"_ob("+ str(sub_ob)
                        + ")_monthly.txt' file is exported to your 'exported_files' folder!")
            msgBox.exec_()

        except:         
            msgBox = QMessageBox()
            msgBox.setWindowIcon(QtGui.QIcon(':/QSWATMOD2/pics/sm_icon.png'))
            msgBox.setWindowTitle("Not Ready!")
            msgBox.setText("Running the simulation for a warm-up period!")
            msgBox.exec_()
    else:
        output_rch = pd.read_csv(
                                os.path.join(wd, "output.rch"),
                                delim_whitespace=True,
                                skiprows = 9,
                                usecols = [1,colNum],
                                names = ["date", "streamflow_sim"],
                                index_col = 0)
        try:
            df = output_rch.loc[outletSubNum]
            df.index = pd.date_range(startDate, periods=len(df.streamflow_sim))
            dfm = df.resample('M').mean()

            # ------------ Export Data to file -------------- #
            with open(os.path.join(outfolder, "swatmf_reach(" + str(outletSubNum) + ")_monthly"+".txt"), 'w') as f:
                f.write("# swatmf_reach(" + str(outletSubNum) + ")_monthly"+".txt is created by QSWATMOD2 plugin "+ version + time + "\n")
                dfm.to_csv(f, index_label="Date", sep='\t', float_format='%10.4f', line_terminator='\n', encoding='utf-8')
                f.write('\n')
                f.write("# Statistics\n")
                # f.write("Nash–Sutcliffe: " + str('{:.4f}'.format(dNS) + "\n"))
                f.write("Nash–Sutcliffe: ---\n")
                f.write("R-squared: ---\n")
                f.write("PBIAS: ---\n")

            msgBox = QMessageBox()
            msgBox.setWindowIcon(QtGui.QIcon(':/QSWATMOD2/pics/sm_icon.png'))
            msgBox.setWindowTitle("Exported!")
            msgBox.setText("'swatmf_reach(" + str(outletSubNum)+")_monthly.txt' file is exported to your 'exported_files' folder!")
            msgBox.exec_()
        except:
            msgBox = QMessageBox()
            msgBox.setWindowIcon(QtGui.QIcon(':/QSWATMOD2/pics/sm_icon.png'))
            msgBox.setWindowTitle("Not Ready!")
            msgBox.setText("Nothing to write down right now!")
            msgBox.exec_()


def export_sd_mTa(self):
    from qgis.PyQt import QtCore, QtGui, QtSql
    QSWATMOD_path_dict = self.dirs_and_paths()
    stdate, eddate, stdate_warmup, eddate_warmup = self.define_sim_period() 
    wd = QSWATMOD_path_dict['SMfolder']
    outfolder = QSWATMOD_path_dict['exported_files']
    startDate = stdate_warmup.strftime("%m/%d/%Y")
    endDate = eddate_warmup.strftime("%m/%d/%Y")
    colNum = 6 # get flow_out
    outletSubNum = int(self.dlg.comboBox_sub_number.currentText())
    stf_obd_nam = self.dlg.comboBox_stf_obd.currentText()
    # Add info
    from datetime import datetime
    version = "version 2.7."
    time = datetime.now().strftime('- %m/%d/%y %H:%M:%S -')

    if self.dlg.checkBox_stream_obd.isChecked():
        strObd = pd.read_csv(
                            os.path.join(wd, stf_obd_nam),
                            index_col = 0,
                            header = 0,
                            parse_dates=True,
                            na_values=[-999, ""])
        output_rch = pd.read_csv(
                            os.path.join(wd, "output.rch"),
                            delim_whitespace=True,
                            skiprows = 9,
                            usecols = [1,colNum],
                            names = ["date", "streamflow_sim"],
                            index_col = 0)
        
        sub_ob = self.dlg.comboBox_SD_obs_data.currentText()

        try:
        # if (output_rch.index[0] == 1):
            df = output_rch.loc[outletSubNum]
            df.index = pd.date_range(startDate, periods=len(df.streamflow_sim), freq = "M")
            dfa = df.resample('A').mean()
            strObda = strObd.resample('A').mean()
            df2 = pd.concat([dfa, strObda[sub_ob]], axis = 1)
            df3 = df2.dropna()

            if (len(df3[sub_ob]) > 1):

                ## R-squared
                r_squared = (
                    (
                        (sum((df3[sub_ob] - df3[sub_ob].mean())*(df3.streamflow_sim-df3.streamflow_sim.mean())))**2
                    ) 
                    /
                    (
                        (sum((df3[sub_ob] - df3[sub_ob].mean())**2)* (sum((df3.streamflow_sim-df3.streamflow_sim.mean())**2))
                    ))
                )

                ##Nash–Sutcliffe (E) model efficiency coefficient ---used up in the class
                dNS = 1 - (sum((df3.streamflow_sim - df3[sub_ob])**2) / 
                    sum((df3[sub_ob] - (df3[sub_ob]).mean())**2))

                ## PBIAS
                PBIAS = 100*(sum(df3[sub_ob] - df3.streamflow_sim) / sum(df3[sub_ob]))

            # ------------ Export Data to file -------------- #
            with open(os.path.join(outfolder, "swatmf_reach(" + str(outletSubNum) + ")"+"_ob("+ str(sub_ob)+")_annual.txt"), 'w') as f:
                f.write("# swatmf_reach(" + str(outletSubNum) + ")"+"_ob("+ str(sub_ob)
                        +")_annual.txt is created by QSWATMOD2 plugin "+ version + time + "\n")
                df3.to_csv(f, index_label = "Date", sep = '\t', float_format='%10.4f', line_terminator='\n', encoding='utf-8')
                f.write('\n')
                f.write("# Statistics\n")
                f.write("Nash–Sutcliffe: " + str('{:.4f}'.format(dNS) + "\n"))
                f.write("R-squared: " + str('{:.4f}'.format(r_squared) + "\n"))
                f.write("PBIAS: " + str('{:.4f}'.format(PBIAS) + "\n"))

            msgBox = QMessageBox()
            msgBox.setWindowIcon(QtGui.QIcon(':/QSWATMOD2/pics/sm_icon.png'))
            msgBox.setWindowTitle("Exported!")
            msgBox.setText("'swatmf_reach(" + str(outletSubNum) + ")"+"_ob("+ str(sub_ob)
                        +")_annual.txt' file is exported to your 'exported_files' folder!")
            msgBox.exec_()

        except:         
            msgBox = QMessageBox()
            msgBox.setWindowIcon(QtGui.QIcon(':/QSWATMOD2/pics/sm_icon.png'))
            msgBox.setWindowTitle("Not Ready!")
            msgBox.setText("Running the simulation for a warm-up period!")
            msgBox.exec_()
    else:
        output_rch = pd.read_csv(os.path.join(wd, "output.rch"),
                   delim_whitespace=True,
                   skiprows = 9,
                   usecols = [1,colNum],
                   names = ["date", "streamflow_sim"],
                   index_col = 0)
        try:
            df = output_rch.loc[outletSubNum]
            df.index = pd.date_range(startDate, periods=len(df.streamflow_sim), freq = "M")
            dfa = df.resample('A').mean()

            # ------------ Export Data to file -------------- #
            with open(os.path.join(outfolder, "swatmf_reach(" + str(outletSubNum) + ")_annual"+".txt"), 'w') as f:
                f.write("# swatmf_reach(" + str(outletSubNum) + ")_annual"+".txt is created by QSWATMOD2 plugin "+ version + time + "\n")
                dfa.to_csv(f, index_label = "Date", sep = '\t', float_format='%10.4f', line_terminator='\n', encoding='utf-8')
                f.write('\n')
                f.write("# Statistics\n")
                # f.write("Nash–Sutcliffe: " + str('{:.4f}'.format(dNS) + "\n"))
                f.write("Nash–Sutcliffe: ---\n")
                f.write("R-squared: ---\n")
                f.write("PBIAS: ---\n")

            msgBox = QMessageBox()
            msgBox.setWindowIcon(QtGui.QIcon(':/QSWATMOD2/pics/sm_icon.png'))
            msgBox.setWindowTitle("Exported!")
            msgBox.setText("'swatmf_reach(" + str(outletSubNum)+")_annual.txt' file is exported to your 'exported_files' folder!")
            msgBox.exec_()

        except:
            msgBox = QMessageBox()
            msgBox.setWindowIcon(QtGui.QIcon(':/QSWATMOD2/pics/sm_icon.png'))
            msgBox.setWindowTitle("Not Ready!")
            msgBox.setText("Nothing to write down right now!")
            msgBox.exec_()


def export_sd_annual(self):
    from qgis.PyQt import QtCore, QtGui, QtSql
    QSWATMOD_path_dict = self.dirs_and_paths()
    stdate, eddate, stdate_warmup, eddate_warmup = self.define_sim_period() 
    wd = QSWATMOD_path_dict['SMfolder']
    outfolder = QSWATMOD_path_dict['exported_files']
    startDate = stdate_warmup.strftime("%m/%d/%Y")
    endDate = eddate_warmup.strftime("%m/%d/%Y")
    colNum = 6 # get flow_out
    outletSubNum = int(self.dlg.comboBox_sub_number.currentText())
    stf_obd_nam = self.dlg.comboBox_stf_obd.currentText()
    # Add info
    from datetime import datetime
    version = "version 2.7."
    time = datetime.now().strftime('- %m/%d/%y %H:%M:%S -')

    if self.dlg.checkBox_stream_obd.isChecked():
        strObd = pd.read_csv(
                            os.path.join(wd, stf_obd_nam),
                            index_col = 0,
                            header = 0,
                            parse_dates=True,
                            na_values=[-999, ""])

        output_rch = pd.read_csv(os.path.join(wd, "output.rch"),
                           delim_whitespace=True,
                           skiprows = 9,
                           usecols = [1,colNum],
                           names = ["date", "streamflow_sim"],
                           index_col = 0)
        
        sub_ob = self.dlg.comboBox_SD_obs_data.currentText()

        try:
        # if (output_rch.index[0] == 1):
            df = output_rch.loc[outletSubNum]
            df.index = pd.date_range(startDate, periods=len(df.streamflow_sim))
            dfa = df.resample('A').mean()
            strObda = strObd.resample('A').mean()
            df2 = pd.concat([dfa, strObda[sub_ob]], axis = 1)
            df3 = df2.dropna()

            if (len(df3[sub_ob]) > 1):
                ## R-squared
                r_squared = (
                    (
                        (sum((df3[sub_ob] - df3[sub_ob].mean())*(df3.streamflow_sim-df3.streamflow_sim.mean())))**2
                    ) 
                    /
                    (
                        (sum((df3[sub_ob] - df3[sub_ob].mean())**2)* (sum((df3.streamflow_sim-df3.streamflow_sim.mean())**2))
                    ))
                )

                ##Nash–Sutcliffe (E) model efficiency coefficient ---used up in the class
                dNS = 1 - (sum((df3.streamflow_sim - df3[sub_ob])**2) / 
                    sum((df3[sub_ob] - (df3[sub_ob]).mean())**2))

                ## PBIAS
                PBIAS =  100*(sum(df3[sub_ob] - df3.streamflow_sim) / sum(df3[sub_ob]))

            # ------------ Export Data to file -------------- #
            with open(os.path.join(outfolder, "swatmf_reach(" + str(outletSubNum) + ")"+"_ob("+ str(sub_ob)+")_annual.txt"), 'w') as f:
                f.write("# swatmf_reach(" + str(outletSubNum) + ")"+"_ob("+ str(sub_ob)
                        +")_annual.txt is created by QSWATMOD2 plugin "+ version + time + "\n")
                df3.to_csv(f, index_label = "Date", sep = '\t', float_format='%10.4f', line_terminator='\n', encoding='utf-8')
                f.write('\n')
                f.write("# Statistics\n")
                f.write("Nash–Sutcliffe: " + str('{:.4f}'.format(dNS) + "\n"))
                f.write("R-squared: " + str('{:.4f}'.format(r_squared) + "\n"))
                f.write("PBIAS: " + str('{:.4f}'.format(PBIAS) + "\n"))

            msgBox = QMessageBox()
            msgBox.setWindowIcon(QtGui.QIcon(':/QSWATMOD2/pics/sm_icon.png'))
            msgBox.setWindowTitle("Exported!")
            msgBox.setText("'swatmf_reach(" + str(outletSubNum) + ")"+"_ob("+ str(sub_ob)
                        +")_annual.txt' file is exported to your 'exported_files' folder!")
            msgBox.exec_()

        except:         
            msgBox = QMessageBox()
            msgBox.setWindowIcon(QtGui.QIcon(':/QSWATMOD2/pics/sm_icon.png'))
            msgBox.setWindowTitle("Not Ready!")
            msgBox.setText("Running the simulation for a warm-up period!")
            msgBox.exec_()
    else:
        output_rch = pd.read_csv(os.path.join(wd, "output.rch"),
                   delim_whitespace=True,
                   skiprows = 9,
                   usecols = [1,colNum],
                   names = ["date", "streamflow_sim"],
                   index_col = 0)
        try:
            df = output_rch.loc[outletSubNum]
            df.index = pd.date_range(startDate, periods=len(df.streamflow_sim))
            dfa = df.resample('A').mean()

            # ------------ Export Data to file -------------- #
            with open(os.path.join(outfolder, "swatmf_reach(" + str(outletSubNum) + ")_annual"+".txt"), 'w') as f:
                f.write("# swatmf_reach(" + str(outletSubNum) + ")_annual"+".txt is created by QSWATMOD2 plugin "+ version + time + "\n")
                dfa.to_csv(f, index_label = "Date", sep = '\t', float_format='%10.4f', line_terminator='\n', encoding='utf-8')
                f.write('\n')
                f.write("# Statistics\n")
                # f.write("Nash–Sutcliffe: " + str('{:.4f}'.format(dNS) + "\n"))
                f.write("Nash–Sutcliffe: ---\n")
                f.write("R-squared: ---\n")
                f.write("PBIAS: ---\n")

            msgBox = QMessageBox()
            msgBox.setWindowIcon(QtGui.QIcon(':/QSWATMOD2/pics/sm_icon.png'))
            msgBox.setWindowTitle("Exported!")
            msgBox.setText("'swatmf_reach(" + str(outletSubNum)+")_annual.txt' file is exported to your 'exported_files' folder!")
            msgBox.exec_()

        except:
            msgBox = QMessageBox()
            msgBox.setWindowIcon(QtGui.QIcon(':/QSWATMOD2/pics/sm_icon.png'))
            msgBox.setWindowTitle("Not Ready!")
            msgBox.setText("Nothing to write down right now!")
            msgBox.exec_()


def load_str_obd(self):
    QSWATMOD_path_dict = self.dirs_and_paths()
    settings = QSettings()
    if settings.contains('/QSWATMOD2/LastInputPath'):
        path = str(settings.value('/QSWATMOD2/LastInputPath'))
    else:
        path = ''
    title = "Provide 'streamflow.obd' file!"
    inFileName, __ = QFileDialog.getOpenFileNames(
        None, title, path,
        "Observation data (*.obd *.OBD);; All files (*.*)"
        )
    if inFileName:
        settings.setValue('/QSWATMOD2/LastInputPath', os.path.dirname(str(inFileName)))           
        output_dir = QSWATMOD_path_dict['SMfolder']
        inInfo = QFileInfo(inFileName[0])
        inFile = inInfo.fileName()
        pattern = os.path.splitext(inFileName[0])[0] + '.*'

        # inName = os.path.splitext(inFile)[0]
        inName = 'streamflow'
        for f in glob.iglob(pattern):
            suffix = os.path.splitext(f)[1]
            if os.name == 'nt':
                outfile = ntpath.join(output_dir, inName + '.obd')
            else:
                outfile = posixpath.join(output_dir, inName + '.obd')             
            shutil.copy(f, outfile)


def load_mf_obd(self):
    QSWATMOD_path_dict = self.dirs_and_paths()
    settings = QSettings()
    if settings.contains('/QSWATMOD2/LastInputPath'):
        path = str(settings.value('/QSWATMOD2/LastInputPath'))
    else:
        path = ''
    title = "Provide 'modflow.obd' file!"
    inFileName, __ = QFileDialog.getOpenFileNames(
        None, title, path,
        "Observation data (*.obd *.OBD);; All files (*.*)"
        )
    if inFileName:
        settings.setValue('/QSWATMOD2/LastInputPath', os.path.dirname(str(inFileName)))           
        output_dir = QSWATMOD_path_dict['SMfolder']
        inInfo = QFileInfo(inFileName[0])
        inFile = inInfo.fileName()
        pattern = os.path.splitext(inFileName[0])[0] + '.*'

        # inName = os.path.splitext(inFile)[0]
        inName = 'modflow'
        for f in glob.iglob(pattern):
            suffix = os.path.splitext(f)[1]
            if os.name == 'nt':
                outfile = ntpath.join(output_dir, inName + '.obd')
            else:
                outfile = posixpath.join(output_dir, inName + '.obd')             
            shutil.copy(f, outfile)


# NOTE: will create several methods for specific functionalities, making the code more modular and easier to understand.
def sd_plot_daily2(self):
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

    # plot
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.set_ylabel(r'Stream Discharge $[m^3/s]$', fontsize=8)
    ax.tick_params(axis='both', labelsize=8)

    if self.dlg.checkBox_stream_obd.isChecked():
        plot_stream_obd(self, ax, wd, stf_obd_nam, startDate, outletSubNum, colNum)
    else:
        self.plot_simulated(ax, wd, outletSubNum, colNum, startDate)

    plt.legend(fontsize=8, loc="lower right", ncol=2, bbox_to_anchor=(1, 1))
    plt.show()

def plot_stream_obd(self, ax, wd, stf_obd_nam, startDate, outletSubNum, colNum):
    strObd = pd.read_csv(
        os.path.join(wd, stf_obd_nam),
        index_col=0,
        header=0,
        parse_dates=True,
        na_values=[-999, ""]
    )

    output_rch = pd.read_csv(
        os.path.join(wd, "output.rch"),
        delim_whitespace=True,
        skiprows=9,
        usecols=[1, 3, colNum],
        names=["date", "filter", "streamflow_sim"],
        index_col=0
    )

    sub_ob = self.dlg.comboBox_SD_obs_data.currentText()

    try:
        df = output_rch.loc[outletSubNum]
        df.index = date_range_frequency(self, df, startDate)

        ax.plot(df.index.values, df.streamflow_sim.values, c='limegreen', lw=1, label="Simulated")

        df2 = pd.concat([df, strObd[sub_ob]], axis=1)
        df3 = df2.dropna()

        plot_observed_data(self, ax, df3, sub_ob)

    except Exception as e:
        handle_exception(self, ax, str(e))

def plot_simulated(self, ax, wd, outletSubNum, colNum, startDate):
    output_rch = pd.read_csv(
        os.path.join(wd, "output.rch"),
        delim_whitespace=True,
        skiprows=9,
        usecols=[1, 3, colNum],
        names=["date", "filter", "streamflow_sim"],
        index_col=0
    )

    try:
        df = output_rch.loc[outletSubNum]
        df.index = self.date_range_frequency(df, startDate)

        ax.plot(df.index.values, df.streamflow_sim.values, c='g', lw=1, label="Simulated")
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d\n%Y'))

    except Exception as e:
        self.handle_exception(ax, str(e))

def date_range_frequency(self, df, startDate):
    if self.dlg.radioButton_day.isChecked():
        return pd.date_range(startDate, periods=len(df.streamflow_sim))
    elif self.dlg.radioButton_month.isChecked():
        df = df[df['filter'] < 13]
        return pd.date_range(startDate, periods=len(df.streamflow_sim), freq="M")
    else:
        return pd.date_range(startDate, periods=len(df.streamflow_sim), freq="A")

def plot_observed_data(self, ax, df3, sub_ob):
    if self.dlg.radioButton_str_obd_pt.isChecked():
        size = float(self.dlg.spinBox_str_obd_size.value())
        ax.scatter(
            df3.index, df3[sub_ob], c='m', lw=1, alpha=0.5, s=size, marker='x',
            label="Observed", zorder=3
        )
    else:
        ax.plot(
            df3.index, df3[sub_ob], c='m', lw=1.5, alpha=0.5,
            label="Observed", zorder=3
        )

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d\n%Y'))

    if len(df3[sub_ob]) > 1:
        self.calculate_metrics(ax, df3, sub_ob)
    else:
        self.display_no_data_message(ax)

def calculate_metrics(self, ax, df3, sub_ob):
    r_squared = ((sum((df3[sub_ob] - df3[sub_ob].mean()) * (df3.streamflow_sim - df3.streamflow_sim.mean())))**2) / (
            (sum((df3[sub_ob] - df3[sub_ob].mean())**2) * (sum((df3.streamflow_sim - df3.streamflow_sim.mean())**2)))
    )

    dNS = 1 - (sum((df3.streamflow_sim - df3[sub_ob])**2) / sum((df3[sub_ob] - (df3[sub_ob]).mean())**2))

    PBIAS = 100 * (sum(df3[sub_ob] - df3.streamflow_sim) / sum(df3[sub_ob]))

    self.display_metrics(ax, dNS, r_squared, PBIAS)

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



