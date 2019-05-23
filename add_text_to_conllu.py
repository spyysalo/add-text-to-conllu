#!/usr/bin/env python3

import os
import sys
import re

from logging import warning, error


# TODO: complete
PTB_UNESCAPES = {
    '``': '"',
    "''": '"',
}


class Word(object):
    def __init__(self, id_, form, lemma, upos, xpos, feats, head, deprel,
                 deps, misc):
        self.id = id_
        self.form = form
        self.lemma = lemma
        self.upos = upos
        self.xpos = xpos
        self.feats = feats
        self.head = head
        self.deprel = deprel
        self.deps = deps
        self.misc = misc

    def __str__(self):
        return '\t'.join([
            self.id, self.form, self.lemma, self.upos, self.xpos, self.feats,
            self.head, self.deprel, self.deps, self.misc
        ])


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser(description='Add "# text = " lines to CoNLL-U')
    ap.add_argument('-unptb', default=False, action='store_true',
                    help='unescape PTB escapes')
    ap.add_argument('text', help='text file')
    ap.add_argument('conllu', help='CoNLL-U file')
    return ap


def unescape_ptb(words):
    for word in words:
        word.form = PTB_UNESCAPES.get(word.form, word.form)
        word.lemma = PTB_UNESCAPES.get(word.lemma, word.lemma)


def read_sentences(f):
    comments, words = [], []
    for l in f:
        l = l.rstrip('\n')
        if not l or l.isspace():
            yield comments, words
            comments, words = [], []
        elif l.startswith('#'):
            comments.append(l)
        else:
            fields = l.split('\t')
            words.append(Word(*fields))


def write_sentence(comments, words, out=sys.stdout):
    for comment in comments:
        print(comment, file=out)
    for word in words:
        print(word, file=out)
    print(file=out)


def find_ignorespace(text, string):
    """Return (start, end) for string in start of text, ignoring space."""
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


def replace_text_comment(comments, new_text):
    """Replace "# text = " comment (if any) with one using new_text instead."""
    new_text = new_text.replace('\n', ' ')    # newlines cannot be represented
    new_text = new_text.strip(' ')
    new_comments, replaced = [], False
    for comment in comments:
        if comment.startswith('# text ='):
            new_comments.append('# text = {}'.format(new_text))
            replaced = True
        else:
            new_comments.append(comment)
    if not replaced:
        new_comments.append('# text = {}'.format(new_text))
    return new_comments


def set_spaceafter(words, sent_text):
    for word in words:
        if sent_text[:len(word.form)] != word.form:
            raise ValueError('text mismatch: "{}" vs "{}"'.format(
                sent_text[:len(word.form)], word.form))
        sent_text = sent_text[len(word.form):]
        space_after = len(sent_text) == 0 or sent_text[0].isspace()
        sent_text = sent_text.lstrip()
        new_misc, replaced = [], False
        misc = [] if word.misc == '_' else word.misc.split('|')
        for value in misc:
            if value.startswith('SpaceAfter='):
                if not space_after:
                    new_misc.append('SpaceAfter=No')
                replaced = True
            else:
                new_misc.append(value)
        if not replaced:
            if not space_after:
                new_misc.append('SpaceAfter=No')
        if not new_misc:
            word.misc = '_'
        else:
            word.misc = '|'.join(new_misc)


def main(argv):
    args = argparser().parse_args(argv[1:])
    with open(args.text) as f:
        doc_text = f.read()
    with open(args.conllu) as f:
        for comments, words in read_sentences(f):
            if args.unptb:
                unescape_ptb(words)
            token_text = ' '.join(w.form for w in words)
            start, end = find_ignorespace(doc_text, token_text)
            sent_text = doc_text[start:end].strip()
            set_spaceafter(words, doc_text.lstrip())
            comments = replace_text_comment(comments, sent_text)
            write_sentence(comments, words)
            doc_text = doc_text[end:]
        if doc_text.strip():
            error('extra text not found in .conllu data: {}'.format(doc_text))

if __name__ == '__main__':
    sys.exit(main(sys.argv))
