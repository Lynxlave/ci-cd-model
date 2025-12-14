import math


class DummyModel:
    def __init__(self, weights, bias=0.0):
        self.weights = list(weights)
        self.bias = bias

    def _score(self, rows):
        scores = []
        for row in rows:
            s = 0.0
            for f, w in zip(row, self.weights):
                s += f * w
            s += self.bias
            scores.append(s)
        return scores

    def predict_proba(self, rows):
        scores = self._score(rows)
        probs = []
        for s in scores:
            p1 = 1 / (1 + math.exp(-s))
            probs.append([1 - p1, p1])
        return probs

    def predict(self, rows):
        labels = []
        for p0, p1 in self.predict_proba(rows):
            labels.append(1 if p1 >= 0.5 else 0)
        return labels

