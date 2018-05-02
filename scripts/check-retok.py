import bs4
import glob
import os
import sys

import mmax


def compare_mmax(dir1, dir2, mmax_dir, mmax_id):
    mmax_dir1 = os.path.join(dir1, mmax_dir)
    mmax_dir2 = os.path.join(dir2, mmax_dir)

    with open(mmax.words_file(mmax_dir1, mmax_id), 'r') as f:
        words1 = [w.string for w in bs4.BeautifulSoup(f, 'xml').find_all('word')]
    with open(mmax.words_file(mmax_dir2, mmax_id), 'r') as f:
        words2 = [w.string for w in bs4.BeautifulSoup(f, 'xml').find_all('word')]

    to_check = []

    for level in ['sentence', 'coref']:
        fname1 = '%s/Markables/%s_%s_level.xml' % (mmax_dir1, mmax_id, level)
        fname2 = '%s/Markables/%s_%s_level.xml' % (mmax_dir2, mmax_id, level)

        with open(fname1, 'r') as f:
            markables1 = [m for m in bs4.BeautifulSoup(f, 'xml').find_all('markable')]
        with open(fname2, 'r') as f:
            markables2 = [m for m in bs4.BeautifulSoup(f, 'xml').find_all('markable')]

        def sort_key(mrk):
            return [mmax.parse_span(m) for m in mrk['span'].split(',')]

        markables1.sort(key=sort_key)
        markables2.sort(key=sort_key)

        if len(markables1) != len(markables2):
            print('%s/%s: Number of markables does not match (%d != %d)' %
                  (mmax_dir, mmax_id, len(markables1), len(markables2)), file=sys.stderr)
            continue

        for mrk1, mrk2 in zip(markables1, markables2):
            spans1 = mrk1['span'].split(',')
            spans2 = mrk2['span'].split(',')
            if len(spans1) != len(spans2):
                print('%s/%s: Number of span components does not match (%s / %s)' %
                      (mmax_dir, mmax_id, mrk1['span'], mrk2['span']), file=sys.stderr)
                continue

            for sp1, sp2 in zip(spans1, spans2):
                s1, e1 = mmax.parse_span(sp1)
                s2, e2 = mmax.parse_span(sp2)
                txt1 = ''.join(words1[s1:e1])
                txt2 = ''.join(words2[s2:e2])

                # Quotes are changed by the tokeniser
                txt1 = txt1.replace("``", '"').replace("''", '"')
                txt2 = txt2.replace("``", '"').replace("''", '"')

                if txt1 != txt2:
                    to_check.append((level, sp2))

    if to_check:
        print(mmax_dir, mmax_id, file=sys.stderr)
        create_checks_level(mmax_dir2, mmax_id, to_check)


def create_checks_level(mmax_dir, mmax_id, to_check):
    fname = os.path.join(mmax_dir, 'Markables/%s_checks_level.xml' % mmax_id)
    with open(fname, 'w') as f:
        print('<?xml version="1.0" encoding="utf-8"?>', file=f)
        print('<!DOCTYPE markables SYSTEM "markables.dtd">', file=f)
        print('<markables xmlns="www.eml.org/NameSpaces/checks">', file=f)
        for i, (level, span) in enumerate(to_check):
            print('<markable mmax_level="checks" id="markable_%d" span="%s" check="%s" />' % (i, span, level), file=f)
        print('</markables>', file=f)


def main():
    if len(sys.argv) != 3:
        print('Usage: %s dir1 dir2' % sys.argv[0])
        sys.exit(1)

    dir1 = sys.argv[1]
    dir2 = sys.argv[2]

    startdir = os.open('.', os.O_RDONLY)
    os.chdir(dir1)
    mmax_files = glob.glob('**/*.mmax', recursive=True)
    os.fchdir(startdir)

    for fname in sorted(mmax_files):
        mmax_dir, mmax_file = os.path.split(fname)
        mmax_id = os.path.splitext(mmax_file)[0]
        compare_mmax(dir1, dir2, mmax_dir, mmax_id)


if __name__ == '__main__':
    main()
