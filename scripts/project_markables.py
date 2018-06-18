import collections
import re
import sys

from lxml import etree


def get_start_idx(span):
    m = re.match(r'word_([0-9]+)', span)
    return int(m[1])


def transform_span(span, alignment):
    outspan = []
    for part in span.split(','):
        ep = part.split('..')
        start = int(ep[0][5:])
        if start not in alignment:
            return None
        o = 'word_%d' % alignment[start].min

        if len(ep) == 2:
            end = int(ep[1][5:])
            if end not in alignment:
                return None
            o += '..word_%d' % alignment[end].max

        outspan.append(o)
    return ','.join(outspan)


class MinMax:
    def __init__(self):
        self.min = None
        self.max = None

    def offer(self, val):
        if self.min is None or val < self.min:
            self.min = val

        if self.max is None or val > self.max:
            self.max = val

    def __bool__(self):
        return self.min is not None

    def __repr__(self):
        return 'MinMax(%d, %d)' % (self.min, self.max)


def main():
    sentence_markable = '{www.eml.org/NameSpaces/sentence}markable'
    coref_markable = '{www.eml.org/NameSpaces/coref}markable'

    if len(sys.argv) != 5:
        print('Usage: %s coref-level.xml in-sentence-level.xml out-sentence-level.xml alignments' % sys.argv[0], file=sys.stderr)
        sys.exit(1)

    coref_file = sys.argv[1]
    in_sentence_file = sys.argv[2]
    out_sentence_file = sys.argv[3]
    aligfile = sys.argv[4]

    with open(coref_file, 'r') as f:
        coref_xml = etree.parse(f)

    with open(in_sentence_file, 'r') as f:
        if in_sentence_file.endswith('.xml'):
            in_sentence_xml = etree.parse(f)
            in_sentence_start = [get_start_idx(insnt.get('span')) for insnt in in_sentence_xml.iter(sentence_markable)]
        else:
            in_sentence_start = []
            i = 1
            for line in f:
                in_sentence_start.append(i)
                i += len(line.split(' '))

    with open(out_sentence_file, 'r') as f:
        out_sentence_xml = etree.parse(f)

    alignment = collections.defaultdict(MinMax)
    with open(aligfile, 'r') as f:
        ap_pattern = re.compile(r'([0-9]+)-([0-9]+)')
        for aligline, instart, outsnt in zip(f, in_sentence_start, out_sentence_xml.iter(sentence_markable)):
            outstart = get_start_idx(outsnt.get('span'))

            for ap in re.finditer(ap_pattern, aligline):
                s = int(ap[1])
                t = int(ap[2])
                alignment[instart + s].offer(outstart + t)

    for mrk in coref_xml.iter(coref_markable):
        outspan = transform_span(mrk.get('span'), alignment)
        if outspan is None:
            mrk.getparent().remove(mrk)
            continue

        for k in mrk.attrib.keys():
            if k not in ['id', 'span', 'mmax_level']:
                del mrk.attrib[k]

        mrk.set('mention', 'none')
        mrk.set('span', outspan)

    print('<?xml version="1.0" encoding="utf-8"?>')
    sys.stdout.write(etree.tostring(coref_xml, pretty_print=True).decode('utf8'))


if __name__ == '__main__':
    main()

