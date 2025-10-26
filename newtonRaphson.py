import dataclasses
from typing import Callable
import time
from tabulate import tabulate

@dataclasses.dataclass
class Interval:
    low: float
    high: float


@dataclasses.dataclass
class NewtonRaphsonRoot:
    root: float
    iterations: int
    error: float
    time: float = 0.0

@dataclasses.dataclass
class NewtonRaphsonResult:
    root: NewtonRaphsonRoot

class NewtonRaphsonRootFinder:
    def __init__(self, intervalStartPoint:float = 0.0, intervalStepSize:float = 1.0, intervalMaxSteps:int = 1000, rootTolerance:float = 1e-7, rootFindingMaximumIterations:int = 1000):
        self.intervalStartPoint = intervalStartPoint
        self.intervalStepSize = intervalStepSize
        self.intervalMaxSteps = intervalMaxSteps
        self.rootTolerance = rootTolerance
        self.rootFindingMaximumIterations = rootFindingMaximumIterations
    
    def findIntervals(self, func: Callable[[float],float]) -> list[Interval]:
        value:float = self.intervalStartPoint
        intervals: list[Interval] = []

        for _ in range(self.intervalMaxSteps):
            nextValue:float = value + self.intervalStepSize
            lowResult: float = func(value)
            highResult: float = func(nextValue)
            if lowResult * highResult < 0:
                intervals.append(Interval(low=value, high=nextValue))
            value = nextValue
        return intervals
    
    def _findRootInInterval(self, func: Callable[[float],float], derivativeFunc: Callable[[float],float], interval: Interval) -> NewtonRaphsonRoot | None:
        x0 = (interval.low + interval.high) / 2.0
        startTime = time.perf_counter()
        for i in range(self.rootFindingMaximumIterations):
            x1 = x0 - (func(x0) / derivativeFunc(x0))
            if abs(x1 - x0) < self.rootTolerance:
                endTime = time.perf_counter()
                return NewtonRaphsonRoot(root=x1, iterations=i+1, error=abs(x1 - x0), time=endTime - startTime)
            x0 = x1
        return None
    
    def findRoots(self, func: Callable[[float],float], derivativeFunc: Callable[[float],float]) -> list[NewtonRaphsonResult] | None:
        intervals = self.findIntervals(func)
        if not intervals:
            return None
        
        results: list[NewtonRaphsonResult] = []
        for interval in intervals:
            root = self._findRootInInterval(func, derivativeFunc, interval)
            if root is not None:
                results.append(NewtonRaphsonResult(root=root))
        return results

    def printRoots(self, roots: list[NewtonRaphsonResult]):
        tableData = []
        for result in roots:
            tableData.append([result.root.root, result.root.iterations, result.root.error, result.root.time * 1000])
        print(tabulate(tableData, headers=["Root (x)", "Iterations", "Error", "Time (milliseconds)"]))

if __name__ == "__main__":
    # Example usage
    def func(x: float) -> float:
        return x**2 - 5*x - 2

    def derivativeFunc(x: float) -> float:
        return 2*x - 5

    rootFinder = NewtonRaphsonRootFinder(intervalStartPoint=-200.0, intervalStepSize=0.1, intervalMaxSteps=60000, rootTolerance=1e-7, rootFindingMaximumIterations=10000000)
    roots = rootFinder.findRoots(func, derivativeFunc)
    if roots:
        rootFinder.printRoots(roots)
    else:
        print("No roots found in the specified intervals.")