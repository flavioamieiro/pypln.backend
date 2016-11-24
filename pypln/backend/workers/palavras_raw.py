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
import subprocess

from pypln.backend.celery_task import PyPLNTask

# The machine's locale should be set to pt_BR.UTF-8 during palavras'
# installation process.
PALAVRAS_ENCODING = 'utf-8'
BASE_PARSER = '/opt/palavras/por.pl'
PARSER_MODE = '--dep'

def palavras_installed():
    return os.path.exists(BASE_PARSER)

class PalavrasRaw(PyPLNTask):

    def process(self, document):
        if document['language'] != 'pt' or not palavras_installed():
            return {'palavras_raw_ran': False}

        text = document['text']

        # This code is here because when using python2 for some
        # reason, sometimes document['text'] was not a unicode object
        # (as it should be, coming from pymongo).  Since we're now
        # using python3, we should really always get a str (unicode)
        # object. But, since we do not know the real reason for the
        # original error, we will keep this code here for now. As
        # before, if we receive a bytes object, since it came from
        # mongodb we can be sure it will be encoded in utf-8.
        if isinstance(text, bytes):
            text = text.decode('utf-8')

        process = subprocess.Popen([BASE_PARSER, PARSER_MODE],
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(text.encode(PALAVRAS_ENCODING))

        return {'palavras_raw': stdout.decode('utf-8'), 'palavras_raw_ran': True}
