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

import os
from unittest import TestCase, mock

from pypln.backend.workers.spellchecker import (SpellingChecker,
                                                MissingDictionaryWarning)

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))


class TestSpellcheckerWorker(TestCase):
    def test_spellcheck_pt(self):
        text = "Meu cachoro é um pastor"
        result = SpellingChecker().process({'text': text, 'language': 'pt_BR'})

        self.assertEqual(len(result['spelling_errors']), 1)
        self.assertIn('cachoro', result['spelling_errors'][0])
        self.assertIn('cachorro', result['spelling_errors'][0][2])
        self.assertEqual(result['spelling_errors'][0][1], 4)

    def test_spellcheck_en(self):
        text = "The cat bit the doggyo"
        result = SpellingChecker().process({'text': text, 'language': 'en'})

        self.assertEqual(len(result['spelling_errors']), 1)
        self.assertIn('doggyo', result['spelling_errors'][0])
        self.assertIn('doggy', result['spelling_errors'][0][2])
        self.assertEqual(result['spelling_errors'][0][1], 16)

    @mock.patch('warnings.warn')
    def test_warns_about_missing_dictionary(self, warn_mock):
        SpellingChecker().process({'text': '',
                                   'language': 'missing_language'})
        warn_mock.assert_called_with(mock.ANY, MissingDictionaryWarning)
