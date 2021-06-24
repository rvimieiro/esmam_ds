import pandas as pd
import statsmodels.api as sm
from lifelines import KaplanMeierFitter
from utils import NoIndent



class Rule:
    """
    funcionalidades:
    1. adicionar e remover itens do antecedente
    2. retornar o antecedente
    3. calcular a qualidade
    4. obter a cobertura, tamanho dela
    5. implementar representações __repr__, __str__
    """

    def __init__(self, dataset, baseline):

        # agora eh uma lista
        self.antecedent = None
        self.quality = 0.0
        self._Dataset = dataset #referencia
        self._baseline = baseline #enum
        # https://docs.python.org/3/library/enum.html#enum.Flag
        # from enum import Enum
        # class Baseline(Enum):
        #     POPULATION = 1
        #     COMPLEMENT = 2
        # Baseline.POPULACAO
        # Baseline.COMPLEMENTO
        # if self._baseline == Baseline.POP:


        def __repr__(self):
            pass

        def __str__(self):
            pass


        


if __name__ == "__main__":
    enumerate()