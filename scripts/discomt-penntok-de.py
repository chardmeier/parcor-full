# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import bs4
import os
import xml
import re
import spacy
import sys

import mmax
import tokalign


def get_penntok_from_txt(infile):
    nlp = spacy.load('de')
    with open(infile, 'r') as f:
        # The regex substitution is because some files have double spaces.
        sentences = [[t.text for t in nlp(re.sub(r'\s+', ' ', line.rstrip('\n')))] for line in f]

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
            if len(snt) == 0:
                continue
            elif len(snt) == 1:
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
        print('Usage: %s outdir input.mmax input.txt' % sys.argv[0], file=sys.stderr)
        sys.exit(1)

    out_dir = sys.argv[1]
    in_mmax = sys.argv[2]
    in_txt = sys.argv[3]

    mmax_dir, mmax_file = os.path.split(in_mmax)
    mmax_id = os.path.splitext(mmax_file)[0]

    mmax_sent = mmax.get_sentences_from_mmax(mmax_dir, mmax_id)
    penn_sent = get_penntok_from_txt(in_txt)

    for d in ['Basedata', 'Markables']:
        if not os.path.exists(out_dir + '/' + d):
            os.mkdir(out_dir + '/' + d)

    mmax_start = 0
    penn_start = 0
    translated = {}

    for m, p in zip(mmax_sent, penn_sent):
        alig = tokalign.align([t[1] for t in m], p)
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

