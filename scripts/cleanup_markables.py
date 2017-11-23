import bs4
import datetime
import glob
import os
import sys


def cleanup_file(fname, bakname):
    n_removed = 0

    os.rename(fname, bakname)
    with open(bakname, 'r') as f:
        soup = bs4.BeautifulSoup(f, 'xml')

        for mrk in soup.find_all('markable'):
            if 'not sure. help!' in mrk.attrs.values() and mrk.get('coref_class') == 'empty':
                print(mrk.extract())
                n_removed += 1

        with open(fname, 'w') as outf:
            outf.write(soup.prettify())

    return n_removed


def main():
    if len(sys.argv) != 2:
        print('Usage: cleanup_markables.py top-dir', file=sys.stderr)
        sys.exit(1)

    top_dir = sys.argv[1]

    backup_ext = datetime.date.today().strftime('%Y%m%d')

    os.chdir(top_dir)
    for fname in glob.iglob('**/*_coref_level.xml', recursive=True):
        bakname = fname + '.' + backup_ext
        if os.path.exists(bakname):
            print('%s: Backup file already exists. Skipping.' % fname, file=sys.stderr)
        else:
            nremoved = cleanup_file(fname, bakname)
            print('%s: Removed %d markables.' % (fname, nremoved), file=sys.stderr)


if __name__ == '__main__':
    main()