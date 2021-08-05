import dataset
from abc import ABC, abstractmethod
from enum import Enum


class Baseline(Enum):
    POPULATION = 1
    COMPLEMENT = 2


class Algorithm(ABC):
    """Abstract class for ESMAM/ESMAMDS"""

    def __init__(self, dataset: dataset.Dataset,
                 baseline: Baseline, alpha: float) -> None:
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
