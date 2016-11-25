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
from unittest import TestCase

from pypln.backend.workers import FreqDist


class TestFreqDistWorker(TestCase):
    def test_freqdist_should_be_a_list_of_tuples_with_frequency_distribution(self):
        tokens = ['The', 'sky', 'is', 'blue', ',', 'the', 'sun', 'is',
                  'yellow', '.']

        expected_fd = [('is', 2), ('the', 2), (',', 1), ('.', 1), ('blue', 1),
                       ('sky', 1), ('sun', 1), ('yellow', 1)]

        resulting_fd = FreqDist().process({'tokens': tokens})['freqdist']
        self.assertEqual(resulting_fd, expected_fd)
