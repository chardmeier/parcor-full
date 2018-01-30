import glob
import numpy

from lxml import etree


def load_docs(pattern):
    tree = etree.Element('docs')
    for name in glob.iglob(pattern):
        with open(name, 'r') as f:
            doc = etree.parse(f)
            tree.append(doc.getroot())
    return tree


def mention_stats(en_tree, de_tree):
    ns = {'c': 'www.eml.org/NameSpaces/coref'}
    lstats = [[int(t.xpath('count(.//c:markable[@mention="%s"])' % mtype, namespaces=ns)) for t in [en_tree, de_tree]]
              for mtype in ['pronoun', 'np', 'vp', 'clause']]
    mat = numpy.zeros((5, 3), dtype=numpy.int32)
    mat[:4, :2] = numpy.array(lstats)
    mat[4, :] = numpy.sum(mat[:4, :], axis=0)
    mat[:, 2] = numpy.sum(mat[:, :2], axis=1)
    print('Mention statistics:')
    print(mat)


def chains_per_language(tree):
    ns = {'c': 'www.eml.org/NameSpaces/coref'}
    nchains = 0
    markables_in_chain = 0
    for doc in tree:
        chain_ids = [c for c in doc.xpath('.//c:markable/@coref_class', namespaces=ns) if c != 'empty']
        nchains += len(set(chain_ids))
        markables_in_chain += len(chain_ids)

    return nchains, markables_in_chain


def chain_stats(en_tree, de_tree):
    en_chains, en_mrk = chains_per_language(en_tree)
    de_chains, de_mrk = chains_per_language(de_tree)
    print('Chain statistics:')
    print(en_chains, de_chains, en_chains + de_chains)
    print(en_mrk / en_chains, de_mrk / de_chains, (en_mrk + de_mrk) / (en_chains + de_chains))


def main():
    en_tree = load_docs('*/EN/markables/*_coref_level.xml')
    de_tree = load_docs('*/DE/markables/*_coref_level.xml')
    mention_stats(en_tree, de_tree)
    chain_stats(en_tree, de_tree)


if __name__ == '__main__':
    main()