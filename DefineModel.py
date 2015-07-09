import numpy as np


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
