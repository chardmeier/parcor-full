import bs4
import collections
import glob
import os
import spacy


def words_file(top_dir, docid):
    return '%s/Basedata/%s_words.xml' % (top_dir, docid)


def sentences_file(top_dir, docid):
    return '%s/Markables/%s_sentence_level.xml' % (top_dir, docid)


def coref_file(top_dir, docid):
    return '%s/Markables/%s_coref_level.xml' % (top_dir, docid)


def parse_span(span):
    if ',' in span:
        # discontinuous spans are not supported
        return None

    idx = [int(w.lstrip('word_')) - 1 for w in span.split('..')]
    if len(idx) == 1:
        return idx[0], idx[0] + 1
    else:
        return idx[0], idx[1] + 1


def make_span(from_idx, to_idx):
    if from_idx + 1 == to_idx:
        return 'word_%d' % (from_idx + 1)
    else:
        return 'word_%d..word_%d' % (from_idx + 1, to_idx)


def report(checks, span, problem):
    if span in checks:
        checks[span] += ' ' + problem
    else:
        checks[span] = problem


def named_entities_without_markable(nlp, checks, levels):
    markable_positions = set()
    for mrk in levels['coref'].find_all('markable'):
        for subspan in mrk['span'].split(','):
            markable_positions.update(pos for pos in range(*parse_span(subspan)))

    words = [str(w.string) for w in levels['basedata'].find_all('word')]
    doc = nlp.get_pipe('ner')(spacy.tokens.Doc(nlp.vocab, words=words))
    for ent in doc.ents:
        if ent.label_ in ['DATE', 'TIME', 'PERCENT', 'MONEY', 'QUANTITY', 'ORDINAL', 'CARDINAL']:
            continue

        found = False
        for i in range(ent.start, ent.end):
            if i in markable_positions:
                found = True
                break
        if not found:
            report(checks, make_span(ent.start, ent.end), 'NE:' + ent.label_)


def markables_across_sentence_boundaries(checks, levels):
    sent_ids = []
    for mrk in sorted(levels['sentences'].find_all('markable'), key=lambda m: int(m['orderid'])):
        span = parse_span(mrk['span'])
        sent_ids.extend(mrk['orderid'] for _ in range(*span))

    for mrk in levels['coref'].find_all('markable'):
        if mrk.get('mention', None) == 'clause':
            continue

        cross_sent = False
        for subspan in mrk['span'].split(','):
            start, end = parse_span(subspan)
            if sent_ids[start] != sent_ids[end - 1]:
                cross_sent = True
                break

        if cross_sent:
            report(checks, mrk['span'], 'cross-sentence')


def markables_with_identical_spans(checks, levels):
    spans = set()
    for mrk in levels['coref'].find_all('markable'):
        if mrk['span'] in spans:
            report(checks, mrk['span'], 'duplicate-markable')
        spans.add(mrk['span'])


def overlapping_markables_in_chain(checks, levels):
    chains = collections.defaultdict(list)
    for mrk in levels['coref'].find_all('markable'):
        chains[mrk['coref_class']].append(mrk)

    for ch in chains.values():
        covered_positions = set()
        for mrk in ch:
            mrk_positions = set()
            for subspan in mrk['span'].split(','):
                mrk_positions.update(i for i in range(*parse_span(subspan)))
            if mrk_positions & covered_positions:
                report(checks, mrk['span'], 'overlapping-in-chain')
            covered_positions.update(mrk_positions)


def unsure(checks, levels):
    for mrk in levels['coref'].find_all('markable'):
        for attr in ['type', 'nptype', 'vptype']:
            if attr in mrk and mrk[attr] == 'Not sure. HELP!':
                report(checks, mrk['span'], 'unsure')
                break


def position_audience(checks, levels):
    for mrk in levels['coref'].find_all('markable'):
        span = mrk['span']
        if ',' in span or '..' in span:
            continue
        if mrk.get('position') == 'none' and levels['basedata'].find(id=span).string in ['it', 'you']:
            report(checks, span, 'missing-position')
        if mrk.get('type') in ['speaker reference', 'addressee reference'] and \
                        mrk.get('audience', 'none') == 'none' and \
                        levels['basedata'].find(id=span).string in ['you', 'we', 'one']:
            report(checks, span, 'missing-audience')


def load_data(mmax_dir, mmax_id):
    levels = {}
    for fname, level in zip([fn(mmax_dir, mmax_id) for fn in [words_file, sentences_file, coref_file]],
                            ['basedata', 'sentences', 'coref']):
        with open(fname, 'r') as f:
            levels[level] = bs4.BeautifulSoup(f, 'xml')

    return levels


def create_checks_layer(mmax_dir, mmax_id, checks):
    fname = os.path.join(mmax_dir, 'Markables/%s_checks_level.xml' % mmax_id)
    with open(fname, 'w') as f:
        print('<?xml version="1.0" encoding="utf-8"?>', file=f)
        print('<!DOCTYPE markables SYSTEM "markables.dtd">', file=f)
        print('<markables xmlns="www.eml.org/NameSpaces/checks">', file=f)
        for i, (span, check) in enumerate(checks.items()):
            print('<markable mmax_level="checks" id="markable_%d" span="%s" check="%s" />' % (i, span, check), file=f)
        print('</markables>', file=f)


def main():
    data_root = '/Users/christianhardmeier/Documents/project/2017-parcor-full/parcor-full'

    nlp = spacy.load('en_core_web_sm')
    tests = [lambda c, l: named_entities_without_markable(nlp, c, l),
             markables_across_sentence_boundaries,
             markables_with_identical_spans,
             overlapping_markables_in_chain,
             unsure,
             position_audience]

    os.chdir(data_root)
    for fname in glob.iglob('*/EN/*.mmax'):
        mmax_dir = os.path.split(fname)[0]
        if not mmax_dir:
            mmax_dir = '.'

        mmax_id = os.path.splitext(os.path.basename(fname))[0]

        levels = load_data(mmax_dir, mmax_id)
        checks = {}
        for test in tests:
            test(checks, levels)

        counts = collections.Counter(checks.values())
        print(fname)
        for name, cnt in sorted(counts.items()):
            print(name, cnt)

        create_checks_layer(mmax_dir, mmax_id, checks)


if __name__ == '__main__':
    main()
