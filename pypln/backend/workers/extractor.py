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
import shlex

from html.parser import HTMLParser
from tempfile import NamedTemporaryFile
from os import unlink
from subprocess import Popen, PIPE
from mimetypes import guess_type
from re import compile as regexp_compile, DOTALL, escape

import pycld2 as cld
import magic

from pypln.backend.celery_task import PyPLNTask


regexp_tags = regexp_compile(r'(<[ \t]*([a-zA-Z0-9!"./_-]*)[^>]*>)', flags=DOTALL)
regexp_comment = regexp_compile(r'<!--.*?-->', flags=DOTALL)
regexp_spaces_start = regexp_compile('([\n]+)[ \t]*',
        flags=DOTALL)
regexp_spaces_end = regexp_compile('[ \t]*\n', flags=DOTALL)
regexp_newlines = regexp_compile('[\n]{3,}', flags=DOTALL)
regexp_spaces = regexp_compile('[ \t]{2,}', flags=DOTALL)
regexp_punctuation = regexp_compile('[ \t]*([' + escape('!,.:;?') + '])',
        flags=DOTALL)
breakline_tags = ['table', '/table', 'tr', 'div', '/div', 'h1', '/h1', 'h2',
                  '/h2', 'h3', '/h3', 'h4', '/h4', 'h5', '/h5', 'h6', '/h6',
                  'br', 'br/']
double_breakline = ['table', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']

def clean(text):
    text = regexp_spaces_start.sub(r'\1', text)
    text = regexp_spaces_end.sub('\n', text)
    text = regexp_newlines.sub('\n\n', text)
    text = regexp_spaces.sub(' ', text)
    text = regexp_punctuation.sub(r'\1', text)
    return text.strip()

def parse_html(html, remove_tags=None, remove_inside=None,
               replace_space_with=' ', replace_newline_with='\n'):
    html = regexp_comment.sub('', html.replace('\n', ''))
    data = regexp_tags.split(html)
    content_between = data[::3]
    complete_tags = data[1::3]
    tag_names = [x.lower() for x in data[2::3]]
    for index, tag_name in enumerate(tag_names):
        if not tag_name.strip():
            continue
        search_tag = tag_name
        if tag_name and tag_name[0] == '/':
            search_tag = tag_name[1:]
        if remove_tags and search_tag not in remove_inside:
            if tag_name in breakline_tags:
                if search_tag in double_breakline:
                    complete_tags[index] = 2 * replace_newline_with
                else:
                    complete_tags[index] = replace_newline_with
            else:
                complete_tags[index] = replace_space_with
        if remove_inside and tag_name in remove_inside:
            remove_to = tag_names.index('/' + tag_name, index)
            total_to_remove = remove_to - index + 1
            complete_tags[index:remove_to + 1] = [''] * total_to_remove
            content_between[index + 2:remove_to + 1] = \
                    [''] * (total_to_remove - 2)
            content_between[index + 1] = '\n'
    complete_tags.append('')
    result = ''.join(sum(list(zip(content_between, complete_tags)), tuple()))
    return clean(result)

def get_pdf_metadata(data: str) -> dict:
    lines = data.strip().splitlines()
    metadata = {}
    for line in lines:
        try:
            key, value = line[:line.index(':')], line[line.index(':') + 1:]
        except ValueError:
            continue
        metadata[key.strip()] = value.strip()
    return metadata

def extract_pdf(data: bytes) -> (str, dict):
    temp = NamedTemporaryFile(delete=False)
    filename = temp.name
    temp.close()
    pdf2html = Popen(shlex.split('pdftohtml -q -i - {}'.format(temp.name)),
                     stdin=PIPE, stdout=PIPE, stderr=PIPE)
    html, html_err = pdf2html.communicate(input=data)
    fp = open(filename + 's.html', 'r')
    html = fp.read()
    fp.close()
    unlink(filename + '.html')
    unlink(filename + '_ind.html')
    unlink(filename + 's.html')
    text = parse_html(html.replace('&#160;', ' '), True, ['script', 'style'])

    info_process = Popen(shlex.split('pdfinfo -'), stdin=PIPE, stdout=PIPE,
                         stderr=PIPE)
    meta_out, meta_err = info_process.communicate(input=data)
    try:
        metadata = get_pdf_metadata(meta_out.decode('utf-8'))
    except Exception:
        # TODO: what should I do here?
        metadata = {}

    if not (text and metadata):
        return '', {}
    elif not html_err:
        return text, {} if meta_err else metadata
    else:
        return '', {}


def decode_text_bytes(text: bytes) -> str:
    """
    Tries to detect text encoding using file magic. If that fails or the
    detected encoding is not supported, tries using utf-8. If that doesn't work
    tries using iso8859-1.
    """
    try:
        with magic.Magic(flags=magic.MAGIC_MIME_ENCODING) as m:
            content_encoding = m.id_buffer(text)
    except magic.MagicError:
        pass  # This can happen for instance if text is a single char
    else:
        try:
            return text.decode(content_encoding)
        except LookupError:  # The detected encoding is not supported
            pass

    try:
        result = text.decode('utf-8')
    except UnicodeDecodeError:
        # Decoding with iso8859-1 doesn't raise UnicodeDecodeError, so this is
        # a last resort.
        result = text.decode('iso8859-1')
    return result


class Extractor(PyPLNTask):
    #TODO: need to verify some exceptions when trying to convert 'evil' PDFs
    #TODO: should 'replace_with' be '' when extracting from HTML?

    def process(self, file_data):
        contents = base64.b64decode(file_data['contents'])
        with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as m:
            file_mime_type = m.id_buffer(contents)

        metadata = {}
        if file_mime_type == 'text/plain':
            text = contents
        elif file_mime_type == 'text/html':
            text = parse_html(contents, True, ['script', 'style'])
        elif file_mime_type == 'application/pdf':
            text, metadata = extract_pdf(contents)
        else:
            # If we can't detect the mimetype we add a flag that can be read by
            # the frontend to provide more information on why the document
            # wasn't processed.
            # XXX: We're returning an empty text because if we don't the
            # pipeline will run indefinitely. The right approach is to make
            # pypelinin understand an specific exception (something like
            # StopPipeline) as a signal to stop processing this pipeline.
            return {'mimetype': 'unknown', 'text': "",
                    'file_metadata': {}, 'language': ""}

        if isinstance(text, bytes):
            text = decode_text_bytes(text)

        if isinstance(text, str):
            # HTMLParser only handles unicode objects. We can't pass the text
            # through it if we don't know the encoding, and it's possible we
            # also shouldn't. There's no way of knowing if it's a badly encoded
            # html or a binary blob that happens do have bytes that look liked
            # html entities.
            text = HTMLParser().unescape(text)

        text = clean(text)

        if isinstance(text, str):
            language = cld.detect(text.encode('utf-8'))[1]
        else:
            language = cld.detect(text)[1]

        # TODO: check for uses of forced_decoding and remove them
        return {'text': text, 'file_metadata': metadata, 'language': language,
                'mimetype': file_mime_type, 'forced_decoding': None}
