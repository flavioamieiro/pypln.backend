# coding: utf-8

import unittest
from textwrap import dedent
from pypln.workers import extractor


class TestExtractorWorker(unittest.TestCase):
    def test_extraction_from_text_file(self):
        expected = "This is a test file.\nI'm testing PyPLN extractor worker!"
        filename = 'tests/data/test.txt'
        data = {'filename': filename, 'contents': open(filename).read()}
        result = extractor.main(data)
        metadata = result['file_metadata']
        self.assertEqual(expected, result['text'])
        self.assertEqual(metadata, {})

    def test_extraction_from_html_file(self):
        expected = "This is a test file. I'm testing PyPLN extractor worker!"
        filename = 'tests/data/test.html'
        data = {'filename': filename, 'contents': open(filename).read()}
        result = extractor.main(data)
        metadata = result['file_metadata']
        self.assertEqual(expected, result['text'])
        self.assertEqual(metadata, {})

    def test_extraction_from_pdf_file(self):
        expected = "This is a test file.\nI'm testing PyPLN extractor worker!"
        filename = 'tests/data/test.pdf'
        data = {'filename': filename, 'contents': open(filename).read()}
        result = extractor.main(data)
        metadata = result['file_metadata']
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
        self.assertEqual(expected, result['text'])
        self.assertEqual(metadata, metadata_expected)

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
        data = {'filename': 'test.html', 'contents': contents}
        result = extractor.main(data)
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

    def test_language_detection(self):
        text_pt = 'Esse texto foi escrito por Álvaro em Português.'
        text_es = 'Este texto ha sido escrito en Español por Álvaro.'
        text_en = 'This text was written by Álvaro in English.'
        data_pt = {'filename': 'text-pt.txt', 'contents': text_pt}
        data_es = {'filename': 'text-es.txt', 'contents': text_es}
        data_en = {'filename': 'text-en.txt', 'contents': text_en}
        result_pt = extractor.main(data_pt)
        result_es = extractor.main(data_es)
        result_en = extractor.main(data_en)
        self.assertEqual('pt', result_pt['language'])
        self.assertEqual('es', result_es['language'])
        self.assertEqual('en', result_en['language'])