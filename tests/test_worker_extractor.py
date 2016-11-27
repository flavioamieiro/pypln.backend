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

import base64
import os
from textwrap import dedent
from unittest import TestCase
from unittest.mock import patch, Mock, MagicMock, call

from magic import MagicError

from pypln.backend.workers import Extractor
from pypln.backend.workers.extractor import decode_text_bytes

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))


class DecodeTextBytesTest(TestCase):
    def setUp(self):
        magic_mock = MagicMock()
        magic_identifier = Mock()
        self.id_buffer_mock = Mock(return_value='magic_codec')
        magic_identifier.id_buffer = self.id_buffer_mock
        magic_mock.return_value.__enter__.return_value = magic_identifier
        self.magic_patcher = patch('magic.Magic', magic_mock)

    def test_ignores_magic_error(self):
        self.id_buffer_mock.side_effect = MagicError()
        text = Mock()
        with self.magic_patcher:
            result = decode_text_bytes(text)
        self.assertEqual(result, text.decode.return_value)
        self.assertEqual(text.decode.call_args_list, [call('utf-8')])

    def test_tries_decoding_with_encoding_returned_by_magic(self):
        text = Mock()
        with self.magic_patcher:
            result = decode_text_bytes(text)
        self.assertEqual(result, text.decode.return_value)
        self.assertEqual(text.decode.call_args_list, [call('magic_codec')])

    def test_tries_decoding_as_utf8(self):
        text = Mock()
        text.decode.side_effect = [LookupError(), 'result']
        with self.magic_patcher:
            result = decode_text_bytes(text)
        self.assertEqual(result, 'result')
        self.assertEqual(text.decode.call_args_list,
                         [call('magic_codec'), call('utf-8')])

    def test_tries_iso8859_1_if_all_else_fails(self):
        text = Mock()

        class FakeUnicodeDecodeError(UnicodeDecodeError):
            def __init__(self):
                pass

        text.decode.side_effect = [LookupError(),
                                   FakeUnicodeDecodeError(),
                                   'result']
        with self.magic_patcher:
            result = decode_text_bytes(text)
        self.assertEqual(result, 'result')
        self.assertEqual(text.decode.call_args_list,
                         [call('magic_codec'),
                          call('utf-8'),
                          call('iso8859-1')])


class TestExtractorWorker(TestCase):
    def test_extraction_from_text_file(self):
        expected = "This is a test file.\nI'm testing PyPLN extractor worker!"
        filename = os.path.join(DATA_DIR, 'test.txt')
        data = {'filename': filename,
                'contents': base64.b64encode(open(filename, 'rb').read())}
        result = Extractor().process(data)
        self.assertEqual(result['text'], expected)
        self.assertEqual(result['file_metadata'], {})
        self.assertEqual(result['mimetype'], 'text/plain')

    def test_extraction_from_html_file(self):
        expected = "This is a test file. I'm testing PyPLN extractor worker!"
        filename = os.path.join(DATA_DIR, 'test.html')
        # When saving directly to mongodb we always get everything back from
        # the database as unicode. Because of that, the extractor is having
        # problems when there is a non-ascii character in the content. This
        # wasn't a problem before because with mongodict we used to keep a
        # pickled representation of the data.
        data = {'filename': filename,
                'contents': base64.b64encode(open(filename, 'rb').read())}
        result = Extractor().process(data)
        self.assertEqual(result['text'], expected)
        self.assertEqual(result['file_metadata'], {})
        self.assertEqual(result['mimetype'], 'text/html')

    def test_extraction_from_pdf_file(self):
        expected = "This is a test file.\nI'm testing PyPLN extractor worker!"
        filename = os.path.join(DATA_DIR, 'test.pdf')
        data = {'filename': filename,
                'contents': base64.b64encode(open(filename, 'rb').read())}
        result = Extractor().process(data)
        self.assertEqual(result['text'], expected)
        # Check that the expected metadata is a subset of what
        # our Extractor found (it may have found more details
        # depending on the toolset used to extract metadata)
        metadata_expected = {
                'Author':         'Álvaro Justen',
                'Creator':        'Writer',
                'Producer':       'LibreOffice 3.5',
                'CreationDate':   'Fri Jun  1 17:07:57 2012',
                'Tagged':         'no',
                'Pages':          '1',
                'Encrypted':      'no',
                'Page size':      '612 x 792 pts (letter)',
                'Optimized':      'no',
                'PDF version':    '1.4',
        }
        metadata_expected_set = set(metadata_expected.items())
        metadata = result['file_metadata']
        metadata_set = set(metadata.items())
        diff_set = metadata_expected_set - metadata_set
        self.assertTrue(metadata_expected_set.issubset(metadata_set),
                        ("Extracted metadata is not a subset of the expected metadata. "
                         "Items missing or with different values: {}").format(
                         ", ".join(str(item) for item in diff_set)))
        self.assertEqual(result['mimetype'], 'application/pdf')

    def test_extraction_from_html(self):
        contents = dedent('''
        <html>
          <head>
            <title>Testing</title>
            <script type="text/javascript">this must not appear</script>
            <style type="text/css">this must not appear [2]</style>
          </head>
          <body>
            python test1
            <br>
            test2
            <table>
              <tr><td>spam</td></tr>
              <tr><td>eggs</td></tr>
              <tr><td>ham</td></tr>
            </table>
            test3
            <div>test4</div>test5
            <span>test6</span>test7
            <h1>bla1</h1> bla2
          </body>
        </html>
        ''')
        data = {'filename': 'test.html',
                'contents': base64.b64encode(contents.encode('utf-8'))}
        result = Extractor().process(data)
        expected = dedent('''
            Testing

            python test1
            test2

            spam
            eggs
            ham

            test3
            test4
            test5 test6 test7

            bla1

            bla2''').strip()
        self.assertEqual(result['text'], expected)
        self.assertEqual(result['mimetype'], 'text/html')

    def test_language_detection_pt(self):
        text = 'Esse texto foi escrito por Álvaro em Português.'
        data = {'filename': 'text-pt.txt',
                'contents': base64.b64encode(text.encode('utf-8'))}
        result = Extractor().process(data)
        self.assertEqual(result['language'], 'pt')

    def test_language_detection_es(self):
        text = 'Este texto ha sido escrito en Español por Álvaro.'
        data = {'filename': 'text-es.txt',
                'contents': base64.b64encode(text.encode('utf-8'))}
        result = Extractor().process(data)
        self.assertEqual(result['language'], 'es')

    def test_language_detection_en(self):
        text = 'This text was written by Álvaro in English.'
        data = {'filename': 'text-en.txt',
                'contents': base64.b64encode(text.encode('utf-8'))}
        result =  Extractor().process(data)
        self.assertEqual(result['language'], 'en')

    def test_unescape_html_entities(self):
        expected = ("This text has html <entities>. Álvaro asked me to make"
                     " sure it also has non ascii chars.")
        filename = os.path.join(DATA_DIR, 'test_html_entities.txt')
        data = {'filename': filename,
                'contents': base64.b64encode(open(filename, 'rb').read())}
        result = Extractor().process(data)
        self.assertEqual(result['text'], expected)

    def test_should_detect_encoding_and_return_a_unicode_object(self):
        expected = "Flávio"
        filename = os.path.join(DATA_DIR, 'test_iso-8859-1.txt')
        data = {'filename': filename,
                'contents': base64.b64encode(open(filename, 'rb').read())}
        result = Extractor().process(data)
        self.assertEqual(result['text'], expected)
        self.assertEqual(type(result['text']), str)

    def test_should_guess_mimetype_for_file_without_extension(self):
        contents = "This is a test file. I'm testing PyPLN extractor worker!"
        filename = os.path.join(DATA_DIR, 'text_file')
        data = {'filename': filename,
                'contents': base64.b64encode(contents.encode('utf-8'))}
        result = Extractor().process(data)
        self.assertEqual(result['mimetype'], 'text/plain')

    def test_unknown_mimetype_should_be_flagged(self):
        filename = os.path.join(DATA_DIR, 'random_file')
        # we can't put the expected text content here, so we'll just make sure
        # it's equal to the input content, since
        contents = open(filename, 'rb').read()
        result = Extractor().process({'filename': filename,
                                      'contents': base64.b64encode(contents)})
        self.assertEqual(result['mimetype'], 'unknown')
        self.assertEqual(result['text'], "")
        self.assertEqual(result['language'], "")
        self.assertEqual(result['file_metadata'], {})

    def test_unknown_encoding_should_be_ignored(self):
        filename = os.path.join(DATA_DIR, 'encoding_unknown_to_libmagic.txt')
        expected = "This file has a weird byte (\x96) that makes it " \
                   "impossible for libmagic to recognize it's encoding."
        data = {'filename': filename,
                'contents': base64.b64encode(open(filename, 'rb').read())}
        result = Extractor().process(data)
        self.assertEqual(result['text'], expected)
        self.assertEqual(result['file_metadata'], {})
        self.assertEqual(result['language'], 'en')
