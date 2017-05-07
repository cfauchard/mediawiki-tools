#!/usr/bin/env python3
# coding: utf8
# -----------------------------------------------------------------
# export Mediawiki pages in directory structure
#
# Copyright (C) 2016-2017, Christophe Fauchard
# -----------------------------------------------------------------

__version_info__ = (0, 2, 0, 'b1')
__version__ = '.'.join(map(str, __version_info__))

import argparse
import sqlite3
import re

parser = argparse.ArgumentParser(
    description='export Mediawiki pages in directory structure')
parser.add_argument(
    "--version",
    action='version',
    version='%(prog)s ' + __version__)
parser.add_argument('database', help="database SQLite3 file")
parser.add_argument('directory', help="export directory")

re_wikitext = re.compile(".*\..*$")

args = parser.parse_args()
try:
    conn = sqlite3.connect("file:" + args.database + "?mode=ro", uri=True)

    for page_row in conn.execute(
            'SELECT page_id, page_title FROM page ORDER BY page_title'):
        page_id = page_row[0]
        page_name = page_row[1]

        select_newer_revision = "select max(rev_timestamp) from revision where rev_page = %d" % (page_id)
        select_rev_text_id = "select rev_text_id from revision where rev_timestamp = (%s)" % (select_newer_revision)
        select_text = "select old_text from text where old_id = (%s)" % (select_rev_text_id)

        for text_row in conn.execute(select_text):
            if not re_wikitext.match(page_name):
                page_name = page_name + ".wikitext"
                fd = open(args.directory + "/" + page_name, mode='w')
                fd.write(text_row[0])
                print(page_name)
                fd.close()

    conn.close()

except sqlite3.OperationalError as error:
    print(error.__str__())
    exit(2)
except FileNotFoundError as error:
    print(error.strerror, error.filename)
except PermissionError as error:
    print(error.strerror, error.filename)
