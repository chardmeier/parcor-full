import glob
import json
import os
import sys

import mmax


def main():
    if len(sys.argv) < 2:
        print('Usage: %s mmaxdir ...' % sys.argv[0], file=sys.stderr)
        sys.exit(1)

    for mmax_dir in sys.argv[1:]:
        for in_mmax in glob.iglob(os.path.join(mmax_dir, '*.mmax')):
            mmax_file = os.path.basename(in_mmax)
            mmax_id = os.path.splitext(mmax_file)[0]

            snt = mmax.get_sentences_from_mmax(mmax_dir, mmax_id)

            words = [[w[1] for w in s] for s in snt]
            speakers = [['' for _ in s] for s in snt]

            doc = { 'clusters': [], 'doc_key': 'nw', 'sentences': words, 'speakers': speakers }
            print(json.dumps(doc))


if __name__ == '__main__':
    main()

