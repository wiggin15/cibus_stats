import imaplib
import email
import re

# CIBUS_SUBJECT_PREIFX = "ishur iska al sach -"
CIBUS_SUBJECT_PREIFX = '\xd7\x90\xd7\x99\xd7\xa9\xd7\x95\xd7\xa8 \xd7\xa2\xd7\xa1\xd7\xa7\xd7\x94 \xd7\xa2\xd7\x9c \xd7\xa1\xd7\x9a -'
# CIBUS_SUBJECT_PREIFX = "hiyuv kartis tenbis bemiseded "
TENBIS_SUBJECT_PREFIX = "\xd7\x97\xd7\x99\xd7\x95\xd7\x91 \xd7\x9b\xd7\xa8\xd7\x98\xd7\x99\xd7\xa1 \xd7\xaa\xd7\x9f \xd7\x91\xd7\x99\xd7\xa1 \xd7\x91\xd7\x9e\xd7\xa1\xd7\xa2\xd7\x93\xd7\xaa "
# TENBIS_BODY_PATTERN = "al sach * bemiseded *"
TENBIS_BODY_PATTERN = "\r\n\xd7\xa2\xd7\x9c \xd7\xa1\xd7\x9a \*(.*?)\r\n\* \xe2\x82\xaa \xd7\x91\xd7\x9e\xd7\xa1\xd7\xa2\xd7\x93\xd7\xaa (.*?)\.\r\n"

def get_mails_from(email_address, password, fromwho):
    mailbox = imaplib.IMAP4_SSL('imap.gmail.com')
    mailbox.login(email_address, password)
    mailbox.select('"[Gmail]/All Mail"')

    result, data = mailbox.search(None, '(FROM "{}")'.format(fromwho))

    for mail_id in data[0].split():
        status, data = mailbox.fetch(mail_id, "(RFC822)")
        mail = email.message_from_string(data[0][1])
        yield mail

def parse_subject(mail):
    return email.Header.decode_header(mail['subject'])[0][0]

def parse_cibus_mails(mails):
    for mail in mails:
        subject = parse_subject(mail)
        if not subject.startswith(CIBUS_SUBJECT_PREIFX):
            continue
        subject = subject[len(CIBUS_SUBJECT_PREIFX):]
        place, nis = subject.split(' NIS ')
        place = ' - '.join([part.strip() for part in place.split('-')])
        yield place, nis

def parse_10bis_mails(mails):
    for mail in mails:
        subject = parse_subject(mail)
        if not subject.startswith(TENBIS_SUBJECT_PREFIX):
            continue
        mail_body = mail.get_payload().decode("base64")
        matchobj = re.search(TENBIS_BODY_PATTERN, mail_body)
        if matchobj is not None:
            place, nis = matchobj.groups()
            yield place, nis

def group_by_places(items):
    prices = dict()
    for place, nis in items:
        prices.setdefault(place, list()).append(float(nis))
    for place, pricelist in prices.items():
        average = sum(pricelist) / len(pricelist)
        yield place, average, len(pricelist)

def extract(email_address, password, fromwho, parser, output_file):
    mails = get_mails_from(email_address, password, fromwho)
    items = parser(mails)
    items = sorted(group_by_places(items), key=lambda x: x[1])
    if len(items) > 0:
        with open(output_file, "wb") as fd:
            fd.writelines(['{} {:.2f} {}\n'.format(*item) for item in items])

def main():
    import sys
    _, email_address, password = sys.argv
    extract(email_address, password, "cibus", parse_cibus_mails, "cibus.txt")
    extract(email_address, password, "10bis", parse_10bis_mails, "10bis.txt")

if __name__ == '__main__':
    main()
