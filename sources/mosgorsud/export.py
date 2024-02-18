import ijson
import json
import os
import re


DIR = '../../data/mosgorsud/'


def get_doc_text(attachment: dict) -> str | None:
    doc_id = attachment['link'].replace('https://mos-gorsud.ru/mgs/cases/docs/content/', '')
    txt_file = '%s/documents/%s.txt' % (DIR, doc_id)
    if not os.path.isfile(txt_file):
        return None

    with open(txt_file) as f:
        text = f.read()

    text = text.strip()
    text = re.sub(r'[\u0000-\u001f]', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text


def get_case_add_command(case: dict) -> dict:
    participants = set()
    codex_articles = set()
    if 'participants' in case:
        for participant in case['participants']:
            name = '%s (%s)' % (
                participant['displayName'],
                participant['categoryName'] or '',
            )
            participants.add(name)
            if 'codexArticles' in participant:
                for codexArticle in participant['codexArticles']:
                    codex_articles.add(codexArticle['name'])

    attachments = []
    if 'attachments' in case:
        for attachment in case['attachments']:
            text = get_doc_text(attachment)
            if text is not None:
                attachments.append(text)
    if len(attachments) == 0:
        attachments = ['']

    return {
        'type': 'add',
        'id': 'mosgorsud:' + case['_id'],
        'fields': {
            'number': case['number'],
            'uid': case['uid'] or '',
            'url': case['url'] or '',
            'year': case['year'] or 0,
            'last_session_type': case['lastSessionType'] or '',
            'document_type': case['documentType'] or '',
            'court_code': case['courtCode'] or '',
            'court_name': case['courtName'] or '',
            'judge': case['judge'] or '',
            'publishing_state': case['publishingState'] or '',
            'date_reg': '%sT00:00:00Z' % (case['dateReg'] or '1970-01-01'),
            'date_legal': '%sT00:00:00Z' % (case['dateLegal'] or '1970-01-01'),
            'date_final': '%sT00:00:00Z' % (case['dateFinal'] or '1970-01-01'),
            'last_hearing_date': '%sT00:00:00Z' % (case['lastHearingDate'] or '1970-01-01'),
            'participants': list(participants),
            'codex_articles': list(codex_articles),
            'attachments': attachments,
        }
    }


def export_cases():
    size = 0
    with open(DIR + 'data.json') as f:
        export_id = 1
        fw = open('%s/export/%s.json' % (DIR, export_id), 'w')
        fw.write('[')

        first = True
        cases = ijson.items(f, 'item')

        for case in cases:
            row = get_case_add_command(case)
            json_row = json.dumps(row)

            if size + len(json_row) > 5242000:
                fw.write('\n]')
                fw.close()

                export_id += 1
                size = 0
                fw = open('%s/export/%s.json' % (DIR, export_id), 'w')
                fw.write('[')
                first = True

            if first:
                first = False
                fw.write('\n')
            else:
                fw.write(',\n')

            size += len(json_row)
            fw.write(json_row)

        fw.write('\n]')


if __name__ == '__main__':
    export_cases()
