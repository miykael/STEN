import wx
import wx.lib.sheet as sheet
import numpy as np
import os
import tables
import Stat
from EntryPanel import DataEntry
from FactorDefinition import FactorDef

# tables: /Data/*subject/*condition # array
# /DataGFP/*subject/*condition # array
# /Model/Within # array
# /Model/Between # array
# /Model/Covariate # array
# /Model/Subject # array
# /Names/Within # List
# /Names/Between
# /Names/Covariate
# /Info/Shape
# /Info/FS # frequncy sampling
# /Info/level # array
# /Info/ColFactor
# /Info/ColWithin
# /Info/ColBetween
# /Info/ColCovaraite
# /Info/Param # info si parametric ou non
# /Sheet/Value # list
# /Sheet/NoEmptyCol # array
# /Sheet/ColName # list
# /Sheet/Dim # array
# /Error/EPH
# /Result/Anova/All/P # P value for All electrodes and IS
# /Result/Anova/All/F # F value only in parametric
# /Result/Anova/GFP/P # P value for GFP
# /Result/Anova/GFP/F # F value
# /Result/PostHoc/All/P # P value for All electrodes and IS
# /Result/PostHoc/All/T # T value
# /Result/PostHoc/GFP/P # P value for GFP
# /Result/PostHoc/GFP/T # T value
# /Result/IntermediateResult # place for storing intermediate results


class info(wx.Panel):

    """ TODO: translate to english
    Panle de gauche de l'application demande les dossier EPH, résultats, les facteurs, ...."""

    def __init__(self, Conteneur, Main):
        #wx.Frame.__init__(self, None, -1, title = "test", size = (500,300))
        wx.Panel.__init__(self, parent=Conteneur)
        FrameSizer = wx.BoxSizer(wx.VERTICAL)
        # definition des OutPut
        self.PathResult = None
        self.NbFactor = 0
        self.Level = {}
        self.Analyse = None
        self.Main = Conteneur
        self.ExportData = Main
        self.ExportData.H5 = []
        # panel 1 = folders
        ##############
        # définition panel 1
        self.PanelFichier = wx.Panel(self, -1)
        PanelFichierSizer = wx.BoxSizer(wx.VERTICAL)
        PanelFichierSizer.AddSpacer(20)

        # selection Load old file
        PanelLoad = wx.Panel(self.PanelFichier, -1)
        PanelLoadSizer = wx.BoxSizer(wx.HORIZONTAL)
        PanelLoadSizer.AddSpacer(5)
        self.DataFile = wx.TextCtrl(
            PanelLoad, -1, value="", style=wx.TE_READONLY, size=(550, 21))
        self.DataFile.SetBackgroundColour(wx.WHITE)
        PanelLoadSizer.Add(self.DataFile, 0, wx.EXPAND)
        ButtonDataLoad = wx.Button(
            PanelLoad, 4, label="Load File", size=(108, 23))
        PanelLoadSizer.Add(ButtonDataLoad, 0, wx.EXPAND)
        PanelLoad.SetSizer(PanelLoadSizer)
        PanelFichierSizer.Add(PanelLoad, 0, wx.EXPAND)
        PanelFichierSizer.AddSpacer(10)

        #  selection result folder
        PanelRes = wx.Panel(self.PanelFichier, -1)
        PanelResSizer = wx.BoxSizer(wx.HORIZONTAL)
        PanelResSizer.AddSpacer(5)
        self.TextResult = wx.TextCtrl(
            PanelRes, -1, value="", style=wx.TE_READONLY, size=(550, 21))
        self.TextResult.SetBackgroundColour(wx.WHITE)
        PanelResSizer.Add(self.TextResult, 0, wx.EXPAND)
        self.ButtonResult = wx.Button(
            PanelRes, 2, label="Select result folder", size=(108, 23))
        PanelResSizer.Add(self.ButtonResult, 0, wx.EXPAND)
        PanelRes.SetSizer(PanelResSizer)
        PanelFichierSizer.Add(PanelRes, 0, wx.EXPAND)
        PanelFichierSizer.AddSpacer(10)

        # lie les sizer au panel
        self.PanelFichier.SetSizer(PanelFichierSizer)
        # on mets le panel de fichier dans le sizer de la frame
        FrameSizer.Add(self.PanelFichier, 0, wx.EXPAND)
        FrameSizer.AddSpacer(10)

        ###############
        # panel 2 = INfo avec creation Data + information sur les datas
        # text data
        PanelInfo = wx.Panel(self, -1)
        InfoSizer = wx.BoxSizer(wx.HORIZONTAL)
        InfoSizer.AddSpacer(5)
        PanelData = wx.Panel(PanelInfo, -1)
        DataSizer = wx.BoxSizer(wx.VERTICAL)
        DataTxt = wx.StaticText(
            PanelData, -1, label="Data selection ", style=wx.CENTRE)
        DataSizer.Add(DataTxt, 0, wx.EXPAND)
        DataSizer.AddSpacer(5)
        # panel 3 avec les boutton création
        ButtonDataCreate = wx.Button(
            PanelData, 3, label="Create Data File / Modifiy data")
        DataSizer.Add(ButtonDataCreate, 0, wx.EXPAND)
        PanelData.SetSizer(DataSizer)
        InfoSizer.Add(PanelData)
        InfoSizer.AddSpacer(100)
        self.TxtInfo = wx.StaticText(
            PanelInfo, -1, label="", style=wx.ALIGN_LEFT)
        InfoSizer.Add(self.TxtInfo)
        PanelInfo.SetSizer(InfoSizer)
        # lie les sizer au panel
        FrameSizer.Add(PanelInfo, 0, wx.EXPAND)
        FrameSizer.AddStretchSpacer()

        # Panel Progression
        PanelFinal = wx.Panel(self, -1)
        FinalSizer = wx.BoxSizer(wx.HORIZONTAL)
        FinalSizer.AddSpacer(50)
        self.ProgressTxt = wx.StaticText(
            PanelFinal, -1, label="", style=wx.ALIGN_LEFT)
        FinalSizer.Add(self.ProgressTxt, 0, wx.EXPAND)
        PanelFinal.SetSizer(FinalSizer)

        # lie les sizer au panel
        FrameSizer.Add(PanelFinal, 0, wx.EXPAND)
        FrameSizer.AddStretchSpacer()
        # on lie le size au frame sizer
        self.SetSizer(FrameSizer)
        # FrameSizer.SetSizeHints(self)
        # self.SetSize((800,200))

        # evenement
        # wx.EVT_BUTTON(self, 1,self.Eph)
        wx.EVT_BUTTON(self, 2, self.Result)
        wx.EVT_BUTTON(self, 3, self.CreateData)
        wx.EVT_BUTTON(self, 4, self.LoadData)

    def Result(self, event):
        self.TextResult.SetBackgroundColour(wx.WHITE)
        wx.InitAllImageHandlers()
        dlg = wx.DirDialog(None, "select Result folder",
                           defaultPath=os.getcwd(), style=wx.DD_DEFAULT_STYLE)
        retour = dlg.ShowModal()
        self.PathResult = dlg.GetPath()
        os.chdir(self.PathResult)
        self.TextResult.SetLabel(dlg.GetPath())
        dlg.Show(True)
        dlg.Destroy()

    def LoadData(self, event):
        dlg = wx.FileDialog(
            None, "Load H5 file", wildcard="*.h5", style=wx.FD_OPEN)
        text = []
        retour = dlg.ShowModal()
        if retour == wx.ID_OK:
            chemin = dlg.GetPath()
            fichier = dlg.GetFilename()
            self.DataFile.SetLabel(chemin)
            self.ExportData.H5 = chemin
            dlg.Destroy()
            dlg.Show(True)
            info = ReturnInfomation(chemin)
            self.TxtInfo.SetLabel("".join(info.text))
            if info.CovariatePresent:
                self.ExportData.AnovaWave.PostHocCheckBox.Disable()
                self.ExportData.AnovaIS.PostHocCheckBox.Disable()
                self.ExportData.AnovaWave.PostHocCheckBox.SetValue(False)
                self.ExportData.AnovaIS.PostHocCheckBox.SetValue(False)

            else:
                self.ExportData.AnovaWave.PostHocCheckBox.Enable()
                self.ExportData.AnovaIS.PostHocCheckBox.Enable()

        else:
            self.ExportData.H5 = []
            self.DataFile.SetLabel('')

    def CreateData(self, event):
        Data = DataEntry(self)
        Data.Show(True)
        self.ExportData.Show(False)


class DataProcessing:

    def __init__(self, info):
        ColName = []
        for i in info.Data.NoEmptyCol:
            ColName.append(str(info.Sheet.GetColLabelValue(i)))
        Level = info.Level
        Within = info.Within
        Between = info.Between
        Subject = info.Subject
        Covariate = info.Covariate
        FactorName = info.FactorName
        # lire les EPH
        Nbsujet = len(Subject)
        NbCombi = Level.prod()
        if Between.any():
            NameBetween = []
            for i in info.BetweenIndex:
                NameBetween.append(ColName[i])
        else:
            NameBetween = False

        if Covariate.any():
            NameCovariate = []
            for i in info.CovariateIndex:
                NameCovariate.append(ColName[i])

        else:
            NameCovariate = False

        # demande si le Covariate est différentes pour les facteur within
        Model = DefineModel(
            Level.tolist(), Subject.tolist(), Between.tolist(), Covariate.tolist())

        # ecriture dans la table des donnée lié aux stat et autres info utilse
        # nom, ...
        info.FactorName = [str(f) for f in info.FactorName]

        for i, col in enumerate(info.Data.Value):
            if type(col) == list:
                col = [str(n) for n in col]
                info.Data.Value[i] = col
            else:
                info.Data.Value[i] = str(col)
        info.ColFactor = [str(n) for n in info.ColFactor]
        Dim = []
        Dim.append(info.Sheet.GetNumberRows())
        Dim.append(info.Sheet.GetNumberCols())

        # les vecteur/array des model pWithin, between, covariate et sujet
        WithinH5 = info.file.createArray(
            info.ModelGroup, 'Within', Model.Within)
        BetweenH5 = info.file.createArray(
            info.ModelGroup, 'Between', Model.Groupe)
        SubjectH5 = info.file.createArray(
            info.ModelGroup, 'Subject', Model.Subject)

        # info sur les colone Within
        ColFactor = info.file.createArray(
            info.InfoGroup, 'ColFactor', info.ColFactor)
        ColWithin = info.file.createArray(
            info.InfoGroup, 'ColWithin', info.ModelDef.ModelFull.WithinIndex)
        if info.ModelDef.ModelFull.BetweenIndex == []:
            info.ModelDef.ModelFull.BetweenIndex = -1
        ColBetween = info.file.createArray(
            info.InfoGroup, 'ColBetween', info.ModelDef.ModelFull.BetweenIndex)
        if info.ModelDef.ModelFull.CovariateIndex == []:
            info.ModelDef.ModelFull.CovariateIndex = -1
        ColCovariate = info.file.createArray(
            info.InfoGroup, 'ColCovariate', info.ModelDef.ModelFull.CovariateIndex)
        # info général, les niveau des facteur Within (pour modification des
        # entrées)
        if Level.any() == False:
            Level = False
        Level = info.file.createArray(info.InfoGroup, 'Level', Level)
        # info les valeur des cellule
        SheetValue = info.file.createArray(
            info.SheetGroup, 'Value', info.Data.Value)
        # les colone non vide
        SheetNoEmptyCol = info.file.createArray(
            info.SheetGroup, 'NoEmptyCol', info.Data.NoEmptyCol)
        # le nom des colone
        ColName = info.file.createArray(info.SheetGroup, 'ColName', ColName)
        # dimenssion du tableur
        Dim = info.file.createArray(info.SheetGroup, 'Dim', Dim)
        # nom des fateur Within
        if info.FactorName == []:
            info.FactorName = False
        FactorName = info.file.createArray(
            info.NamesGroup, 'Within', info.FactorName)
        # nom de between
        BetweenName = info.file.createArray(
            info.NamesGroup, 'Between', NameBetween)
        # nom des covariate
        CovName = info.file.createArray(
            info.NamesGroup, 'Covariate', NameCovariate)

        if Covariate.any():
            # demander si il y a des valeurs différentes de covariate pour les
            # différents niveau des facteurs within
            dlg = wx.MessageDialog(None, 'Do you have different Covariate Value for each Within Subject Factor?',
                                   "Covariate Data", wx.YES_NO | wx.YES_DEFAULT | wx.ICON_QUESTION)
            dlg.SetSize((800, 800))
            response = dlg.ShowModal()
            if response == wx.ID_YES:
                ModelModif = CovariateDefinition(
                    Model.Within, Model.Groupe, Model.Subject, Model.Covariate, FactorName, NameBetween, NameCovariate)
                if ModelModif.Correction:
                    Covariate = info.file.createArray(
                        info.ModelGroup, 'Covariate', ModelModif.Covariate)
                elif ModelModif.Correction == False:
                    Covariate = info.file.createArray(
                        info.ModelGroup, 'Covariate', Model.Covariate)
            else:
                Covariate = info.file.createArray(
                    info.ModelGroup, 'Covariate', Model.Covariate)
                dlg.Destroy()
            dlg.Destroy()
        else:
            Covariate = info.file.createArray(
                info.ModelGroup, 'Covariate', Model.Covariate)

        # Lecture de Eph  et mise dans la table  puis faire les claluls dessus
        # (GFP, ST, ..:)
        SubjectGroup = []
        SubjectGroupGFP = []
        dlg = wx.ProgressDialog(
            'File extraction', 'Files extraction : 0 %', (Nbsujet * NbCombi + 1), None, wx.PD_REMAINING_TIME)
        dlg.SetSize((200, 130))
        n = 0
        ErrorEph = []
        for cond, i in enumerate(Within):
            if type(i) == list:
                for sujet, e in enumerate(i):
                    try:
                        Name = ['Subject', str(sujet)]
                        SubjectGroup.append(
                            info.file.createGroup(info.DataGroup, "".join(Name)))
                        SubjectGroupGFP.append(
                            info.file.createGroup(info.DataGFPGroup, "".join(Name)))
                    except:
                        pass
                    NameEph = e
                    try:
                        EphData = Eph(NameEph)
                        CondName = ['Condition', str(cond)]
                        if EphData.tf == 1:
                            Data = info.file.createArray(SubjectGroup[sujet], "".join(
                                CondName), EphData.data.reshape((1, EphData.data.shape[0])))
                            Data = info.file.createArray(
                                SubjectGroupGFP[sujet], "".join(CondName), EphData.data.std(0))
                        elif EphData.electrodes == 1:
                            Data = info.file.createArray(
                                SubjectGroupGFP[sujet], "".join(CondName), EphData.data.data)
                            Data = info.file.createArray(SubjectGroup[sujet], "".join(
                                CondName), EphData.data.reshape((EphData.data.shape[0], 1)))
                        else:
                            Data = info.file.createArray(
                                SubjectGroupGFP[sujet], "".join(CondName), EphData.data.std(1))
                            Data = info.file.createArray(
                                SubjectGroup[sujet], "".join(CondName), EphData.data)
                    except:
                        ErrorEph.append(NameEph)

                    n += 1
                    pourcent = str(100.0 * n / (Nbsujet * NbCombi))
                    pourcent = pourcent[0:pourcent.find('.') + 3]
                    dlg.Update(
                        n, " ".join(['Files extraction  :', pourcent, '%']))

            else:
                Name = ['Subject', str(cond)]
                SubjectGroup.append(
                    info.file.createGroup(info.DataGroup, "".join(Name)))
                NameEph = i
                try:
                    EphData = Eph(NameEph)
                    Data = info.file.createArray(
                        SubjectGroup[cond], 'Condition', EphData.data)
                    if EphData.tf == 1:
                        Data = info.file.createArray(
                            SubjectGroupGFP[sujet], "".join(CondName), EphData.data.std(0))
                    elif EphData.electrodes == 1:
                        Data = info.file.createArray(
                            SubjectGroupGFP[sujet], "".join(CondName), EphData.data)
                    else:
                        Data = info.file.createArray(
                            SubjectGroupGFP[sujet], "".join(CondName), EphData.data.std(1))
                except:
                    ErrorEph.append(NameEph)
                n += 1
                pourcent = str(100.0 * n / (Nbsujet * NbCombi))
                pourcent = pourcent[0:pourcent.find('.') + 3]
                dlg.Update(n, " ".join(['Files extraction  :', pourcent, '%']))

        dlg.Destroy()
        # Erreur dans la lecture des EPHs
        if ErrorEph == []:
            ErrorEph = False
            ErrorEph = info.file.createArray(info.ErrorGroup, 'Eph', ErrorEph)
            Shape = info.file.createArray(info.InfoGroup, 'ShapeGFP', np.array(
                [int(EphData.tf), 1, int(NbCombi), int(Nbsujet)]))
            Shape = info.file.createArray(info.InfoGroup, 'Shape', np.array(
                [int(EphData.tf), int(EphData.electrodes), int(NbCombi), int(Nbsujet)]))
            Fs = info.file.createArray(
                info.InfoGroup, 'FS', np.array(EphData.fs))
        else:
            ErrorEph = info.file.createArray(info.ErrorGroup, 'Eph', ErrorEph)

        try:
            ModelModif.Destroy()
        except:
            pass

"""lecture: path eph/eph name"""


class Eph:  # lire les Eph, puis faire les claluls dessus (GFP, ST, ..:)

    """ TODO: translate to english
    lecture: path eph/eph name"""

    def __init__(self, PathEph):
        """ TODO: translate to english
        on initialise l'objet eph
        soit on lis des EPH 2 parametres 
        1) PathEph = lieu de l'eph
        2) NameEph = nom de l'eph
        """
        header = open(PathEph).readline()
        header = header.split('\t')
        if len(header) == 1:
            header = open(PathEph).readline()
            header = header.split(' ')
        self.electrodes = int(header[0])
        self.tf = int(header[1])
        try:
            self.fs = int(header[2])
        except:
            self.fs = float(header[2])
        self.data = np.loadtxt(PathEph, skiprows=1)


class CalculSheet(sheet.CSheet):

    def __init__(self, parent, size=(2, 2)):
        sheet.CSheet.__init__(self, parent)
        self.SetNumberRows(30)
        self.SetNumberCols(9)
        self.SetColLabelValue(0, 'subject')


class FactorWithin(wx.Frame):

    """ TODO: translate to english
    définition des facteur Within stype SPSS"""

    def __init__(self, NoEmptyCol, Sheet, Parent, Level, Factor):
        wx.Frame.__init__(
            self, None, -1, title="Within subject definition", size=(200, 250))
        FrameSizer = wx.BoxSizer(wx.VERTICAL)
        self.Level = Level
        self.Factor = Factor
        self.NoEmptyCol = NoEmptyCol
        self.Sheet = Sheet
        self.ColWithin = []
        self.ColBetween = []
        self.ColSubject = []
        self.ColCovariate = []
        self.TabValue = Parent.Data.Value
        self.DataEntry = Parent

        # panel Factor
        PanelFactor = wx.Panel(self, -1)
        FactorSizer = wx.BoxSizer(wx.VERTICAL)
        TextNameFactor = wx.StaticText(
            PanelFactor, -1, label="   Within Subject Factor Name : ")
        FactorSizer.Add(TextNameFactor, 0, wx.ALIGN_LEFT)
        self.FactorName = wx.TextCtrl(PanelFactor, 1, value="")
        FactorSizer.Add(self.FactorName, 0, wx.ALIGN_RIGHT)

        TextNbLevel = wx.StaticText(
            PanelFactor, -1, label="   Number of Levels : ")
        FactorSizer.Add(TextNbLevel, 0, wx.ALIGN_LEFT)
        self.LevelNb = wx.TextCtrl(PanelFactor, 1, value="")
        FactorSizer.Add(self.LevelNb, 0, wx.ALIGN_RIGHT)
        PanelFactor.SetSizerAndFit(FactorSizer)
        FrameSizer.Add(PanelFactor, 0, wx.EXPAND)
        FrameSizer.AddStretchSpacer()

        # Panel button et def
        PanelDef = wx.Panel(self, -1)
        DefSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Panel avec les button
        PanelButton = wx.Panel(PanelDef, -1)
        ButtonSizer = wx.BoxSizer(wx.VERTICAL)
        self.ButtonAdd = wx.Button(PanelButton, 1, label="Add")
        ButtonSizer.Add(self.ButtonAdd, 0, wx.EXPAND)
        self.ButtonClear = wx.Button(PanelButton, 2, label="Clear")
        self.ButtonClear.Disable()
        ButtonSizer.Add(self.ButtonClear, 0, wx.EXPAND)
        self.ButtonChange = wx.Button(PanelButton, 3, label="Change")
        self.ButtonChange.Disable()
        ButtonSizer.Add(self.ButtonChange, 0, wx.EXPAND)
        PanelButton.SetSizerAndFit(ButtonSizer)
        DefSizer.Add(PanelButton, 0, wx.EXPAND)
        # panel avec la liste non modifiable
        PanelList = wx.Panel(PanelDef, -1)
        self.ListFactor = wx.ListBox(
            PanelList, 1, size=(100, 100), style=wx.LB_SINGLE)
        DefSizer.Add(PanelList, wx.EXPAND)
        PanelDef.SetSizerAndFit(DefSizer)
        FrameSizer.Add(PanelDef, 0, wx.EXPAND)
        FrameSizer.AddStretchSpacer()

        # Panel Continue
        PanelContinue = wx.Panel(self, -1)
        ContinueSizer = wx.BoxSizer(wx.VERTICAL)
        ContinueButton = wx.Button(PanelContinue, 4, label="Continue")
        ContinueSizer.Add(ContinueButton, 0, wx.ALIGN_RIGHT)
        PanelContinue.SetSizer(ContinueSizer)
        FrameSizer.Add(PanelContinue, 0, wx.EXPAND)
        self.SetSizer(FrameSizer)
        Factor = []
        for i in range(len(self.Factor)):
            name = []
            name.append(self.Factor[i])
            name.append('(')
            name.append(str(self.Level[i]))
            name.append(')')
            Factor.append("".join(name))
        self.ListFactor.SetItems(Factor)

        # les evenements !!!!
        wx.EVT_BUTTON(self, 1, self.Add)
        wx.EVT_BUTTON(self, 2, self.Clear)
        wx.EVT_BUTTON(self, 3, self.Change)
        wx.EVT_BUTTON(self, 4, self.Continue)
        wx.EVT_LISTBOX(self, 1, self.ItemSelected)

    def ItemSelected(self, event):
        self.ButtonChange.Enable()
        self.ButtonClear.Enable()
        self.ButtonAdd.Disable()
        idx = self.ListFactor.GetSelections()
        self.FactorName.SetValue(self.Factor[idx[0]])
        self.LevelNb.SetValue(str(self.Level[idx[0]]))

    def Add(self, event):

        name = []
        name.append(self.FactorName.GetValue())
        name.append('(')
        name.append(self.LevelNb.GetValue())
        name.append(')')
        Factor = self.ListFactor.GetItems()
        try:
            level = int(self.LevelNb.GetValue())
            if level == 1:
                dlg = wx.MessageDialog(
                    'Level must be bigger than 1', style=wx.OK)
                retour = dlg.ShowModal()
                dlg.Destroy()
                self.FactorName.SetValue('')
                self.LevelNb.SetValue('')
            else:
                self.Level.append(level)
                self.Factor.append(self.FactorName.GetValue())
                Factor.append("".join(name))
                self.ListFactor.DeselectAll()
                self.ListFactor.SetItems(Factor)
                self.FactorName.SetValue('')
                self.LevelNb.SetValue('')

        except:
            dlg = wx.MessageDialog(
                self, 'Numbers of level must be integer', style=wx.OK)
            retour = dlg.ShowModal()
            dlg.Destroy()
            self.FactorName.SetValue('')
            self.LevelNb.SetValue('')

    def Clear(self, event):
        idx = self.ListFactor.GetSelections()
        idx = idx[0]
        self.ListFactor.Delete(idx)
        self.ButtonChange.Disable()
        self.ButtonAdd.Enable()
        self.ButtonClear.Disable()
        self.FactorName.SetValue('')
        self.LevelNb.SetValue('')

    def Change(self, event):
        self.ButtonChange.Disable()
        self.ButtonAdd.Enable()
        self.ButtonClear.Disable()
        idx = self.ListFactor.GetSelections()
        idx = idx[0]
        Factor = self.ListFactor.GetItems()
        name = []
        name.append(self.FactorName.GetValue())
        name.append('(')
        name.append(self.LevelNb.GetValue())
        name.append(')')
        try:
            level = int(self.LevelNb.GetValue())
            if level == 1:
                dlg = wx.MessageDialog(
                    'Level must be bigger than 1', style=wx.OK)
                retour = dlg.ShowModal()
                dlg.Destroy()
                self.FactorName.SetValue(self.Factor[idx])
                self.LevelNb.SetValue(str(self.Level[idx]))
            else:
                self.Level[idx] = level
                self.Factor[idx] = self.FactorName.GetValue()
                Factor[idx] = "".join(name)
                self.ListFactor.SetItems(Factor)
                self.ListFactor.DeselectAll()
                self.FactorName.SetValue('')
                self.LevelNb.SetValue('')
        except:
            dlg = wx.MessageDialog(
                self, 'Numbers of level must be integer', style=wx.OK)
            retour = dlg.ShowModal()
            dlg.Destroy()
            self.FactorName.SetValue(self.Factor[idx])
            self.LevelNb.SetValue(str(self.Level[idx]))

    def Continue(self, event):
        self.ModelFull = FactorDef(self.NoEmptyCol, self.Sheet, self)
        self.ModelFull.Show(True)
        self.Show(False)
        self.DataEntry.FactorName = self.Factor


# Class definition du Model
class DefineModel:

    def __init__(self, level, sujet, groupe, covariate):
        # level,groupe, sujet , covariate are list
        if groupe == []:
            groupevide = True
        else:
            groupevide = False
        if covariate == []:
            covvide = True
        else:
            covvide = False

        groupe = np.array(groupe)
        groupe = groupe.T
        sujet = np.array(sujet)
        covariate = np.array(covariate)
        covariate = covariate.T
        levelArray = np.array(level)
        combi = levelArray.prod()
        condition = combi * len(sujet)
        conditiontmp = condition
        ModelWithin = np.zeros((int(condition), int(len(level))))
        if level != []:
            for k, i in enumerate(level):
                repet = conditiontmp / i
                conditiontmp = repet
                for j in range(i):
                    fact = np.ones((repet, 1)) * j + 1
                    debut = j * repet
                    fin = (j + 1) * repet
                    ModelWithin[debut:fin, k] = fact[:, 0]
                n = j
                while ModelWithin[condition - 1, k] == 0:
                    for j in range(i):
                        n += 1
                        fact = np.ones((repet, 1)) * j + 1
                        debut = n * repet
                        fin = (n + 1) * repet
                        ModelWithin[debut:fin, k] = fact[:, 0]

        else:
            ModelWithin = np.array(False)
        self.Within = ModelWithin

        ModelSujet = np.zeros(int((condition)))
        MarkGroup = 0
        MarkCov = 0
        try:
            ModelGroupe = np.zeros((condition, groupe.shape[1]))
            MarkGroup = 1
        except:
            ModelGroupe = np.zeros(int((condition)))
        try:
            ModelCovariate = np.zeros((condition, covariate.shape[1]))
            MarkCov = 1
        except:
            ModelCovariate = np.zeros(int((condition)))
        combi = int(combi)
        for i in range(combi):
            debut = i * len(sujet)
            fin = (i + 1) * len(sujet)
            ModelSujet[debut:fin] = sujet
            if groupevide:
                   # ModelGroupe=np.array([])
                ModelGroupe = False
            else:
                if MarkGroup == 1:
                    ModelGroupe[debut:fin, :] = groupe
                else:
                    ModelGroupe[debut:fin] = groupe
            if covvide:
                # ModelCovariate=np.array([])
                ModelCovariate = False
            else:
                if MarkCov == 1:
                    ModelCovariate[debut:fin, :] = covariate
                else:
                    ModelCovariate[debut:fin] = covariate
        self.Subject = ModelSujet
        self.Groupe = ModelGroupe
        self.Covariate = ModelCovariate


class Summary:

    def __init__(self, ColWithin, ColBetween, ColSubject, ColCovariate, PanelTxt):
        txt = ['SUMMARY\n']
        txt.append('SUBJECT FACTOR COL :\n')
        txt.append(ColSubject)
        txt.append('\n')
        tmp = ['Within SUBJECT FACTOR COL :\n']
        for i in ColWithin:
            tmp.append(', ')
            tmp.append(i)
        tmp.remove(', ')
        txt.append("".join(tmp))
        txt.append('\n')
        tmp = ['BETWEEN SUBJECT FACTOR COL :\n']
        for i in ColBetween:
            tmp.append(', ')
            tmp.append(i)
        tmp.remove(', ')
        txt.append("".join(tmp))
        txt.append('\n')
        tmp = ['COVARIATE SUBJECT FACTOR COL :\n']
        for i in ColCovariate:
            tmp.append(', ')
            tmp.append(i)
        tmp.remove(', ')
        txt.append("".join(tmp))
        PanelTxt.SetLabel("".join(txt))


class ReturnInfomation:

    def __init__(self, chemin):
        text = []
        info = Stat.Anova(chemin, self)
        info.file.close()
        file = tables.openFile(chemin, mode='r')
        formule = ['R-FORMULA : aov(']
        formule.append(info.Formule)
        formule.append(')\n\n')
        text.append("".join(formule))
        Within = ['Within FACTOR(S) NAME(S)[LEVELS] : ']
        Factor = file.getNode('/Names/Within')
        Factor = Factor.read()
        Level = file.getNode('/Info/Level')
        Level = Level.read()
        if Factor != False:
            for i, f in enumerate(Factor):
                Within.append(', ')
                Within.append(f)
                Within.append(' [')
                Within.append(str(Level[i]))
                Within.append(']')
            Within.remove(', ')
            Within.append('\n\n')
            text.append("".join(Within))

        NameBetween = file.getNode('/Names/Between')
        BetweenFactor = file.getNode('/Model/Between')
        BetweenFactor = BetweenFactor.read()
        NameBetween = NameBetween.read()
        if NameBetween != False:
            between = ['BETWEEN FACTOR(S) NAME(S): ']
            for i, f in enumerate(NameBetween):
                between.append(', ')
                tmp = []
                try:
                    BetweenLevel = str(int(BetweenFactor[:, i].max()))
                except:
                    BetweenLevel = str(int(BetweenFactor.max()))
                tmp.append(f)
                tmp.append('[')
                tmp.append(BetweenLevel)
                tmp.append(']')
                between.append("".join(tmp))
            between.remove(', ')
            between.append('\n\n')
            text.append("".join(between))
        Namecov = file.getNode('/Names/Covariate')
        Namecov = Namecov.read()
        if Namecov != False:
            cov = ['COVARIATE NAME(S): ']
            for f in Namecov:
                cov.append(', ')
                cov.append(f)
            cov.remove(', ')
            cov.append('\n\n')
            text.append("".join(cov))
            self.CovariatePresent = True
        else:
            self.CovariatePresent = False
        ErrorEph = file.getNode('/Error/Eph')
        ErrorEph = ErrorEph.read()
        if ErrorEph == False:
            error = 'ALL EPH FILES ARE READED !!!'
        else:
            error = ['This Eph Files have a problem : \n']
            n = 0
            for i, e in enumerate(ErrorEph):
                if n == 10:
                    n = 0
                    error.append(', ')
                    error.append(e)
                    error.append('\n')
                else:
                    error.append(', ')
                    error.append(e)
            error.remove(', ')
            txt = "".join(error)
            txt = txt.replace(',', '\n')
            dlg = wx.MessageDialog(
                None, txt, "Error Eph Files", wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()
            dlg.Destroy()
        self.text = text
        file.close()


class CovariateDefinition(wx.Dialog):

    def __init__(self, Within, Between, Subject, Covariate, NameWithin, NameBetween, NameCovariate):
        wx.Dialog.__init__(
            self, None, -1, title="Covariate Definition", size=(1000, 500))
        self.MakeModal(True)
        FrameSizer = wx.BoxSizer(wx.VERTICAL)
        # load panel
        self.Correction = []
        PanelSheet = wx.Panel(self, -1)
        SheetSizer = wx.BoxSizer(wx.VERTICAL)
        self.Sheet = CalculSheetCov(PanelSheet)
        SheetSizer.Add(self.Sheet, 0, wx.EXPAND)
        PanelSheet.SetSizer(SheetSizer)
        FrameSizer.Add(PanelSheet, 0, wx.EXPAND)
        FrameSizer.AddSpacer(10)

        ModifPanel = wx.Panel(self, -1)
        ModifiySizer = wx.BoxSizer(wx.HORIZONTAL)
        ButtonCancel = wx.Button(ModifPanel, 1, label="Cancel", size=(108, 23))
        ModifiySizer.Add(ButtonCancel, 0, wx.EXPAND)
        Buttonok = wx.Button(ModifPanel, 2, label="OK", size=(108, 23))
        ModifiySizer.Add(Buttonok, 0, wx.EXPAND)
        ModifPanel.SetSizerAndFit(ModifiySizer)
        FrameSizer.Add(ModifPanel, 0, wx.EXPAND)
        self.SetSizerAndFit(FrameSizer)

        wx.EVT_BUTTON(self, 1, self.Cancel)
        wx.EVT_BUTTON(self, 2, self.OK)
        self.Show(True)
        # subject
        row = 0
        NbRow = len(Subject)
        NbCol = 1

        if len(Within.shape) != 1:
            NbCol += Within.shape[1]
        else:
            NbCol += 1

        if len(Covariate.shape) != 1:
            NbCol += Covariate.shape[1]
        else:
            NbCol += 1

        try:
            if len(Between.shape) != 1:
                NbCol += Between.shape[1]
            else:
                NbCol += 1
        except:
            pass

        self.Sheet.SetNumberRows(NbRow)
        self.Sheet.SetNumberCols(NbCol)
        for s in Subject:
            value = str(int(s))
            self.Sheet.SetCellValue(row, 0, value)
            row += 1
        col = 1
        ColDisable = [0]
        # Within
        if NameWithin != False:
            for i, n in enumerate(NameWithin):
                self.Sheet.SetColLabelValue(col, n)
                if len(Within.shape) != 1:
                    ColValues = Within[:, i]
                else:
                    ColValues = Within
                row = 0
                for v in ColValues:
                    value = str(int(v))
                    self.Sheet.SetCellValue(row, col, value)
                    row += 1
                ColDisable.append(col)
                col += 1

        # Between
        if NameBetween != False:
            for i, n in enumerate(NameBetween):
                self.Sheet.SetColLabelValue(col, n)
                if len(Between.shape) != 1:
                    ColValues = Between[:, i]
                else:
                    ColValues = Between
                row = 0
                for v in ColValues:
                    value = str(int(v))
                    self.Sheet.SetCellValue(row, col, value)
                    row += 1
                ColDisable.append(col)
                col += 1
        self.ColCov = []
        # Covariate
        if NameCovariate != False:
            for i, n in enumerate(NameCovariate):
                self.Sheet.SetColLabelValue(col, n)
                if len(Covariate.shape) != 1:
                    ColValues = Covariate[:, i]
                else:
                    ColValues = Covariate
                row = 0
                for v in ColValues:
                    value = str(float(v))
                    self.Sheet.SetCellValue(row, col, value)
                    row += 1
                self.ColCov.append(col)
                col += 1
        self.NbRow = NbRow
        self.Sheet.Bind(wx.EVT_CHAR, self.OnKeyPress)
        self.Sheet.DisableCellEditControl
        self.ShowModal()

    def OK(self, event):
        NewModelCov = np.zeros((self.NbRow, len(self.ColCov)))
        for i, c in enumerate(self.ColCov):
            for r in range(self.NbRow):
                cell = self.Sheet.GetCellValue(r, c)
                NewModelCov[r, i] = float(cell)
        self.Covariate = NewModelCov
        self.Correction = True
        self.MakeModal(False)
        self.Close()

    def Cancel(self, event):
        self.Correction = False
        self.MakeModal(False)
        self.Close()

    def OnKeyPress(self, event):
        if event.GetKeyCode() == 3:
            self.Sheet.Copy()
        elif event.GetKeyCode() == 22:
            self.Sheet.Paste()
        else:

            event.Skip()


class CalculSheetCov(sheet.CSheet):

    def __init__(self, l):
        sheet.CSheet.__init__(self, parent)
        self.SetNumberRows(40)
        self.SetNumberCols(9)
        self.SetColLabelValue(0, 'subject')
