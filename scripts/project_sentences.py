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
        if b in mapping:
            out_boundaries.append(mapping[b])
        else:
            for i in range(1, 20):
                if b - i in mapping:
                    print('Offset mapping: %d' % (-i), file=sys.stderr)
                    out_boundaries.append(mapping[b - i] + 1)
                    break
                elif b + i in mapping:
                    print('Offset mapping: %d' % i, file=sys.stderr)
                    out_boundaries.append(mapping[b + i])
                    break

    if len(out_boundaries) != len(boundaries) + 1:
        print('Could not map all boundaries!', file=sys.stderr)

    for start, end in zip(out_boundaries, out_boundaries[1:]):
        print(' '.join(toks2[start:end]))


if __name__ == '__main__':
    main()

