from dataset import Dataset
from rule import Baseline
from abc import ABC, abstractmethod

class Algorithm(ABC):
    """Abstract class for ESMAM/ESMAMDS"""

    def __init__(self, dataset, baseline, alpha) -> None:
        self._dataset: Dataset = dataset
        self._baseline: Baseline = baseline
        self._alpha: float = alpha
        self._rule_set: list = []

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

    @abstractmethod
    def results(self) -> set():
        return self.rule_set
