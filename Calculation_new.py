import wx
import Stat
import tables
import PostStat
import os
import time
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
        self.Cancel = False

        # ANOVA on Wave/GFP
        if self.notebookSelected == 0:
            self.AnovaCheck = self.Mainframe.AnovaWave.AnovaCheck
            self.AnovaAlpha = self.Mainframe.AnovaWave.Alpha
            self.AnovaClust = self.Mainframe.AnovaWave.Clust
            self.AnovaIteration = self.Mainframe.AnovaWave.nIteration
            self.AnovaParam = self.Mainframe.AnovaWave.Param
            self.AnovaPtsConsec = self.Mainframe.AnovaWave.PtsConseq
            self.PostHocCheck = self.Mainframe.AnovaWave.PostHocCheck
            self.PostHocAlpha = self.Mainframe.AnovaWave.AlphaPostHoc
            self.PostHocClust = self.Mainframe.AnovaWave.ClustPostHoc
            self.PostHocnIteration = self.Mainframe.AnovaWave.nIterationPostHoc
            self.PostHocParam = self.Mainframe.AnovaWave.ParamPostHoc
            self.PostHocPtsConseq = self.Mainframe.AnovaWave.PtsConseqPostHoc
            self.SpaceFile = self.Mainframe.AnovaWave.SPIFile
            self.SPIPath = self.Mainframe.AnovaWave.SPIPath
            self.AnalyseType = self.Mainframe.AnovaWave.AnalyseType

        # ANOVA in Brain Space
        elif self.notebookSelected == 1:
            self.AnovaCheck = self.Mainframe.AnovaIS.AnovaCheck
            self.AnovaAlpha = self.Mainframe.AnovaIS.Alpha
            self.AnovaClust = self.Mainframe.AnovaIS.Clust
            self.AnovaIteration = self.Mainframe.AnovaIS.nIteration
            self.AnovaParam = self.Mainframe.AnovaIS.Param
            self.AnovaPtsConsec = self.Mainframe.AnovaIS.PtsConseq
            self.PostHocCheck = self.Mainframe.AnovaIS.PostHocCheck
            self.PostHocAlpha = self.Mainframe.AnovaIS.AlphaPostHoc
            self.PostHocClust = self.Mainframe.AnovaIS.ClustPostHoc
            self.PostHocnIteration = self.Mainframe.AnovaIS.nIterationPostHoc
            self.PostHocParam = self.Mainframe.AnovaIS.ParamPostHoc
            self.PostHocPtsConseq = self.Mainframe.AnovaIS.PtsConseqPostHoc
            self.SpaceFile = self.Mainframe.AnovaIS.SPIFile
            self.SPIPath = self.Mainframe.AnovaIS.SPIPath
            self.AnalyseType = None

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

        # TODO: Delete following line
        print 'DONE'

    def calcAnovaWave(self):

        # calcul Anova on wave and/or GFP
        if self.AnovaCheck:

            self.Wave = Stat.Anova(self.H5, self.Mainframe)

            # Parametric
            if self.AnovaParam:

                if self.AnalyseType in ["GFP Only", "Both"] and self.doAnovaParamGFP:
                    self.Wave.Param(DataGFP=True)
                    self.progressTxt.append('Parametric Anova (GFP) : %s' % self.Wave.elapsedTime)

                if self.AnalyseType in ["All Electrodes", "Both"] and self.doAnovaParamElect:
                    self.Wave.Param()
                    self.progressTxt.append('Parametric Anova (All Electrodes) : %s' % self.Wave.elapsedTime)

            # Non Parametric
            else:
                if self.AnalyseType in ["GFP Only", "Both"] and self.doAnovaNonParamGFP:
                    self.Wave.NonParam(self.AnovaIteration, DataGFP=True)
                    self.progressTxt.append('Non-Parametric Anova (GFP) : %s' % self.Wave.elapsedTime)

                if self.AnalyseType in ["All Electrodes", "Both"] and self.doAnovaNonParamElect:
                    self.Wave.NonParam(self.AnovaIteration)
                    self.progressTxt.append('Non-Parametric Anova (All Electrodes) : %s' % self.Wave.elapsedTime)

            # TODO: Make sure that the h5 files are always closed at the end
            self.Wave.file.close()
            self.Cancel = self.Wave.Cancel

            # Post Stat (PostHoc) i.e Mathematical Morphology,
            # write Data
            # TODO: skip Post Stat (PostHoc) as long as PostStat.py is not updated
            #if not self.Cancel:
            if False:
                ResultName = 'Anova'
                PathResultAnova = os.path.abspath("/".join([self.PathResult, ResultName]))

                if not os.path.exists(PathResultAnova):
                    os.makedirs(PathResultAnova)

                if self.AnalyseType in ["GFP Only", "Both"]:
                    start = time.clock()
                    self.WavePostStat = PostStat.Data(self.H5, self, Anova=True, DataGFP=True, Param=self.AnovaParam)
                    self.WavePostStat.MathematicalMorphology(self.AnovaAlpha, TF=self.AnovaPtsConsec, SpaceCriteria=1, SpaceFile=None)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append('Multiple Test Correction (GFP): %s' % self.TimeTxt)

                    start = time.clock()
                    self.WavePostStat.WriteData(PathResultAnova)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append('Writing EPH Results : %s' % self.TimeTxt)

                    start = time.clock()
                    self.WavePostStat.WriteIntermediateResult(self.PathResult, DataGFP=True)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append('Writing intermediater EPH Results : %s' % self.TimeTxt)
                    self.WavePostStat.file.close()
                if self.AnalyseType in ["All Electrodes", "Both"]:
                    start = time.clock()
                    self.WavePostStat = PostStat.Data(self.H5, self, Anova=True, DataGFP=False, Param=self.AnovaParam)
                    self.WavePostStat.MathematicalMorphology(self.AnovaAlpha, TF=self.AnovaPtsConsec, SpaceCriteria=self.AnovaClust, SpaceFile=self.SpaceFile)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append('Multiple Test Correction (All electrodes): %s' % self.TimeTxt)

                    start = time.clock()
                    self.WavePostStat.WriteData(PathResultAnova)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append('Writing EPH Results : %s' % self.TimeTxt)

                    start = time.clock()
                    self.WavePostStat.WriteIntermediateResult(self.PathResult)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append('Writing intermediater EPH Results : %s' % self.TimeTxt)
                    self.WavePostStat.file.close()


        # calcul PostHoc on wave and/or GFP
        if self.PostHocCheck:

            self.WavePostHoc = Stat.PostHoc(self.H5, self.Mainframe)

            # Parametric
            if self.PostHocParam:
                if self.AnalyseType in ["GFP Only", "Both"] and self.doPostHocParamGFP:
                    self.WavePostHoc.Param(DataGFP=True)
                    self.progressTxt.append('Parametric PostHoc (GFP) : %s' % self.WavePostHoc.elapsedTime)

                if self.AnalyseType in ["All Electrodes", "Both"] and self.doPostHocParamElect:
                    self.WavePostHoc.Param()
                    self.progressTxt.append('Parametric PostHoc (All Electrodes) : %s' % self.WavePostHoc.elapsedTime)

            # Non Parametric
            else:
                if self.AnalyseType in ["GFP Only", "Both"] and self.doPostHocNonParamGFP:
                    self.WavePostHoc.NonParam(self.PostHocIteration, DataGFP=True)
                    self.progressTxt.append('Non-Parametric PostHoc (GFP) : %s' % self.WavePostHoc.elapsedTime)

                if self.AnalyseType in ["All Electrodes", "Both"] and self.doPostHocNonParamElect:
                    self.WavePostHoc.NonParam(self.PostHocIteration)
                    self.progressTxt.append('Non-Parametric PostHoc (All Electrodes) : %s' % self.WavePostHoc.elapsedTime)

            # TODO: Make sure that the h5 files are always closed at the end
            self.WavePostHoc.file.close()
            self.Cancel = self.WavePostHoc.Cancel

            # Post Stat (PostHoc) i.e Mathematical Morphology, write
            # Data
            if not self.Cancel:
                ResultName = 'PostHoc'
                PathResultPostHoc = os.path.abspath("/".join([self.PathResult, ResultName]))

                if not os.path.exists(PathResultPostHoc):
                    os.makedirs(PathResultPostHoc)

                if self.AnalyseType in ["GFP Only", "Both"]:

                    start = time.clock()
                    self.WavePostStat = PostStat.Data(self.H5, self, Anova=False, DataGFP=True, Param=self.PostHocParam)
                    self.WavePostStat.MathematicalMorphology(self.PostHocAlpha, TF=self.PostHocPtsConsec, SpaceCriteria=self.PostHocClust, SpaceFile=self.SpaceFile)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append('Multiple Test Correction on PostHoc (GFP): %s' % self.TimeTxt)

                    start = time.clock()
                    self.WavePostStat.WriteData(PathResultPostHoc)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append('Writing EPH Results on PostHoc(GFP) : %s' % self.TimeTxt)
                    self.WavePostStat.file.close()

                if self.AnalyseType in ["All Electrodes", "Both"]:

                    start = time.clock()
                    self.WavePostStat = PostStat.Data(self.H5, self, Anova=False, DataGFP=False, Param=self.PostHocParam)
                    self.WavePostStat.MathematicalMorphology(self.PostHocAlpha, TF=self.PostHocPtsConsec, SpaceCriteria=self.PostHocClust, SpaceFile=self.SpaceFile)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append('Multiple Test Correction on PostHoc (All electrodes): %s' % self.TimeTxt)

                    start = time.clock()
                    self.WavePostStat.WriteData(PathResultPostHoc)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append('Writing EPH Results on PostHoc : %s' % self.TimeTxt)
                    self.WavePostStat.file.close()



    def calcAnovaIS(self):

        # TODO: check for reruns

        if self.AnovaCheck:
            if CalculAnova:
                self.IS = Stat.Anova(self.H5, self)
                if self.AnovaParam:  # parametric
                    start = time.clock()
                    self.IS.Param()
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append("".join(['Parametric Anova : ', self.TimeTxt]))
                    AllTime = self.IS.file.createArray('/Result/All', 'Anova_ElapsedTime', self.TimeTxt)

                else:  # non param
                    start = time.clock()
                    self.IS.NonParam(self.AnovaIteration)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append("".join(['Non-Parametric Anova : ', self.TimeTxt]))
                    AllTime = self.IS.file.createArray('/Result/All', 'Anova_ElapsedTime', self.TimeTxt)

                self.Cancel = self.IS.Cancel
                self.IS.file.close()

            # Post Stat (ANOVA) i.e Mathematical Morphology, write Data
            if not self.Cancel:
                ResultName = 'Anova'
                PathResultAnova = os.path.abspath( "/".join([PathResult, ResultName]))
                if not os.path.exists(PathResultAnova):
                    os.makedirs(PathResultAnova)
                start = time.clock()
                self.ISPostStat = PostStat.Data(self.H5, self, Anova=True, DataGFP=False, Param=self.AnovaParam)
                self.ISPostStat.MathematicalMorphology(self.AnovaAlpha, TF=self.AnovaPtsConsec, SpaceCriteria=self.AnovaClust, SpaceFile=self.SpaceFile)
                end = time.clock()
                elapsed = end - start
                self.extractTime(elapsed)
                self.progressTxt.append("".join(['Multiple Test Correction : ', self.TimeTxt]))

                start = time.clock()
                self.ISPostStat.WriteData(PathResultAnova)
                end = time.clock()
                elapsed = end - start
                self.extractTime(elapsed)
                self.progressTxt.append("".join(['Writing EPH Results : ', self.TimeTxt]))

                start = time.clock()
                self.ISPostStat.WriteIntermediateResult(PathResult)
                end = time.clock()
                elapsed = end - start
                self.extractTime(elapsed)
                self.progressTxt.append("".join(['Writing intermediater EPH Results : ', self.TimeTxt]))

                self.ISPostStat.file.close()

        # PostHoc on inverse space
        if self.PostHocCheck:
            if CalculPostHoc:
                self.ISPostHoc = Stat.PostHoc(self.H5, self)
                if self.PostHocParam:  # parametric
                    start = time.clock()
                    self.ISPostHoc.Param()
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append("".join(['Parametric PostHoc : ', self.TimeTxt]))
                    AllTime = self.ISPostHoc.file.createArray('/Result/All', 'PostHoc_ElapsedTime', self.TimeTxt)
                else:  # Non param
                    start = time.clock()
                    self.ISPostHoc.NonParam(self.PostHocIteration)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append("".join(['Parametric PostHoc (All Electrodes) : ', self.TimeTxt]))
                    AllTime = self.ISPostHoc.file.createArray('/Result/All', 'PostHoc_ElapsedTime', self.TimeTxt)
                self.Cancel = self.ISPostHoc.Cancel
                self.ISPostStat.file.close()

            if not self.Cancel:
                ResultName = 'PostHoc'
                PathResultPostHoc = os.path.abspath("/".join([PathResult, ResultName]))

                if not os.path.exists(PathResultPostHoc):
                    os.makedirs(PathResultPostHoc)

                start = time.clock()
                self.ISPostStat = PostStat.Data(self.H5, self, Anova=False, DataGFP=False, Param=self.PostHocParam)
                self.ISPostStat.MathematicalMorphology(self.PostHocAlpha, TF=self.PostHocPtsConsec, SpaceCriteria=self.PostHocClust, SpaceFile=self.SpaceFile)
                end = time.clock()
                elapsed = end - start
                self.extractTime(elapsed)
                self.progressTxt.append("".join(['Multiple Test Correction on PostHoc : ', self.TimeTxt]))

                start = time.clock()
                self.ISPostStat.WriteData(PathResultPostHoc)
                end = time.clock()
                elapsed = end - start
                self.extractTime(elapsed)
                self.progressTxt.append("".join(['Writing EPH Results on PostHoc : ', self.TimeTxt]))
                self.ISPostStat.file.close()


    def checkIfCancel(self):

        # If cancel press
        if self.Cancel:
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
            self.Mainframe.PanelData.TxtProgress.SetLabel("Calculation Cancel by user")
        else:
            self.Mainframe.PanelData.TxtProgress.SetLabel("\n".join(self.progressTxt))
            # self.writeVrb(self.H5, PathResult)
            dlg = wx.MessageDialog(self.Mainframe, style=wx.OK | wx.CANCEL, message='Work is done enjoy your results !!!! ;-)')
            retour = dlg.ShowModal()
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
            description = h5file.getNode(nodePath+'/'+node).description
            h5file.removeNode(nodePath+'/'+node, recursive=True)
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
            Param += '\tConsecutive Time Frame = %s\n' % self.PostHocPtsConsec

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
        ModelInfo = [e for e in ModelTmp.replace('\n', '\t').split('\t')
                     if e != '']
        ModelInfoTxt += 'Subject         %s\n' % ModelInfo[1]
        ModelInfoTxt += 'Factor          %s\n' % ModelInfo[3]
        ModelInfoTxt += 'Within Factor   %s\n' % ModelInfo[5]
        ModelInfoTxt += 'Between Factor  %s\n' % ModelInfo[7]
        ModelInfoTxt += 'Covariate       %s\n' % ModelInfo[9]
        ModelInfoTxt += 'R-Formula       %s\n' % ModelInfo[11]

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
