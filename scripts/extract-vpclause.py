import os
import re
import sys

from lxml import etree


# I would like to collect following info:
# - for every sentences with an anaphora whose antecedents is a VP or a clause
# 	- the sentence
# 	- the anaphor
# 	- few preceding sentences
# 	- the antecedent


def words_file(top_dir, docid):
    return '%s/Basedata/%s_words.xml' % (top_dir, docid)


def sentences_file(top_dir, docid):
    return '%s/markables/%s_sentence_level.xml' % (top_dir, docid)


def coref_file(top_dir, docid):
    return '%s/markables/%s_coref_level.xml' % (top_dir, docid)


def parse_span(span):
    if ',' in span:
        # discontinuous spans are not supported by this function
        return None

    idx = [int(w.lstrip('word_')) - 1 for w in span.split('..')]
    if len(idx) == 1:
        return idx[0], idx[0] + 1
    else:
        return idx[0], idx[1] + 1


def find_sentence(sentences_dict, markable):
    m = re.match(r'word_([0-9]+)', markable.get('span'))
    return sentences_dict[int(m[1])]


def print_markable(words_list, markable):
    subspans = []
    for s in markable.get('span').split(','):
        start, end = parse_span(s)
        subspans.append(words_list[start:end])
    print(subspans)


def main():
    if len(sys.argv) != 2:
        print('Usage: %s input.mmax' % sys.argv[0], file=sys.stderr)
        sys.exit(1)

    in_mmax = sys.argv[1]

    mmax_dir, mmax_file = os.path.split(in_mmax)
    mmax_id = os.path.splitext(mmax_file)[0]

    if not mmax_dir:
        mmax_dir = '.'

    with open(sentences_file(mmax_dir, mmax_id), 'r') as f:
        sentences_xml = etree.parse(f)

    with open(coref_file(mmax_dir, mmax_id), 'r') as f:
        coref_xml = etree.parse(f)

    with open(words_file(mmax_dir, mmax_id), 'r') as f:
        words_xml = etree.parse(f)

    # Store words in a list
    words_list = [w.text for w in words_xml.iter('word')]

    # The markable level files have annoying namespaces
    namespaces = {'s': 'www.eml.org/NameSpaces/sentence',
                  'c': 'www.eml.org/NameSpaces/coref'}

    # Create a dictionary that gives us the sentence markable for each word
    sentences_dict = {}
    for mrk in sentences_xml.xpath('s:markable', namespaces=namespaces):
        start, end = parse_span(mrk.get('span'))
        for i in range(start, end):
            sentences_dict[i] = mrk

    # Look for mentions of type VP or clause.
    for antecedent in coref_xml.xpath('c:markable[@mention="vp" or @mention="clause"]', namespaces=namespaces):
        print('Antecedent:')
        print_markable(words_list, antecedent)

        coref_class = antecedent.get('coref_class')
        for anaphor in coref_xml.xpath('c:markable[@coref_class="%s"]' % coref_class, namespaces=namespaces):
            if anaphor == antecedent:
                continue

            print('\nAnaphor:')
            print_markable(words_list, anaphor)

            snt = find_sentence(sentences_dict, anaphor)
            # Show current and two previous sentences
            for i in range(3):
                print('Sentence at offset %d:' % -i, end=' ')
                print_markable(words_list, snt)
                snt = snt.getprevious()
                if snt is None:
                    break

        print('\n\n-------------------------------------------\n\n')


if __name__ == '__main__':
    main()

