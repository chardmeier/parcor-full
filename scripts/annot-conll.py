import bs4
import mmax
import os
import re
import sys


def lookup_chain(directory, coref_class):
    if coref_class in directory:
        return directory[coref_class]
    else:
        chain_id = directory['__next__']
        directory[coref_class] = chain_id
        directory['__next__'] += 1
        return chain_id


def append(boundaries, idx, tag):
    if idx in boundaries:
        boundaries[idx].append(tag)
    else:
        boundaries[idx] = [tag]


def get_coref_chain_boundaries(mmax_dir, mmax_id):
    with open(mmax.coref_file(mmax_dir, mmax_id), 'r') as f:
        soup = bs4.BeautifulSoup(f, 'xml')

    directory = {'__next__': 1}
    boundaries = {}
    clause_or_vp = set()
    for mrk in soup.find_all('markable'):
        if not mrk.has_attr('coref_class') or not mrk['coref_class'] or mrk['coref_class'] == 'empty':
            continue

        chain_idx = lookup_chain(directory, mrk['coref_class'])

        if mrk['mention'] in ('clause', 'vp'):
            clause_or_vp.add(chain_idx)

        for s in mrk['span'].split(','):
            start, end = mmax.parse_span(s)
            if start == end - 1:
                append(boundaries, start, ('(%d)', chain_idx))
            else:
                append(boundaries, start, ('(%d', chain_idx))
                append(boundaries, end - 1, ('%d)', chain_idx))

    str_boundaries = {}
    for pos, chains in boundaries.items():
        if idx not in clause_or_vp:
            str_boundaries[pos] = [fmt % idx for fmt, idx in chains]

    return str_boundaries


def annotate_conll(in_conll, boundaries):
    skippable = re.compile(r'^(\s*$|#)')
    with open(in_conll, 'r') as f:
        widx = 0
        for line in f:
            if re.match(skippable, line):
                print(line)
                continue
            else:
                fields = line.rstrip('\n').split()
                if len(fields) < 12:
                    print(in_conll + ': Line too short: ' + line, file=sys.stderr)
                    sys.exit(1)

                if widx in boundaries:
                    fields.append('|'.join(boundaries[widx]))
                else:
                    fields.append('-')

                print('\t'.join(fields))
                widx += 1


def main():
    if len(sys.argv) != 3:
        print('Usage: %s in.mmax in.conll' % sys.argv[0])
        sys.exit(1)

    in_mmax = sys.argv[1]
    in_conll = sys.argv[2]

    mmax_dir, mmax_file = os.path.split(in_mmax)
    mmax_id = os.path.splitext(mmax_file)[0]

    boundaries = get_coref_chain_boundaries(mmax_dir, mmax_id)
    annotate_conll(in_conll, boundaries)


if __name__ == '__main__':
    main()
