# coding: utf-8
#
# Copyright 2014 NAMD-EMAP-FGV
#
# This file is part of PyPLN. You can get more information at: http://pypln.org/.
#
# PyPLN is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyPLN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyPLN.  If not, see <http://www.gnu.org/licenses/>.

import base64
import string
from io import BytesIO

import numpy
import nltk
from wordcloud import make_wordcloud

from pypln.backend.celery_task import PyPLNTask

def filter_stopwords(fdist, lang):
    long_name = {'en': 'english', 'pt': 'portuguese'}
    stopwords =  list(string.punctuation)
    if lang in long_name:
        stopwords += nltk.corpus.stopwords.words(long_name[lang])
    return [pair for pair in fdist if pair[0].lower() not in stopwords]

class WordCloud(PyPLNTask):

    def process(self, document):
        fdist = filter_stopwords(document['freqdist'], document['language'])
        words = numpy.array([t[0] for t in fdist])
        counts = numpy.array([t[1] for t in fdist])
        wordcloud_img = make_wordcloud(words, counts)
        fd = BytesIO()
        wordcloud_img.save(fd, format="PNG")
        fd.seek(0)
        result = {'wordcloud': base64.b64encode(fd.read())}
        fd.close()

        return result
