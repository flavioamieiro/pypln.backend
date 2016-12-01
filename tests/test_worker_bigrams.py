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

import nltk
from unittest import mock

from pypln.backend.workers.bigrams import Bigrams
from .utils import TaskTest

bigram_measures = nltk.collocations.BigramAssocMeasures()


class TestBigramWorker(TaskTest):
    @mock.patch('pypln.backend.workers.bigrams.BigramCollocationFinder')
    def test_bigrams_should_return_correct_score(self, mocked_bigram_finder):
        tokens = ['O', 'doce', 'perguntou', 'pro', 'doce', 'qual',
                  'o', 'doce', 'mais', 'doce', '.', 'O', 'doce',
                  'respondeu', 'pro', 'doce', 'que', 'o', 'doce',
                  'mais', 'doce', 'é', 'o', 'doce', 'de', 'batata',
                  'doce', '.']

        result = Bigrams().process({'tokens': tokens})
        mocked_bigram_finder.from_words.assert_called_with(tokens)
        mocked_bigram_finder.from_words.return_value.score_ngrams.has_calls(
            getattr(bigram_measures, 'chi_sq'))
        mocked_bigram_finder.from_words.return_value.score_ngrams.has_calls(
            getattr(bigram_measures, 'dice'))
        mocked_bigram_finder.from_words.return_value.score_ngrams.has_calls(
            getattr(bigram_measures, 'jaccard'))
        mocked_bigram_finder.from_words.return_value.score_ngrams.has_calls(
            getattr(bigram_measures, 'likelihood_ratio'))
        mocked_bigram_finder.from_words.return_value.score_ngrams.has_calls(
            getattr(bigram_measures, 'mi_like'))
        mocked_bigram_finder.from_words.return_value.score_ngrams.has_calls(
            getattr(bigram_measures, 'phi_sq'))
        mocked_bigram_finder.from_words.return_value.score_ngrams.has_calls(
            getattr(bigram_measures, 'pmi'))
        mocked_bigram_finder.from_words.return_value.score_ngrams.has_calls(
            getattr(bigram_measures, 'poisson_stirling'))
        mocked_bigram_finder.from_words.return_value.score_ngrams.has_calls(
            getattr(bigram_measures, 'raw_freq'))
        mocked_bigram_finder.from_words.return_value.score_ngrams.has_calls(
            getattr(bigram_measures, 'student_t'))

    def test_bigrams_could_contain_dollar_signs_and_dots(self):
        tokens = ['$', '.']

        result = Bigrams().process({'tokens': tokens})
        bigram_rank = result['bigram_rank']
        chi_sq = bigram_rank[0][1][0]
        # 2.0 is the value of the chi_sq measure for this bigram in this
        # colocation
        expected_chi_sq = 2.0
        self.assertEqual(chi_sq, expected_chi_sq)
