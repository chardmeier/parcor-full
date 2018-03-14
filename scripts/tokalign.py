# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import heapq
import logging
import sys

from functools import total_ordering


class Resplit:
    def __init__(self, cost_fn, max_tokens):
        self.cost_fn = cost_fn
        self.max_tokens = max_tokens

    def apply(self, hypo, txt1, txt2):
        new_hypos = []
        for n in range(2, 1 + min(self.max_tokens, -hypo.pos1, -hypo.pos2)):
            t1 = ''.join(txt1[hypo.pos1:hypo.pos1 + n])
            t2 = ''.join(txt2[hypo.pos2:hypo.pos2 + n])
            if t1 == t2:
                ext = [(hypo.pos1 + i, hypo.pos2 + i) for i in range(n)]
                new_hypos.append(Hypothesis(hypo.cost + self.cost_fn(n), hypo.pos1 + n, hypo.pos2 + n, ext, hypo))

        return new_hypos


class LinkBlock:
    def __init__(self, cost_fn, max_tokens):
        self.cost_fn = cost_fn
        self.max_tokens = max_tokens

    def apply(self, hypo, txt1, txt2):
        new_hypos = []
        for n1 in range(1, 1 + min(self.max_tokens, -hypo.pos1)):
            t1 = ''.join(txt1[hypo.pos1:hypo.pos1 + n1])
            for n2 in range(1, 1 + min(self.max_tokens, -hypo.pos2)):
                t2 = ''.join(txt2[hypo.pos2:hypo.pos2 + n2])
                if t1 == t2:
                    ext = [(hypo.pos1 + i, hypo.pos2 + j) for i in range(n1) for j in range(n2)]
                    new_hypos.append(Hypothesis(hypo.cost + self.cost_fn(n1, n2), hypo.pos1 + n1, hypo.pos2 + n2, ext, hypo))

        return new_hypos


class LinkSame:
    def __init__(self, cost):
        self.cost = cost

    def apply(self, hypo, txt1, txt2):
        if hypo.pos1 >= 0 or hypo.pos2 >= 0:
            return []

        if txt1[hypo.pos1] == txt2[hypo.pos2]:
            ext = [(hypo.pos1 + len(txt1), hypo.pos2 + len(txt2))]
            return [Hypothesis(hypo.cost + self.cost, hypo.pos1 + 1, hypo.pos2 + 1, ext, hypo)]
        else:
            return []


class LinkDifferent:
    def __init__(self, cost):
        self.cost = cost

    def apply(self, hypo, txt1, txt2):
        if hypo.pos1 >= 0 or hypo.pos2 >= 0:
            return []

        if txt1[hypo.pos1] != txt2[hypo.pos2]:
            ext = [(hypo.pos1 + len(txt1), hypo.pos2 + len(txt2))]
            return [Hypothesis(hypo.cost + self.cost, hypo.pos1 + 1, hypo.pos2 + 1, ext, hypo)]
        else:
            return []
        

class Skip1:
    def __init__(self, cost):
        self.cost = cost

    def apply(self, hypo, txt1, txt2):
        if hypo.pos1 >= 0:
            return []

        ext = [(hypo.pos1 + len(txt1), None)]
        return [Hypothesis(hypo.cost + self.cost, hypo.pos1 + 1, hypo.pos2, ext, hypo)]


class Skip2:
    def __init__(self, cost):
        self.cost = cost

    def apply(self, hypo, txt1, txt2):
        if hypo.pos2 >= 0:
            return []

        ext = [(None, hypo.pos2 + len(txt2))]
        return [Hypothesis(hypo.cost + self.cost, hypo.pos1, hypo.pos2 + 1, ext, hypo)]


@total_ordering
class Hypothesis:
    def __init__(self, cost, pos1, pos2, alignment, prev, g_skip=None):
        self.cost = cost
        self.pos1 = pos1
        self.pos2 = pos2
        self.alignment = alignment
        self.prev = prev
        self.discarded = False

        if g_skip:
            self.g_skip = g_skip
        elif prev:
            self.g_skip = prev.g_skip
        else:
            self.g_skip = 2.0

        self.total_cost = self.cost + self._future_cost(pos1, pos2)

    def recombination_key(self):
        return (self.pos1, self.pos2, tuple(self.alignment))

    def _future_cost(self, pos1, pos2):
        return self.g_skip * abs(pos1 - pos2)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "Hypothesis(%.2f, %.2f, %d, %d, %s)" % (self.total_cost, self.cost, self.pos1, self.pos2, self.alignment)

    def __eq__(self, other):
        return self.total_cost == other.total_cost

    def __lt__(self, other):
        return self.total_cost < other.total_cost
    

def align(txt1, txt2, operations=None):
    if operations is None:
        operations = [LinkSame(0.0), LinkDifferent(1.0), Skip1(2.0), Skip2(2.0)]

    queue = [Hypothesis(0.0, -len(txt1), -len(txt2), [], None, g_skip=2.0)]
    recomb = {}

    while True:
        hypo = heapq.heappop(queue)
        if hypo.discarded:
            continue

        logging.debug("Expanding:" + str(hypo))

        if hypo.pos1 == 0 and hypo.pos2 == 0:
            break

        for op in operations:
            new_hypos = op.apply(hypo, txt1, txt2)
            for updated in new_hypos:
                existing = recomb.get(updated.recombination_key())
                if existing is None:
                    logging.debug("Adding: " + str(updated))
                    heapq.heappush(queue, updated)
                    recomb[updated.recombination_key()] = updated
                elif existing.total_cost > updated.total_cost:
                    logging.debug("Recombining: " + str(updated))
                    existing.discarded = True
                    heapq.heappush(queue, updated)
                    recomb[updated.recombination_key()] = updated
                else:
                    logging.debug("Discarding: " + str(updated))

    alignments = []
    while hypo is not None:
        alignments.extend(reversed(hypo.alignment))
        hypo = hypo.prev

    alignments.reverse()
    return alignments


def main():
    logging.basicConfig(format='%(asctime)s %(message)s')

    if len(sys.argv) != 3:
        print("Usage: tokalign.py file1 file2", file=sys.stderr)
        sys.exit(1)

    filename1 = sys.argv[1]
    filename2 = sys.argv[2]

    with open(filename1, 'r') as f:
        txt1 = f.read().split()

    with open(filename2, 'r') as f:
        txt2 = f.read().split()

    print(align(txt1, txt2))


if __name__ == "__main__":
    main()
