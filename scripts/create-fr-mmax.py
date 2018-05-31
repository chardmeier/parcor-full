import lxml.etree
import re
import spacy
import xml


def write_mmax(mmax_dir, mmax_id, sentences):
    write_basedata(mmax_dir, mmax_id, sentences)
    write_sentence_level(mmax_dir, mmax_id, sentences)


def write_basedata(mmax_dir, mmax_id, sentences):
    fname = mmax_dir + '/Basedata/%s_words.xml' % mmax_id
    with open(fname, 'w') as f:
        print('<?xml version="1.0" encoding="UTF-8"?>', file=f)
        print('<!DOCTYPE words SYSTEM "words.dtd">', file=f)
        print('<words>', file=f)
        widx = 1
        for snt in sentences:
            for w in snt:
                print('<word id="word_%d">%s</word>' % (widx, xml.sax.saxutils.escape(w)), file=f)
                widx += 1
        print('</words>', file=f)


def write_sentence_level(mmax_dir, mmax_id, sentences):
    fname = mmax_dir + '/Markables/%s_sentence_level.xml' % mmax_id
    with open(fname, 'w') as f:
        print('<?xml version="1.0" encoding="UTF-8" ?>', file=f)
        print('<!DOCTYPE markables SYSTEM "markables.dtd">', file=f)
        print('<markables xmlns="www.eml.org/NameSpaces/sentence">', file=f)
        widx = 1
        for i, snt in enumerate(sentences):
            if len(snt) == 1:
                span = 'word_%d' % widx
            else:
                span = 'word_%d..word_%d' % (widx, widx + len(snt) - 1)
            widx += len(snt)
            print('<markable mmax_level="sentence" orderid="%d" id="markable_%d" span="%s" />' % (i, i, span), file=f)
        print('</markables>', file=f)


def main():
    # talks = [779, 769, 792, 799, 767, 790, 785, 783, 824, 805, 837]
    # infile = 'corpus/TED/FR/Source/IWSLT13.TED.tst2010.en-fr.fr.xml'
    # mmax_dir = 'corpus/TED/FR'

    talks = [1756, 1819, 1825, 1894, None, 1938, 1950, 1953, None, 2043, 205, 2053]
    infile = 'corpus/DiscoMT/FR/Source/DiscoMT2015.test.raw.fr.xml'
    mmax_dir = 'corpus/DiscoMT/FR'

    with open(infile, 'r') as f:
        inxml = lxml.etree.parse(f)

    nlp = spacy.load('fr')
    spaces = re.compile(r'\s+')

    for i, talkid in enumerate(talks):
        if talkid is None:
            continue

        sentences = []
        for seg in inxml.xpath('//doc[@docid="%s"]/seg' % talkid):
            ntext = re.sub(spaces, ' ', seg.text.strip())
            sentences.append([t.text for t in nlp(ntext)])

        write_mmax(mmax_dir, '%03d_%d' % (i, talkid), sentences)


if __name__ == '__main__':
    main()