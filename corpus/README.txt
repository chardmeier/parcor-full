ParCorFull -- a parallel corpus annotated for coreference
=========================================================

Release 1 (May 2018)
http://hdl.handle.net/11372/LRT-2614

Ekaterina Lapshinova-Koltunski, Christian Hardmeier and Pauline Krielke
-----------------------------------------------------------------------

This is the first release of ParCorFull, an English-German parallel corpus
annotated for full coreference.

If you use this corpus in published work, please cite the following paper:

@InProceedings{Lapshinova-Koltunski:2018,
  author = {Ekaterina Lapshinova-Koltunski and Christian Hardmeier and Pauline Krielke},
  title = {{ParCorFull:} a Parallel Corpus Annotated with Full Coreference},
  booktitle = {Proceedings of the Eleventh International Conference on Language Resources and Evaluation (LREC 2018)},
  pages = {423--428},
  year = {2018},
  month = {May},
  address = {Miyazaki, Japan},
  publisher = {European Language Resources Association (ELRA)}
}

http://www.lrec-conf.org/proceedings/lrec2018/summaries/941.html

ParCorFull is a parallel corpus annotated with full coreference chains that has
been created to address an important problem that machine translation and other
multilingual natural language processing (NLP) technologies face -- translation
of coreference across languages. Our corpus contains parallel texts for the
language pair English-German, two major European languages. Despite being
typologically very close, these languages still have systemic differences in the
realisation of coreference, and thus pose problems for multilingual coreference
resolution and machine translation. Our parallel corpus covers the genres of
planned speech (public lectures) and newswire. It is richly annotated for
coreference in both languages, including annotation of both nominal coreference
and reference to antecedents expressed as clauses, sentences and verb phrases.
This resource supports research in the areas of natural language processing,
contrastive linguistics and translation studies on the mechanisms involved in
coreference translation in order to develop a better understanding of the
phenomenon.

The corpus consists of three parts:

TED     - TED talks, corresponding to the test set of the IWSLT 2013 shared task
DiscoMT - TED talks, corresponding to the test set of the DiscoMT 2015 shared task
news    - News texts, taken from the test set of the WMT 2017 news shared task

The annotations in the corpus are partly based on those of the ParCor corpus
(Guillou et al., 2016).

Note: In the TED subcorpus, document 009 (TED talk 805) was excluded from this
release because of serious technical problems with the annotations. We plan to
add this document in a later release.

The English texts in ParCorFull were tokenised with the Penn Treebank-style
tokeniser of NLTK 3.2.4 (http://www.nltk.org/). The German texts were tokenised
with the standard German model of Spacy 2.0.9 (https://spacy.io/). In a handful
of cases, the tokenisation was amended manually. This mostly concerned places
where a single apostrophe was used as a quotation mark and the automatic
tokeniser failed to separate it from the following word.

References:

Liane Guillou, Christian Hardmeier, Aaron Smith, Jörg Tiedemann and Bonnie
Webber (2014): ParCor 1.0: A Parallel Pronoun-Coreference Corpus to Support
Statistical MT. In Proceedings of LREC 2014, Reykjavik, Iceland.
http://www.lrec-conf.org/proceedings/lrec2014/summaries/298.html
