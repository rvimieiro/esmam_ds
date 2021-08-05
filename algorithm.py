from util import dataset
from util import baseline
from abc import ABC, abstractmethod


class Algorithm(ABC):
    """Abstract class for ESMAM/ESMAMDS"""

    def __init__(self, dataset: dataset.Dataset,
                 baseline: baseline.Baseline, alpha: float) -> None:
        self._dataset: dataset.Dataset = dataset
        self._baseline: baseline.Baseline = baseline
        self._alpha: float = alpha
        self._rules: list = []

    @abstractmethod
    def _searchInitialisation(self):
        pass

    @abstractmethod
    def _subgroupSearch(self):
        """execute a colony of ants"""
        pass

    @abstractmethod
    def _subgroupUpdate(self) -> None:
        pass

    @abstractmethod
    def _updateUncoveredCases(self) -> None:
        pass

    @abstractmethod
    def run(self) -> None:
        pass

    def results(self) -> set():
        return self.rules
