from typing import Callable
import math
import dataclasses
from tabulate import tabulate
import time

@dataclasses.dataclass
class Interval:
    low: float
    high: float

@dataclasses.dataclass
class BisectionRoot:
    root: float
    iterations: int
    error: float
    time: float = 0.0


@dataclasses.dataclass
class BisectionResult:
    interval: Interval
    root: BisectionRoot



class BisectionRootFinder:
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


    def _findRootInInterval(self, func: Callable[[float],float], interval: Interval) -> BisectionRoot | None:
        a = interval.low
        b = interval.high
        x1 = (a + b) / 2.0
        startTime = time.perf_counter()
        for i in range(self.rootFindingMaximumIterations):
            x1 = (a + b) / 2.0
            f1 = func(x1)
            if f1 > 0:
                b = x1
            else:
                a = x1
            if abs(b-a) < self.rootTolerance:
                endTime = time.perf_counter()
                return BisectionRoot(root=x1, iterations=i+1, error=abs(b-a), time=endTime - startTime)
        return None
    
    def findRoots(self, func: Callable[[float],float]) -> list[BisectionResult] | None:
        intervals = self.findIntervals(func)
        if not intervals:
            return None
        roots: list[BisectionResult] = []
        for interval in intervals:
            root = self._findRootInInterval(func, interval)
            if root is not None:
                roots.append(BisectionResult(interval=interval, root=root))
        return roots
    
    def printBisectionResults(self, roots: list[BisectionResult]):
        tableData = []
        for result in roots:
            tableData.append([f"[{result.interval.low}, {result.interval.high}]", result.root.root, result.root.iterations, result.root.error, result.root.time * 1000])
        print(tabulate(tableData, headers=["Interval", "Root (x)", "Iterations", "Error", "Time (milliseconds)"]))
    
    def printRoots(self,root: list[BisectionResult]):
        tableData = []
        for result in root:
            tableData.append([result.root.root, result.root.iterations, result.root.error, result.root.time * 1000])
        print(tabulate(tableData, headers=["Root (x)", "Iterations", "Error", "Time (milliseconds)"]))
        


# Test interval finding
if __name__ == "__main__":
    def testFunc(x: float) -> float:
        return x**2 - 5*x - 2
        # return 2*x - 2

    
    bisectionFinder = BisectionRootFinder(intervalStartPoint=-200.0, intervalStepSize=0.1, intervalMaxSteps=60000, rootTolerance=1e-7, rootFindingMaximumIterations=10000000)
    roots = bisectionFinder.findRoots(testFunc)
    if roots is None:
        print("No roots found")
        exit(1)
    
    bisectionFinder.printBisectionResults(roots)