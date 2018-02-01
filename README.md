STEN: Statistical Toolbox for Electrical Neuroimaging
=====================================================

<img align="right" height="290" src="STEN_logo.png">STEN is an open source software toolbox based on Python and R that can be used to compute statistics on several measures of electro- and magnetoencephalographic (EEG and MEG) signals.

STEN enables the sample-point and sensor-wise analysis of EEG and MEG data, but also at the level of Global Field Power (GFP) and distributed neural source estimations (e.g. LAURA or LORETA) by means of parametric and non-parametric (bootstrapping) repeated measure ANOVAs, ANCOVAs and regression analyses. Correction thresholds for temporal and spatial auto-correlations in the data can be individually adjusted.

The currently available STEN toolbox is a beta version. All statistical computations and their outcomes have been extensively validated. However, some minor bugs at the visualization level still need to be fixed.

The most commonly used input data for STEN so far are evoked potential files with header (.eph files), i.e. ASCII files (plain metrics files with header) that have been produced with our partner software [CarTool](https://sites.google.com/site/fbmlab/cartool). STEN produces outputs in the .eph format.


Citation
--------

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.xxxxxx.svg)](https://doi.org/10.5281/zenodo.xxxxxx)

If you used the STEN toolbox in your project, please cite as: Knebel, Jean-Francois, Notter, Michael P., & Murray, Micah M. (2018). STEN: Statistical Toolbox for Electrical Neuroimaging. *Zenodo*. [http://doi.org/10.5281/zenodo.xxxxxx](http://doi.org/10.5281/zenodo.xxxxxx).

Additionally, add the following sentence in the Acknowledgments section:

*The STEN toolbox (https://doi.org/10.5281/zenodo.xxxxxx) has been programmed by Jean-François Knebel and Michael Notter, from the Laboratory for Investigative Neurophysiology (the LINE), Lausanne, Switzerland, and is supported by the Center for Biomedical Imaging (CIBM) of Geneva and Lausanne and by National Center of Competence in Research project “SYNAPSY – The Synaptic Bases of Mental Disease”; project no. 51AU40_125759.*


Installation
------------

Description will follow...


License information
-------------------

STEN toolbox is a statistical toolbox for EEG anlysis at scalp, GFP and brain scale using R 2.11 and Enthought based on Cartool software files
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

The full license is in the file ``LICENSE``. The image of the brain in the logo was created with [MRIcroGL])> and the font used is called Ethnocentric Regular, created and licensed by Ray Larabie (http://typodermicfonts.com/).


Acknowledgments
---------------
Gholam Rezaee Mohammad Mehdi (CHUV, Lausanne, Switzerland) and Prof. Stephan Morgenthaler (EPFL, Lausanne, Switzerland) provided substantial advice on statistical issues and the R software. The team of the LINE (www.unil.ch/line) helped and still help by testing STEN and reporting bugs.
