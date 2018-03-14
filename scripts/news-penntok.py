# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import bs4
import nltk
import os
import xml
import sys

import mmax
import tokalign


class AlignApostropheS:
    def __init__(self, cost):
        self.cost = cost

    def apply(self, hypo, txt1, txt2):
        if hypo.pos1 < -1 and hypo.pos2 < 0:
            if txt1[hypo.pos1 + 1] == "'s" and txt1[hypo.pos1] + "'s" == txt2[hypo.pos2]:
                ext = [(hypo.pos1 + len(txt1), hypo.pos2 + len(txt2))]
                return [tokalign.Hypothesis(hypo.cost + self.cost, hypo.pos1 + 2, hypo.pos2 + 1, ext, hypo)]

        if hypo.pos2 < -1 and hypo.pos1 < 0:
            if txt2[hypo.pos2 + 1] == "'s" and txt1[hypo.pos1] == txt2[hypo.pos2] + "'s":
                ext = [(hypo.pos1 + len(txt1), hypo.pos2 + len(txt2))]
                return [tokalign.Hypothesis(hypo.cost + self.cost, hypo.pos1 + 1, hypo.pos2 + 2, ext, hypo)]

        return []


def get_penntok_from_wmt_xml(infile):
    with open(infile, 'r') as f:
        soup = bs4.BeautifulSoup(f, 'xml')

    sentences = []
    for seg in soup.find_all('seg'):
        sentences.append(nltk.tokenize.word_tokenize(seg.string))

    return sentences


def write_basedata(filename, sentences):
    with open(filename, 'w') as f:
        print('<?xml version="1.0" encoding="UTF-8"?>', file=f)
        print('<!DOCTYPE words SYSTEM "words.dtd">', file=f)
        print('<words>', file=f)
        word_idx = 1
        for snt in sentences:
            for w in snt:
                print('<word id="word_%d">%s</word>' % (word_idx, xml.sax.saxutils.escape(w)), file=f)
                word_idx += 1
        print('</words>', file=f)


def write_sentences(filename, sentences):
    with open(filename, 'w') as f:
        print('<?xml version="1.0" encoding="UTF-8" ?>', file=f)
        print('<!DOCTYPE markables SYSTEM "markables.dtd">', file=f)
        print('<markables xmlns="www.eml.org/NameSpaces/sentence">', file=f)
        snt_start = 1
        for i, snt in enumerate(sentences):
            if len(snt) == 1:
                span = 'word_%d' % snt_start
            else:
                span = 'word_%d..word_%d' % (snt_start, snt_start + len(snt) - 1)
            snt_start += len(snt)
            print('<markable mmax_level="sentence" orderid="%d" id="markable_%d" span="%s" />' % (i, i, span),
                    file=f)
        print('</markables>', file=f)


def translate_coref(infile, outfile, translated):
    with open(infile, 'r') as f:
        soup = bs4.BeautifulSoup(f, 'xml')

    total = 0
    skipped = 0
    for mrk in soup.find_all('markable'):
        total += 1

        span_parts = []
        for in_span in mrk['span'].split(','):
            from_idx, to_idx = mmax.parse_span(in_span)
            if from_idx not in translated:
                print('Unaligned start word: ' + str(mrk), file=sys.stderr)
                skipped += 1
                continue

            if from_idx == to_idx:
                span = 'word_%d' % (translated[from_idx] + 1)
            elif to_idx - 1 not in translated:
                print('Unaligned end word: ' + str(mrk), file=sys.stderr)
                skipped += 1
                continue
            else:
                span = 'word_%d..word_%d' % tuple(translated[i] + 1 for i in [from_idx, to_idx - 1])

            span_parts.append(span)

        mrk['span'] = ','.join(span_parts)

    print('Skipped %d out of %d markables.' % (skipped, total), file=sys.stderr)
    with open(outfile, 'w') as f:
        print(soup.prettify(), file=f)


def main():
    if len(sys.argv) != 4:
        print('Usage: %s outdir input.mmax input.xml' % sys.argv[0], file=sys.stderr)
        sys.exit(1)

    out_dir = sys.argv[1]
    in_mmax = sys.argv[2]
    in_wmt = sys.argv[3]

    mmax_dir, mmax_file = os.path.split(in_mmax)
    mmax_id = os.path.splitext(mmax_file)[0]

    mmax_sent = mmax.get_sentences_from_mmax(mmax_dir, mmax_id)
    penn_sent = get_penntok_from_wmt_xml(in_wmt)

    for d in ['Basedata', 'Markables']:
        if not os.path.exists(out_dir + '/' + d):
            os.mkdir(out_dir + '/' + d)

    mmax_start = 0
    penn_start = 0
    translated = {}

    operations = [tokalign.LinkSame(0.0), AlignApostropheS(0.0),
            tokalign.LinkDifferent(1.0), tokalign.Skip1(2.0), tokalign.Skip2(2.0)]

    for m, p in zip(mmax_sent, penn_sent):
        alig = tokalign.align([t[1] for t in m], p, operations=operations)
        for m_idx, p_idx in alig:
            if m_idx is not None and p_idx is not None:
                translated[mmax_start + m_idx] = penn_start + p_idx
        mmax_start += len(m)
        penn_start += len(p)

    write_basedata(mmax.words_file(out_dir, mmax_id), penn_sent)
    write_sentences(mmax.sentences_file(out_dir, mmax_id), penn_sent)
    translate_coref(mmax.coref_file(mmax_dir, mmax_id), mmax.coref_file(out_dir, mmax_id), translated)


if __name__ == '__main__':
    main()

