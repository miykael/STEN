import wx
import Stat
import tables
import PostStat
import os
import numpy as np


class Start:

    """
    TODO: Description TEXT
    """

    def __init__(self, Mainframe):

        # Get relevant variables from Data and Analysis Panel
        self.PathResult = Mainframe.PanelData.TextResult.Value
        self.notebookSelected = Mainframe.PanelOption.GetSelection()
        self.H5 = Mainframe.H5
        self.Mainframe = Mainframe
        self.cancel = False

        # ANOVA on Wave/GFP
        if self.notebookSelected == 0:
            self.AnovaCheck = self.Mainframe.AnovaWave.AnovaCheck
            self.AnovaIteration = self.Mainframe.AnovaWave.nIteration
            self.AnovaParam = self.Mainframe.AnovaWave.Param
            self.PostHocCheck = self.Mainframe.AnovaWave.PostHocCheck
            self.PostHocnIteration = self.Mainframe.AnovaWave.nIterationPostHoc
            self.PostHocParam = self.Mainframe.AnovaWave.ParamPostHoc
            self.SpaceFile = self.Mainframe.AnovaWave.SPIFile
            self.SPIPath = self.Mainframe.AnovaWave.SPIPath
            self.AnalyseType = self.Mainframe.AnovaWave.AnalyseType


            self.AnovaAlpha = self.Mainframe.AnovaWave.Alpha
            self.AnovaClust = self.Mainframe.AnovaWave.Clust
            self.AnovaPtsConsec = self.Mainframe.AnovaWave.PtsConseq
            self.PostHocAlpha = self.Mainframe.AnovaWave.AlphaPostHoc
            self.PostHocClust = self.Mainframe.AnovaWave.ClustPostHoc
            self.PostHocPtsConseq = self.Mainframe.AnovaWave.PtsConseqPostHoc
            
            self.Alpha={'Anova':self.AnovaAlpha,'PostHoc':self.PostHocAlpha}
            self.PtsConsec={'Anova':self.AnovaPtsConsec,'PostHoc':self.PostHocPtsConseq}
            self.Clust={'Anova':self.AnovaClust,'PostHoc':self.PostHocClust}
            
        # ANOVA in Brain Space
        elif self.notebookSelected == 1:
            self.AnovaCheck = self.Mainframe.AnovaIS.AnovaCheck
            self.AnovaIteration = self.Mainframe.AnovaIS.nIteration
            self.AnovaParam = self.Mainframe.AnovaIS.Param
            self.PostHocCheck = self.Mainframe.AnovaIS.PostHocCheck
            self.PostHocnIteration = self.Mainframe.AnovaIS.nIterationPostHoc
            self.PostHocParam = self.Mainframe.AnovaIS.ParamPostHoc
            self.SpaceFile = self.Mainframe.AnovaIS.SPIFile
            self.SPIPath = self.Mainframe.AnovaIS.SPIPath
            self.AnalyseType = None

            self.AnovaAlpha = self.Mainframe.AnovaIS.Alpha
            self.AnovaClust = self.Mainframe.AnovaIS.Clust
            self.AnovaPtsConsec = self.Mainframe.AnovaIS.PtsConseq
            self.PostHocAlpha = self.Mainframe.AnovaIS.AlphaPostHoc
            self.PostHocClust = self.Mainframe.AnovaIS.ClustPostHoc
            self.PostHocPtsConseq = self.Mainframe.AnovaIS.PtsConseqPostHoc
            
            self.Alpha={'Anova':self.AnovaAlpha,'PostHoc':self.PostHocAlpha}
            self.PtsConsec={'Anova':self.AnovaPtsConsec,'PostHoc':self.PostHocPtsConseq}
            self.Clust={'Anova':self.AnovaClust,'PostHoc':self.PostHocClust}

        # Create result folder
        if not os.path.exists(self.PathResult):
            os.makedirs(self.PathResult)

        # Check which calculations were already computed
        self.checkForRerun()

        # Calculate ANOVA on Wave/GFP
        if self.notebookSelected == 0:
            self.calcAnovaWave()

        # Calculate ANOVA in Brain Space
        elif self.notebookSelected == 1:
            self.calcAnovaIS()

        # Write progressTxt to H5 file
        with tables.openFile(self.H5, mode='r+') as h5file:

            # Delete previous content
            description = h5file.getNode('/Progress').description
            h5file.removeNode('/Progress', recursive=True)
            h5file.createTable('/', 'Progress', description)

            # Write new content
            progRow = h5file.getNode('/Progress').row
            for i, e in enumerate(self.progressTxt):
                progRow['Text'] = e
                progRow.append()

        # Write Verbose File
        self.writeVrb(self.Mainframe.Dataset)

    def calcAnovaWave(self):
        # calculates Anova on wave and/or GFP
        if self.AnovaCheck:

            self.Wave = Stat.Anova(self.H5, self.Mainframe)
            # Parametric Analysis
            if self.AnovaParam:
                if self.AnalyseType in ["GFP Only", "Both"] \
                        and self.doAnovaParamGFP:
                    self.Wave.Param(DataGFP=True)
                    self.progressTxt.append(
                        'Parametric Anova (GFP) : %s' % self.Wave.elapsedTime)
                 

                if self.AnalyseType in ["All Electrodes", "Both"] \
                        and self.doAnovaParamElect:
                    self.Wave.Param()
                    self.progressTxt.append(
                        'Parametric Anova (All Electrodes) : %s'
                        % self.Wave.elapsedTime)
       
            # Non Parametric Analysis
            else:
                if self.AnalyseType in ["GFP Only", "Both"] \
                        and self.doAnovaNonParamGFP:
                    self.Wave.NonParam(self.AnovaIteration, DataGFP=True)
                    self.progressTxt.append(
                        'Non-Parametric Anova (GFP) : %s'
                        % self.Wave.elapsedTime)
                    
                if self.AnalyseType in ["All Electrodes", "Both"] \
                        and self.doAnovaNonParamElect:
                    self.Wave.NonParam(self.AnovaIteration)
                    self.progressTxt.append(
                        'Non-Parametric Anova (All Electrodes) : %s'
                        % self.Wave.elapsedTime)

            # Makes sure that the h5 files are always closed at the end
            self.cancel = self.Wave.cancel
            self.Wave.file.close()

        
        # calculates PostHoc on wave and/or GFP
        if self.PostHocCheck:

            self.WavePostHoc = Stat.PostHoc(self.H5, self.Mainframe)

            # Parametric
            if self.PostHocParam:
                if self.AnalyseType in ["GFP Only", "Both"] \
                        and self.doPostHocParamGFP:
                    self.WavePostHoc.Param(DataGFP=True)
                    self.progressTxt.append(
                        'Parametric PostHoc (GFP) : %s'
                        % self.WavePostHoc.elapsedTime)

                if self.AnalyseType in ["All Electrodes", "Both"] \
                        and self.doPostHocParamElect:
                    self.WavePostHoc.Param()
                    self.progressTxt.append(
                        'Parametric PostHoc (All Electrodes) : %s'
                        % self.WavePostHoc.elapsedTime)

            # Non Parametric
            else:
                if self.AnalyseType in ["GFP Only", "Both"] \
                        and self.doPostHocNonParamGFP:
                    self.WavePostHoc.NonParam(self.PostHocIteration,
                                              DataGFP=True)
                    self.progressTxt.append(
                        'Non-Parametric PostHoc (GFP) : %s'
                        % self.WavePostHoc.elapsedTime)
                    
                if self.AnalyseType in ["All Electrodes", "Both"] \
                        and self.doPostHocNonParamElect:
                    self.WavePostHoc.NonParam(self.PostHocIteration)
                    self.progressTxt.append(
                        'Non-Parametric PostHoc (All Electrodes) : %s'
                        % self.WavePostHoc.elapsedTime)
            # Makes sure that the h5 files are always closed at the end
            self.cancel = self.WavePostHoc.cancel
            self.WavePostHoc.file.close()
            
        # Multiple testing and writing Data
        if self.SpaceFile=='':
            self.SpaceFile=None
        Correction=PostStat.MultipleTestingCorrection(self.H5,self.Mainframe,
                                                          TF=self.PtsConsec,Alpha=self.Alpha,
                                                          SpaceCont=self.Clust,
                                                          SpaceFile=self.SpaceFile)
        Correction.Calculation()
        self.Param={'Anova':self.AnovaParam,'PostHoc':self.PostHocParam}
        if self.AnalyseType in ["GFP Only", "Both"]:
            Writing=PostStat.WriteData(self.PathResult,self.H5,self.Param,DataGFP=True)
            Writing.StatistcalData(Correction.CorrectedMask)
            Writing.IntermediateResult()
            Writing.file.close()
        if self.AnalyseType in ["All Electrodes", "Both"]:
            Writing=PostStat.WriteData(self.PathResult,self.H5,self.Param,DataGFP=False)
            Writing.StatistcalData(Correction.CorrectedMask)
            Writing.IntermediateResult()
            Writing.file.close()
    def calcAnovaIS(self):
        """TODO: implement the checks for rerun"""

        # calculates Anova on inverse space (IS)
        if self.AnovaCheck:

            self.IS = Stat.Anova(self.H5, self.Mainframe)

            # Parametric Analysis
            if self.AnovaParam:
                self.IS.Param()
                self.progressTxt.append(
                    'Parametric Anova (IS) : %s' % self.IS.elapsedTime)

            # Non Parametric Analysis
            else:
                self.IS.NonParam(self.AnovaIteration)
                self.progressTxt.append(
                    'Non-Parametric Anova (IS) : %s' % self.IS.elapsedTime)

            # Makes sure that the h5 files are always closed at the end
            self.IS.file.close()
            self.cancel = self.IS.cancel


            
        # calculates PostHoc on inverse space (IS)
        if self.PostHocCheck:

            self.ISPostHoc = Stat.PostHoc(self.H5, self.Mainframe)

            # Parametric Analysis
            if self.PostHocParam:
                self.ISPostHoc.Param()
                self.progressTxt.append(
                    'Parametric PostHoc (IS) : %s'
                    % self.ISPostHoc.elapsedTime)

            # Non Parametric Analysis
            else:
                self.ISPostHoc.NonParam(self.PostHocIteration)
                self.progressTxt.append(
                    'Non-Parametric PostHoc (IS) : %s'
                    % self.ISPostHoc.elapsedTime)

            # Makes sure that the h5 files are always closed at the end
            self.ISPostHoc.file.close()
            self.cancel = self.ISPostHoc.cancel
        # Multiple testing and writing Data, Post Stat Analysis - i.e Mathematical Morphology, write
        if self.SpaceFile=='':
            self.SpaceFile=None
        Correction=PostStat.MultipleTestingCorrection(self.H5,self.Mainframe,
                                                          TF=self.PtsConsec,Alpha=self.Alpha,
                                                          SpaceCont=self.Clust,
                                                          SpaceFile=self.SpaceFile)
        Correction.Calculation()
        self.Param={'Anova':self.AnovaParam,'PostHoc':self.PostHocParam}
        Writing=PostStat.WriteData(self.PathResult,self.H5,self.Param,DataGFP=False)
        Writing.StatistcalData(Correction.CorrectedMask)
        Writing.IntermediateResult()
        Writing.file.close()

    def checkIfCancel(self):
        """TODO: Check this function - isn't called yet"""

        # If cancel press
        if self.cancel:
            file = tables.openFile(self.H5, 'r+')
            GFPDataTest = file.listNodes('/Result/GFP/Anova')
            AllDataTest = file.listNodes('/Result/All/Anova')
            if GFPDataTest != []:
                file.removeNode('/Result/GFP/Anova', recursive=True)
                file.createGroup('/Result/Anova', 'GFP')
            if AllDataTest != []:
                file.removeNode('/Result/All/Anova', recursive=True)
                file.createGroup('/Result/Anova', 'All')
            file.close()
            self.Mainframe.PanelData.TxtProgress.SetLabel(
                "Calculation Cancel by user")
        else:
            self.Mainframe.PanelData.TxtProgress.SetLabel(
                "\n".join(self.progressTxt))
            # self.writeVrb(self.H5, PathResult)
            dlg = wx.MessageDialog(
                self.Mainframe, style=wx.OK | wx.CANCEL,
                message='Work is done enjoy your results !!!! ;-)')
            dlg.ShowModal()
            dlg.Destroy()

    def checkForRerun(self):
        """
        TODO: Description TEXT
        """

        h5file = tables.openFile(self.H5, mode='a')

        self.progressTxt = [e[0] for e in h5file.getNode('/Progress').read()]

        if self.progressTxt == []:
            self.progressTxt = ['Calculation Time :']

        # Make sure to only run the ones that were selected
        if self.AnalyseType in ["GFP Only", "Both"]:
            self.doAnovaParamGFP = True
            self.doAnovaNonParamGFP = True
            self.doPostHocParamGFP = True
            self.doPostHocNonParamGFP = True

            # Check if Process was already done and ask for rerun
            calcMode = 'Parametric Anova (GFP)'
            if np.any([calcMode in p for p in self.progressTxt]):
                self.doAnovaParamGFP = self.rerunMessage(h5file, calcMode)

            calcMode = 'Non-Parametric Anova (GFP)'
            if np.any([calcMode in p for p in self.progressTxt]):
                self.doAnovaNonParamGFP = self.rerunMessage(h5file, calcMode)

            calcMode = 'Parametric PostHoc (GFP)'
            if np.any([calcMode in p for p in self.progressTxt]):
                self.doPostHocParamGFP = self.rerunMessage(h5file, calcMode)

            calcMode = 'Non-Parametric PostHoc (GFP)'
            if np.any([calcMode in p for p in self.progressTxt]):
                self.doPostHocNonParamGFP = self.rerunMessage(h5file, calcMode)

        if self.AnalyseType in ["All Electrodes", "Both"]:
            self.doAnovaParamElect = True
            self.doAnovaNonParamElect = True
            self.doPostHocParamElect = True
            self.doPostHocNonParamElect = True

            calcMode = 'Parametric Anova (All Electrodes)'
            if np.any([calcMode in p for p in self.progressTxt]):
                self.doAnovaParamElect = self.rerunMessage(h5file, calcMode)

            calcMode = 'Non-Parametric Anova (All Electrodes)'
            if np.any([calcMode in p for p in self.progressTxt]):
                self.doAnovaNonParamElect = self.rerunMessage(h5file, calcMode)

            calcMode = 'Parametric PostHoc (All Electrodes)'
            if np.any([calcMode in p for p in self.progressTxt]):
                self.doPostHocParamElect = self.rerunMessage(h5file, calcMode)

            calcMode = 'Non-Parametric PostHoc (All Electrodes)'
            if np.any([calcMode in p for p in self.progressTxt]):
                self.doPostHocNonParamElect = self.rerunMessage(h5file,
                                                                calcMode)

        h5file.close()

    def rerunMessage(self, h5file, calcMode):
        """Checks if a specific calculation mode was already computed
        and asks if it should be run again or not
        """

        progTxt = self.progressTxt[np.where(
            [calcMode in p for p in self.progressTxt])[0]]

        message = ['Results were already computed for:\n%s\n\n' % progTxt,
                   'Do you want to recalculate (YES) or \n',
                   'continue with the already computed results (NO)?']

        dlg = wx.MessageDialog(
            None, style=wx.YES_NO | wx.YES_DEFAULT | wx.ICON_QUESTION,
            caption='%s already computed' % calcMode,
            message=''.join(message))
        answer = dlg.ShowModal()
        dlg.Destroy()

        if answer == wx.ID_YES:

            nodePath = '/Result'
            if 'All' in calcMode:
                nodePath += '/All'
            else:
                nodePath += '/GFP'
            if 'PostHoc' in calcMode:
                node = 'PostHoc'
            else:
                node = 'Anova'

            # Cleares Node that should be rerun
            description = h5file.getNode(nodePath + '/' + node).description
            h5file.removeNode(nodePath + '/' + node, recursive=True)
            h5file.createTable(nodePath, node, description)

            # Delete progress Text from already computed step
            self.progressTxt.pop(
                np.where(np.asarray(self.progressTxt) == progTxt)[0])

            doRerun = True

        else:
            doRerun = False

        return doRerun

    def writeVrb(self, dataset):
        """
        Writes verbose file into result folder
        """

        with tables.openFile(self.H5, 'r') as h5file:
            shape = h5file.getNode('/Shape').read()

        # Get Analysis and Parameter information
        Analysis = 'Analysis :\n----------\n'
        Param = 'Parameter :\n-----------\n'

        # TODO: update verbose for ANCOVA
        if self.AnovaCheck:
            Param += 'ANOVA :\n'
            Param += '\tAlpha = %s\n' % self.AnovaAlpha
            Param += '\tConsecutive Time Frame = %s\n' % self.AnovaPtsConsec

            if self.AnovaParam:
                Analysis += 'Parametric Repeated Measure ANOVA\n'
            else:
                Analysis += 'Non-Parametric Repeated Measure ANOVA\n'

            if self.AnalyseType in ["GFP Only", "Both"]:
                Analysis += '\tGFP            - Time Frames = %s\n' % shape[0]
            if self.AnalyseType in ["All Electrodes", "Both"]:
                Analysis += '\tAll Electrodes - Time Frames = %s\n' % shape[0]
                Analysis += '\tAll Electrodes - Electrodes  = %s\n' % shape[1]

                Param += '\tCluster Size (Electrodes) = %s\n' % self.AnovaClust
                if self.AnovaClust > 1:
                    Param += '\tXYZ File = %s\n' % self.SpaceFile

            if self.AnalyseType is None:
                Analysis += '\tAll Electrodes - Time Frames = %s\n' % shape[0]
                Analysis += '\tAll Electrodes - Voxels      = %s\n' % shape[1]

                Param += '\tCluster Size (Voxels) = %s\n' % self.AnovaClust
                if self.AnovaClust > 1:
                    Param += '\tSPI File = %s\n' % self.SpaceFile

            if not self.AnovaParam:
                Param += '\tNumber of Bootstrap Iterations = %s\n' \
                    % self.AnovaIteration

        if self.AnovaCheck and self.PostHocCheck:
            Analysis += '\n'
            Param += '\n'

        if self.PostHocCheck:
            Param += 'Post hoc :\n'
            Param += '\tAlpha = %s\n' % self.PostHocAlpha
            Param += '\tConsecutive Time Frame = %s\n' % self.PostHocPtsConseq

            if self.PostHocParam:
                Analysis += 'Parametric Post hoc\n'
            else:
                Analysis += 'Non-Parametric Post hoc\n'

            if self.AnalyseType in ["GFP Only", "Both"]:
                Analysis += '\tGFP            - Time Frames = %s\n' % shape[0]
            if self.AnalyseType in ["All Electrodes", "Both"]:
                Analysis += '\tAll Electrodes - Time Frames = %s\n' % shape[0]
                Analysis += '\tAll Electrodes - Electrodes  = %s\n' % shape[1]

                Param += '\tCluster Size (Electrodes) = %s\n' \
                    % self.PostHocClust
                if self.PostHocClust > 1:
                    Param += '\tXYZ File = %s\n' % self.SpaceFile

            if self.AnalyseType is None:
                Analysis += '\tAll Electrodes - Time Frames = %s\n' % shape[0]
                Analysis += '\tAll Electrodes - Voxels      = %s\n' % shape[1]

                Param += '\tCluster Size (Voxels) = %s\n' % self.PostHocClust
                if self.PostHocClust > 1:
                    Param += '\tSPI File = %s\n' % self.SpaceFile

            if not self.PostHocParam:
                Param += '\tNumber of Bootstrap Iterations = %s\n' \
                    % self.PostHocIteration

        # Get Calculation Time information
        CalcProg = '%s\n------------------\n' % self.progressTxt[0]
        CalcProg += '\t%s' % '\n\t'.join(self.progressTxt[1:])

        # Get Model Information
        ModelInfoTxt = 'Model Information :\n-------------------\n'
        ModelTmp = self.Mainframe.PanelData.TxtModelInfo.GetLabel()[19:]
        ModelInfo=[e.split('\t')[-1] for e in ModelTmp.split('\n')]
        ModelInfoTxt += 'Subject         %s\n' % ModelInfo[0]
        ModelInfoTxt += 'Factor          %s\n' % ModelInfo[1]
        ModelInfoTxt += 'Within Factor   %s\n' % ModelInfo[2]
        ModelInfoTxt += 'Between Factor  %s\n' % ModelInfo[3]
        ModelInfoTxt += 'Covariate       %s\n' % ModelInfo[4]
        ModelInfoTxt += 'R-Formula       %s\n' % ModelInfo[5]

        # Get detailed model Information
        ModelDetailTxt = 'Model Details :\n---------------\n'
        length = len(dataset['Subject'][1])
        tmp = '    {:<16}' + '{:>8}' * length + '\n'
        ModelDetailTxt += 'Subject\n'
        ModelDetailTxt += tmp.format(
            dataset['Subject'][0], *dataset['Subject'][1])
        ModelDetailTxt += 'Covariate\n'
        for covariate in dataset['Covariate']:
            ModelDetailTxt += tmp.format(covariate[0], *covariate[1])
        ModelDetailTxt += 'BetweenFactor\n'
        for beteenfactor in dataset['BetweenFactor']:
            ModelDetailTxt += tmp.format(beteenfactor[0], *beteenfactor[1])

        ModelDetailTxt += 'Factors\n'
        factors = dataset['Factors']
        factors = ['%s (%s)' % (factors[0][i], factors[1][i])
                   for i in range(len(factors[0]))]
        for fac in factors:
            ModelDetailTxt += '    %s\n' % fac

        ModelDetailTxt += 'WithinFactor\n'
        for i, e in enumerate(dataset['WithinFactor']):
            ModelDetailTxt += '    %s %s\n' % (e[0], e[1])
            for j, f in enumerate(e[2]):
                ModelDetailTxt += '        %s\n' % (f)

        # Write everything into a verbose file
        with open('%s/info.vrb' % self.PathResult, 'w') as vrbFile:
            vrbFile.write(Analysis)
            vrbFile.write('\n\n')
            vrbFile.write(Param)
            vrbFile.write('\n\n')
            vrbFile.write(CalcProg)
            vrbFile.write('\n\n')
            vrbFile.write(ModelInfoTxt)
            vrbFile.write('\n\n')
            vrbFile.write(ModelDetailTxt)
