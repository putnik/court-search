import textract
import ijson
import magic
import os
import re
import wget
import urllib
from time import sleep
from urllib.request import urlopen
from zipfile import ZipFile


passport_url = 'https://data.mos-gorsud.ru/opendata/1577103912804-casesallwcdeh'
json_url = 'https://data.mos-gorsud.ru/api/opendata/1577103912804-casesallwcdeh/v150/data/json'

FILE_TYPES_EXT = {
    'application/msword': 'doc',
    'application/octet-stream': 'docx',  # ???
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
    'application/pdf': 'pdf',
    'application/zip': 'docx',  # ???
    'text/rtf': 'rtf',
}

DIR = '../../data/mosgorsud/'

def download_json():
    zip_file = DIR + 'data.json.zip'
    wget.download(json_url, zip_file)
    zf = ZipFile(zip_file, 'r')
    for name in zf.namelist():
        print(name)
        zf.extract(name, DIR)


def process_cases():
    with open(DIR + 'data.json') as f:
        cases = ijson.items(f, 'item')
        for case in cases:
            if case['dateReg'] < '2022-01-01':
                continue
            if 'attachments' in case:
                for attachment in case['attachments']:
                    get_document_text(attachment['link'])


def get_document_text(url: str) -> str:
    doc_id = url.replace('https://mos-gorsud.ru/mgs/cases/docs/content/', '')
    txt_file = '%s/documents/%s.txt' % (DIR, doc_id)

    if os.path.isfile(txt_file):
        with open(txt_file) as f:
            return f.read()

    url = 'https://mos-gorsud.ru/mgs/cases/docs/content/%s' % doc_id
    print(url)

    try:
        request = urllib.request.Request(url)
        sleep(0.2)
        response = urlopen(request)
        file_content = response.read()
    except:
        print('FILE ERROR')
        return ''

    mime_type = magic.from_buffer(file_content, mime=True)
    if mime_type not in FILE_TYPES_EXT:
        print(mime_type)
        return ''

    doc_file = '%s/documents/%s.%s' % (DIR, doc_id, FILE_TYPES_EXT[mime_type])
    with open(doc_file, 'wb') as f:
        f.write(file_content)

    try:
        text = textract.process(doc_file).decode("utf-8")
        text = re.sub(r'[\t ]+', ' ', text)

        with open(txt_file, 'w') as f:
            f.write(text)

        return text
    except:
        return ''


if __name__ == '__main__':
    download_json()
    process_cases()
