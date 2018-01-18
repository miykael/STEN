=====================================================
STEN: Statistical Toolbox for Electrical Neuroimaging
=====================================================

.. |logo| image:: STEN_logo.png
   :width: 512

.. |introText| replace:: STEN is an open source software toolbox based on Python and R that can be used to compute statistics on several measures of electro- and magnetoencephalographic (EEG and MEG) signals. STEN enables the sample-point and sensor-wise analysis of EEG and MEG data, but also at the level of Global Field Power (GFP) and distributed neural source estimations (e.g. LAURA or LORETTA) by means of parametric and non-parametric (bootstrapping) repeated measure ANOVAs, ANCOVAs and regression analyses. Correction thresholds for temporal and spatial auto-correlations in the data can be individually adjusted.

+-------------+--------+
| |introText| | |logo| |
+-------------+--------+

The currently available STEN toolbox is a beta version. All statistical computations and their outcomes have been extensively validated. However, some minor bugs at the visualization level still need to be fixed.

The most commonly used input data for STEN so far are evoked potential files with header (.eph files), i.e. ASCII files (plain metrics files with header) that have been produced with our partner software CarTool (https://sites.google.com/site/fbmlab/cartool). STEN produces outputs in the .eph format.


Citation
--------

If you used to process or manipulate your data with STEN, please add the following sentence in the Acknowledgments section:

    The STEN toolbox (https://github.com/jknebel/STEN) has been programmed by Jean-François Knebel and Michael Notter, from the Laboratory for Investigative Neurophysiology (the LINE), Lausanne, Switzerland, and is supported by the Center for Biomedical Imaging (CIBM) of Geneva and Lausanne and by National Center of Competence in Research project “SYNAPSY – The Synaptic Bases of Mental Disease”; project no. 51AU40_125759.

In addition, reference to STEN within the Material and Methods section should be done in the following way:
The analysis was performed using the STEN toolbox developed by Jean-François Knebel and Michael Notter (https://github.com/jknebel/STEN).


Installation
------------

Description will follow...


License information
-------------------

STEN toolbox is a statistical toolbox for EEG anlysis at scalp, GFP and brain scale using R 2.11 and Enthought based on Cartool software files
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

The full license is in the file ``LICENSE``. The image of the brain in the logo was created with `MRIcroGL <http://www.mccauslandcenter.sc.edu/mricrogl/>`_ and the font used is called Ethnocentric Regular, created and licensed by Ray Larabie (http://typodermicfonts.com/).


Acknowledgments
---------------
Gholam Rezaee Mohammad Mehdi (CHUV, Lausanne, Switzerland) and Prof. Stephan Morgenthaler (EPFL, Lausanne, Switzerland) provided substantial advice on statistical issues and the R software. The team of the LINE (www.unil.ch/line) helped and still help by testing STEN and reporting bugs.
