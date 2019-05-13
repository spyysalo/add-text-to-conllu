# add-text-to-conllu

Add "`# text = `" lines from a text file to CoNLL-U data .

This is a special-purpose script written to handle an issue with CRAFT corpus CONLL-U data, not intended or recommended for use for anything else.

## Example

```
$ python3 add_text_to_conllu.py example/15550985.{txt,tree.conllu} > 15550985.tree.conllu.withtext

$ diff example/15550985.tree.conllu 15550985.tree.conllu.withtext | egrep '^>' | head -n 3
> # text = A Chemoattractant Role for NT-3 in Proprioceptive Axon Guidance
> # text = Abstract
> # text = Neurotrophin-3 (NT-3) is required for proprioceptive neuron survival.
```
