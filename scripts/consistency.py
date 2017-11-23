import bs4
import glob
import os
import sys


def markables_without_chain(chains):
    mrks = [m for m in chains.get('empty', [])
            if m.get('type') not in ('speaker reference', 'addressee reference',
                                     'pleonastic', 'extratextual reference', 'pronoun')]
    report('markable-without-chain', mrks)


def singleton_chains(chains):
    singletons = [c for chain_id, c in chains.items() if len(c) == 1 and chain_id != 'empty']
    mrks = [m[0] for m in singletons if m[0]['split'] != 'no explicit antecedent']
    report('singleton-chain', mrks)


def antecedent_not_first(chains):
    mrks = []
    for c in chains.values():
        if c[0].get('type') != 'cataphoric':
            mrks.extend(m for m in c[1:] if is_antecedent(m))
    report('antecedent-not-first', mrks)


def chains_without_antecedent(chains):
    mrks = []
    for k, c in chains.items():
        if k == 'empty':
            continue
        if not any(is_antecedent(m) for m in c):
            mrks.extend(c)
    report('chain-without-antecedent', mrks)


def antecedent_consistency(chains):
    mrks = []
    for k, c in chains.items():
        if k == 'empty':
            continue
        split = {m['split'] for m in c if 'split' in m}
        antetype = {m['antetype'] for m in c if 'antetype' in m}
        if len(split) > 1 or len(antetype) > 1:
            mrks.extend(c)
    report('antecedent-consistency', mrks)


def split_discontinuous(chains):
    mrks = []
    for c in chains.values():
        split = {m.get('split') for m in c}
        if 'split reference' in split:
            ant = [m for m in c if is_antecedent(m)]
            if ant and ',' not in ant[0]['span']:
                mrks.append(ant[0])
    report('split-discontinuous', mrks)


def report(check, mrks):
    for m in mrks:
        existing = m.get('check')
        if existing:
            m['check'] = existing + ' ' + check
        else:
            m['check'] = check


def is_antecedent(markable):
    cands = [markable.get(t) for t in ['type', 'nptype', 'vptype', 'clausetype']]
    return 'antecedent' in cands


def span_key(markable):
    spans = markable['span'].split(',')
    key = tuple(int(w.lstrip('word_')) for w in spans[0].split('..'))
    return key


def make_chains(soup):
    chains = {}
    for mrk in soup.find_all('markable'):
        ch = mrk['coref_class']
        if ch not in chains:
            chains[ch] = [mrk]
        else:
            chains[ch].append(mrk)
    for chain in chains.values():
        chain.sort(key=span_key)
    return chains


def make_checks_layer(soup):
    soup.find('markables')['xmlns'] = 'www.eml.org/NameSpaces/checks'
    for mrk in soup.find_all('markable'):
        if 'check' not in mrk.attrs.keys():
            mrk.extract()
            continue

        extra_tags = [t for t in mrk.attrs.keys() if t not in {'id', 'span', 'check'}]
        for t in extra_tags:
            del mrk[t]
        mrk['mmax_level'] = 'checks'


def main():
    if len(sys.argv) != 2:
        print('Usage: consistency.py top-dir', file=sys.stderr)
        sys.exit(1)

    top_dir = sys.argv[1]

    tests = [markables_without_chain,
             singleton_chains,
             antecedent_not_first,
             chains_without_antecedent,
             antecedent_consistency,
             split_discontinuous]

    os.chdir(top_dir)
    for fname in glob.iglob('**/*_coref_level.xml', recursive=True):
        with open(fname, 'r') as f:
            print('Checking ' + fname)
            soup = bs4.BeautifulSoup(f, 'xml')
            chains = make_chains(soup)
            for test in tests:
                test(chains)
            make_checks_layer(soup)

            outname = fname.rstrip('_coref_level.xml') + '_checks_level.xml'
            with open(outname, 'w') as outf:
                outf.write(soup.prettify())


if __name__ == '__main__':
    main()