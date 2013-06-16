import imaplib
import email

# prefix = "ishur iska al sach -"
prefix = '\xd7\x90\xd7\x99\xd7\xa9\xd7\x95\xd7\xa8 \xd7\xa2\xd7\xa1\xd7\xa7\xd7\x94 \xd7\xa2\xd7\x9c \xd7\xa1\xd7\x9a -'

def get_mails_from(email_address, password, fromwho):
    mailbox = imaplib.IMAP4_SSL('imap.gmail.com')
    mailbox.login(email_address, password)
    mailbox.select('"[Gmail]/All Mail"')

    result, data = mailbox.search(None, '(FROM "{}")'.format(fromwho))

    for mail_id in data[0].split():
        status, data = mailbox.fetch(mail_id, "(RFC822)")
        mail = email.message_from_string(data[0][1])
        yield mail

def get_cibus_subjects(mails):
    for mail in mails:
        subject = email.Header.decode_header(mail['subject'])[0][0]
        if subject.startswith(prefix):
            yield subject[len(prefix):]

def parse_subjects(subjects):
    """ extracts the restaurant name and its price from the mail subject """
    for subject in subjects:
        place, nis = subject.split(' NIS ')
        place = ' - '.join([part.strip() for part in place.split('-')])
        yield place, nis

def group_by_places(items):
    prices = dict()
    for place, nis in items:
        prices.setdefault(place, list()).append(float(nis))
    for place, pricelist in prices.items():
        average = sum(pricelist) / len(pricelist)
        yield place, average, len(pricelist)

def main():
    import sys
    _, email_address, password = sys.argv
    mails = get_mails_from(email_address, password, "Cibus")
    subjects = get_cibus_subjects(mails)
    items = parse_subjects(subjects)
    items = sorted(group_by_places(items), key=lambda x: x[1])
    open("cibus.txt", "wb").writelines(['{} {:.2f} {}\n'.format(*item) for item in items])

if __name__ == '__main__':
    main()
