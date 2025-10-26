import dataclasses
from typing import Callable
import time
from tabulate import tabulate

@dataclasses.dataclass
class Interval:
    low: float
    high: float


@dataclasses.dataclass
class SecantRaphsonRoot:
    root: float
    iterations: int
    error: float
    time: float = 0.0

@dataclasses.dataclass
class SecantRaphsonResult:
    interval: Interval
    root: SecantRaphsonRoot

class SecantRaphsonRootFinder:
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
    
    def _findRootInInterval(self, func: Callable[[float],float], interval: Interval) -> SecantRaphsonRoot | None:
        x0 = interval.low
        x1 = interval.high
        startTime = time.perf_counter()
        for i in range(self.rootFindingMaximumIterations):
            if func(x1) - func(x0) == 0:
                return None
            x2 = x1 - (func(x1)* (x1 - x0) / (func(x1) - func(x0)))
            if abs(x2 - x1) < self.rootTolerance:
                endTime = time.perf_counter()
                return SecantRaphsonRoot(root=x2, iterations=i+1, error=abs(x2 - x1), time=endTime - startTime)
            x0 = x1
            x1 = x2
        return None
    
    def findRoots(self, func: Callable[[float],float]) -> list[SecantRaphsonResult] | None:
        intervals = self.findIntervals(func)
        if not intervals:
            return None
        
        results: list[SecantRaphsonResult] = []
        for interval in intervals:
            root = self._findRootInInterval(func, interval)
            if root is not None:
                results.append(SecantRaphsonResult(root=root, interval=interval))
        return results

    def printSecantResults(self, roots: list[SecantRaphsonResult]):
        tableData = []
        for result in roots:
            tableData.append([f"[{result.interval.low}, {result.interval.high}]", result.root.root, result.root.iterations, result.root.error, result.root.time * 1000])
        print(tabulate(tableData, headers=["Interval", "Root (x)", "Iterations", "Error", "Time (milliseconds)"]))

if __name__ == "__main__":
    # Example usage
    def func(x):
        return x**2 - 5*x - 2

    secantFinder = SecantRaphsonRootFinder(intervalStartPoint=-200.0, intervalStepSize=0.1, intervalMaxSteps=60000, rootTolerance=1e-7, rootFindingMaximumIterations=10000000)
    roots = secantFinder.findRoots(func)
    if roots:
        secantFinder.printSecantResults(roots)
    else:
        print("No roots found in the specified intervals.")