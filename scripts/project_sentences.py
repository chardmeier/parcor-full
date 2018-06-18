import tokalign

import sys


def main():
    if len(sys.argv) != 3:
        print('Usage: %s txt1 txt2' % sys.argv[0])
        sys.exit(1)
    txt1 = sys.argv[1]
    txt2 = sys.argv[2]

    toks1 = []
    boundaries = []
    with open(txt1, 'r') as f:
        for line in f:
            toks1.extend(line.rstrip('\n').split(' '))
            boundaries.append(len(toks1))

    toks2 = []
    with open(txt2, 'r') as f:
        for line in f:
            toks2.extend(line.rstrip('\n').split(' '))

    alig = tokalign.align(toks1, toks2)
    mapping = {s: t for s, t in alig if s is not None and t is not None}
    out_boundaries = [0]
    for b in boundaries:
        for i in [-1, 0, -2, 1, -3, 2, -4, 3]:
            if b + i in mapping:
                if i not in [-1, 0]:
                    print('Offset mapping: %d' % i, file=sys.stderr)
                adjust = 1 if i < 0 else 0
                out_boundaries.append(mapping[b + i] + adjust)
                break

    if len(out_boundaries) != len(boundaries) + 1:
        print('Could not map all boundaries!', file=sys.stderr)

    for start, end in zip(out_boundaries, out_boundaries[1:]):
        print(' '.join(toks2[start:end]))


if __name__ == '__main__':
    main()

