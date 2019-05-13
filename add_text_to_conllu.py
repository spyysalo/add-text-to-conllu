#!/usr/bin/env python3

import os
import sys

from collections import namedtuple


# https://universaldependencies.org/format.html
CONLLU_FIELDS = [
    'id',
    'form',
    'lemma',
    'upos',
    'xpos',
    'feats',
    'head',
    'deprel',
    'deps',
    'misc',
]


Word = namedtuple('Word', CONLLU_FIELDS)


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser(description='Add "# text = " lines to CoNLL-U')
    ap.add_argument('text', help='text file')
    ap.add_argument('conllu', help='CoNLL-U file')
    return ap


def read_sentences(f):
    words = []
    for l in f:
        l = l.rstrip('\n')
        if not l or l.isspace():
            yield words
            words = []
        else:
            fields = l.split('\t')
            words.append(Word(*fields))


def write_sentence(s, out=sys.stdout):
    for w in s:
        print('\t'.join(w), file=out)
    print(file=out)


def find_ignorespace(text, string):
    """Return (start, end) for s in start of text, ignoring space."""
    ti, si = 0, 0
    while ti < len(text) and si < len(string):
        if text[ti] == string[si]:
            ti += 1
            si += 1
        elif text[ti].isspace():
            ti += 1
        elif string[si].isspace():
            si += 1
        else:
            raise ValueError('{} not prefix of {}[...]'.format(
                string, text[:len(string)]))
    if si != len(string):
        raise ValueError('{} not prefix of {}[...]'.format(
            string, text[:len(string)]))
    return (0, ti)


def main(argv):
    args = argparser().parse_args(argv[1:])
    with open(args.text) as f:
        text = f.read()
    with open(args.conllu) as f:
        for s in read_sentences(f):
            t = ''.join(w.form for w in s)
            start, end = find_ignorespace(text, t)
            print('# text = {}'.format(text[start:end].strip()))
            write_sentence(s)
            text = text[end:]


if __name__ == '__main__':
    sys.exit(main(sys.argv))
