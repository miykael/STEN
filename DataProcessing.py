import wx
import numpy as np
from DefineModel import DefineModel
from Covariate import CovariateDefinition
from Eph import Eph


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
        Model = DefineModel(Level.tolist(), Subject.tolist(),
                            Between.tolist(), Covariate.tolist())

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
            info.InfoGroup, 'ColCovariate',
            info.ModelDef.ModelFull.CovariateIndex)
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
            dlg = wx.MessageDialog(None,
                                   'Do you have different Covariate Value for each Within Subject Factor?',
                                   "Covariate Data", wx.YES_NO |
                                   wx.YES_DEFAULT | wx.ICON_QUESTION)
            dlg.SetSize((800, 800))
            response = dlg.ShowModal()
            if response == wx.ID_YES:
                ModelModif = CovariateDefinition(Model.Within,
                                                 Model.Groupe,
                                                 Model.Subject,
                                                 Model.Covariate,
                                                 FactorName,
                                                 NameBetween,
                                                 NameCovariate)
                if ModelModif.Correction:
                    Covariate = info.file.createArray(
                        info.ModelGroup, 'Covariate', ModelModif.Covariate)
                elif ModelModif.Correction is False:
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
        dlg = wx.ProgressDialog('File extraction',
                                'Files extraction : 0 %',
                                (Nbsujet * NbCombi + 1),
                                None,
                                wx.PD_REMAINING_TIME)
        dlg.SetSize((200, 130))
        n = 0
        ErrorEph = []
        for cond, i in enumerate(Within):
            if type(i) == list:
                for sujet, e in enumerate(i):
                    try:
                        Name = ['Subject', str(sujet)]
                        SubjectGroup.append(
                            info.file.createGroup(info.DataGroup,
                                                  "".join(Name)))
                        SubjectGroupGFP.append(
                            info.file.createGroup(info.DataGFPGroup,
                                                  "".join(Name)))
                    except:
                        pass
                    NameEph = e
                    try:
                        EphData = Eph(NameEph)
                        CondName = ['Condition', str(cond)]
                        if EphData.tf == 1:
                            Data = info.file.createArray(
                                SubjectGroup[sujet], "".join(CondName),
                                EphData.data.reshape((1,
                                                      EphData.data.shape[0])))
                            Data = info.file.createArray(
                                SubjectGroupGFP[sujet],
                                "".join(CondName), EphData.data.std(0))
                        elif EphData.electrodes == 1:
                            Data = info.file.createArray(
                                SubjectGroupGFP[sujet],
                                "".join(CondName), EphData.data.data)
                            Data = info.file.createArray(
                                SubjectGroup[sujet], "".join(CondName),
                                EphData.data.reshape((EphData.data.shape[0],
                                                      1)))
                        else:
                            Data = info.file.createArray(
                                SubjectGroupGFP[sujet],
                                "".join(CondName), EphData.data.std(1))
                            Data = info.file.createArray(
                                SubjectGroup[sujet],
                                "".join(CondName), EphData.data)
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
                            SubjectGroupGFP[sujet],
                            "".join(CondName), EphData.data.std(0))
                    elif EphData.electrodes == 1:
                        Data = info.file.createArray(
                            SubjectGroupGFP[sujet],
                            "".join(CondName), EphData.data)
                    else:
                        Data = info.file.createArray(
                            SubjectGroupGFP[sujet],
                            "".join(CondName), EphData.data.std(1))
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
                [int(EphData.tf), int(EphData.electrodes),
                 int(NbCombi), int(Nbsujet)]))
            Fs = info.file.createArray(
                info.InfoGroup, 'FS', np.array(EphData.fs))
        else:
            ErrorEph = info.file.createArray(info.ErrorGroup, 'Eph', ErrorEph)

        try:
            ModelModif.Destroy()
        except:
            pass
