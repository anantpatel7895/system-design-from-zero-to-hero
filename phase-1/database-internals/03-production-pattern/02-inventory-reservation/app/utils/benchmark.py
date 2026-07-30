from statistics import mean, median


class Benchmark:

    def __init__(self, results):

        self.results = results

        self.latencies = sorted(
            r.elapsed_ms
            for r in results
        )

    def average(self):

        return mean(self.latencies)

    def minimum(self):

        return min(self.latencies)

    def maximum(self):

        return max(self.latencies)

    def median(self):

        return median(self.latencies)

    def percentile(self, p):

        if not self.latencies:
            return 0

        index = int(len(self.latencies) * p / 100)

        index = min(
            index,
            len(self.latencies) - 1,
        )

        return self.latencies[index]