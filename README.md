# <img src="./imgs/icon.png" style="float" width="40" align="center"> &nbsp; QSWATMOD

#### :exclamation: ***Note:*** `QSWATMOD2 is now available and compatible with QGIS3.` 
[Link to QSWATMOD2](https://github.com/spark-brc/QSWATMOD2)

[QSWATMOD](https://swat.tamu.edu/software/swat-modflow/) is a QGIS-based graphical user interface that facilitates linking SWAT and MODFLOW, running SWAT-MODFLOW simulations, and viewing results.  
This repository contains materials for the QSWATMOD tutorial.  
- **[Installer](https://github.com/spark-brc/qswatmod/tree/master/Installer):** QSWATMOD 1.3.exe
    - Fixed bug in installing the FloPy package 
- **[Inputs](https://github.com/spark-brc/qswatmod/tree/master/Inputs):** ExampleDataset.zip
- **[Source Code](https://github.com/spark-brc/qswatmod/tree/master/SourceCode)**
- **[Tutorial Document](https://github.com/spark-brc/qswatmod/blob/master/QSWATMOD%20Tutorial.pdf)** 

-----
# Installation
The QGIS software must be installed on the system prior to the installation of QSWATMOD. We recommend installing the latest “long term release (LTR)” version of QGIS (2.18.21 ~ 2.18.27)

- Install QGIS by running QGIS-OSGeo4W-2.18.27-1-Setup-x86_64.exe. It can be downloaded from http://download.osgeo.org/qgis/win64/QGIS-OSGeo4W-2.18.27-1-Setup-x86_64.exe.
- Download [the QSWATMOD installer](https://github.com/spark-brc/qswatmod/tree/master/Installer) and install it by running QSWATMOD 1.2.exe or a later version. The QSWATMOD is installed into the user's home directory *(~/.qgis2/python/plugins/QSWATMOD)*, which we will refer to as the QSWATMOD plugin directory.

<p align="center">
    <img src="./imgs/fig_01.PNG" width="500" align="center">
</p>

QSWATMOD has dependencies to third-party Python packages including FloPy3, Pandas, OpenCV, and pyshp. These packages will be installed automatically in the designated Python environment after QSWATMOD is activated in QGIS.  
- Open QGIS after the installation of QSWATMOD is finished.
- Click the “Yes” button to install the dependencies.

<p align="center">
    <img src="./imgs/fig_02.PNG" width="500">
</p>

- After all the dependencies are installed, click the “OK” button. It will reopen QGIS automatically.

<p align="center">
    <img src="./imgs/fig_03.PNG" width="500">
</p>

In addition, [documentation and the SWAT-MODFLOW executable](https://swat.tamu.edu/software/swat-modflow/) are available as downloads. QSWATMOD and SWAT-MODFLOW have been tested in several watersheds. However, no warranty is given that either the model or tool is completely error-free. If you encounter problems with the model, tool or have suggestions for improvement, please comment at [the SWAT-MODFLOW Google group](https://groups.google.com/forum/?hl=en#!forum/swat-modflow) or [QSWATMOD github](https://github.com/spark-brc/qswatmod/issues).

A publication documenting QSWATMOD and an example application can be found here:  
[https://doi.org/10.1016/j.envsoft.2018.10.017](https://doi.org/10.1016/j.envsoft.2018.10.017)

