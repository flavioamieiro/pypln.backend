# coding: utf-8
#
# Copyright 2015 NAMD-EMAP-FGV
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
from pypln.backend.celery_task import PyPLNCorpusTask
from mock import MagicMock
from utils import TaskTest


class FakeCorpusTask(PyPLNCorpusTask):
    def process(self, documents):
        return {'result': sum([d["input"] for d in documents])}

class TestCeleryCorpusTask(TaskTest):
    def test_task_should_only_get_the_correct_documents(self):
        # This is just preparing the expected input in the database
        wrong_doc_id = self.collection.insert({'input': 999}, w=1)
        correct_doc_id_1 = self.collection.insert({'input': 1}, w=1)
        correct_doc_id_2 = self.collection.insert({'input': 1}, w=1)
        fake_corpus_id = 1

        FakeCorpusTask.process = MagicMock(return_value={'result': 2})

        corpus_task = FakeCorpusTask()

        corpus_task.delay(fake_corpus_id, [correct_doc_id_1, correct_doc_id_2])

        corpus_task.process.assert_called()

        # We need to compare the call args because it's called with a mongo
        # cursor, not a list.
        # We're getting [0][0] because we want the args (not kwargs) for the
        # first call to the method.
        call_args = list(corpus_task.process.call_args[0][0])
        for arg in call_args:
            self.assertEqual(arg['input'], 1)

    def test_task_is_saving_the_result_to_mongo_with_the_corpus_id(self):
        expected_result = 42
        doc_id_1 = self.collection.insert({'input': 21}, w=1)
        doc_id_2 = self.collection.insert({'input': 21}, w=1)
        fake_corpus_id = 1

        FakeCorpusTask().delay(fake_corpus_id, [doc_id_1, doc_id_2])

        resulting_corpus_analysis = self.corpora_collection.find_one(
                {'corpus_id': fake_corpus_id})['result']

        self.assertEqual(resulting_corpus_analysis, expected_result)
