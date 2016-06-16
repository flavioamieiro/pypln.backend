# coding: utf-8
#
# Copyright 2012 NAMD-EMAP-FGV
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
from pypln.backend.workers import CorpusFreqDist
from utils import TaskTest


class TestCorpusFreqDistWorker(TaskTest):
    def test_freqdist_should_return_a_list_of_tuples_with_frequency_distribution(self):

        freqdist_1 =  [[u'is', 2], [u'the', 2], [u'blue', 1], [u'sun', 1],
                [u'sky', 1], [u',', 1], [u'yellow', 1], [u'.', 1]]

        freqdist_2 = [[u'the', 2], [u'brown', 1], [u'lazy', 1],
                [u'over', 1], [u'fox', 1], [u'dog', 1], [u'.', 1],
                [u'quick', 1], [u'jumps', 1]]

        corpus_fd =  [[u'the', 4], [u'is', 2], [u'.', 2], [u'blue', 1],
                [u'brown', 1], [u'lazy', 1], [u'fox', 1], [u'jumps', 1],
                [u'sun', 1], [u'dog', 1], [u'sky', 1], [u',', 1],
                [u'yellow', 1], [u'quick', 1], [u'over', 1]]

        doc_id_1 = self.collection.insert({'freqdist': freqdist_1}, w=1)
        doc_id_2 = self.collection.insert({'freqdist': freqdist_2}, w=1)
        fake_corpus_id = 1


        CorpusFreqDist().delay(fake_corpus_id, [doc_id_1, doc_id_2])

        resulting_corpus_fd = self.corpora_collection.find_one(
                {'corpus_id': fake_corpus_id})['freqdist']

        self.assertEqual(resulting_corpus_fd, corpus_fd)
