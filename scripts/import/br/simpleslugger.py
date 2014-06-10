# -*- coding: utf-8 -*-
from nltk.corpus import stopwords as _stopwords
from nltk.tokenize import PunktWordTokenizer
from curses.ascii import isascii
import unicodedata

language = "portuguese"
stopwords = [sw.decode('utf-8') for sw in _stopwords.words(language)]
punctuation = u'!(),-.:;?'
tkz = PunktWordTokenizer()

make_ascii = lambda text: \
    filter(isascii, unicodedata.normalize('NFD', text).encode('utf-8'))

def detokenize(words):
    text = "".join((" " if w not in punctuation else "") + w for w in words)
    return text

def make_slug(text):
    text = text.replace(u"/", u"")
    text = text.replace(u".", u"")
    words = [make_ascii(w.lower()) for w in tkz.tokenize(text) if (w not in stopwords) and (w not in punctuation)]
    return u"-".join(words)
