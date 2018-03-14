import bs4


def words_file(top_dir, docid):
    return '%s/Basedata/%s_words.xml' % (top_dir, docid)


def sentences_file(top_dir, docid):
    return '%s/markables/%s_sentence_level.xml' % (top_dir, docid)


def coref_file(top_dir, docid):
    return '%s/markables/%s_coref_level.xml' % (top_dir, docid)


def parse_span(span):
    if ',' in span:
        # discontinuous spans are not supported
        return None

    idx = [int(w.lstrip('word_')) - 1 for w in span.split('..')]
    if len(idx) == 1:
        return idx[0], idx[0] + 1
    else:
        return idx[0], idx[1] + 1


def get_sentences_from_mmax(top_dir, docid):
    with open(words_file(top_dir, docid), 'r') as f:
        w_soup = bs4.BeautifulSoup(f, 'xml')
    with open(sentences_file(top_dir, docid), 'r') as f:
        s_soup = bs4.BeautifulSoup(f, 'xml')

    words = [(w['id'], w.string) for w in w_soup.find_all('word')]
    spans = [parse_span(m['span']) for m in s_soup.find_all({'markable'})]

    #for i, (w1, w2) in enumerate(zip(words, words[1:])):
    #    if w1.endswith('n') and w2 == "'t":
    #        words[i] = words[i][:-1]
    #        words[i + 1] = "n't"

    sentences = [words[slice(*sl)] for sl in spans]

    return sentences
