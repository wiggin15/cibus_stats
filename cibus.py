import imaplib
import email

# prefix = "ishur iska al sach -"
prefix = '\xd7\x90\xd7\x99\xd7\xa9\xd7\x95\xd7\xa8 \xd7\xa2\xd7\xa1\xd7\xa7\xd7\x94 \xd7\xa2\xd7\x9c \xd7\xa1\xd7\x9a -'

def get_mails_from(username, passw, fromwho):
    mailbox = imaplib.IMAP4_SSL('imap.gmail.com')
    mailbox.login(username, passw)
    mailbox.select('"[Gmail]/All Mail"')
    
    result, data = mailbox.search(None, '(FROM "{}")'.format(fromwho))
    
    for mail_id in data[0].split():
        status, data = mailbox.fetch(mail_id, "(RFC822)")
        mail = email.message_from_string(data[0][1])
        yield mail
        
def get_cibus_subjects(mails):
    for mail in mails:
        subject = email.Header.decode_header(mail['subject'])[0][0]

        if not subject.startswith(prefix):
            continue
        
        yield subject[len(prefix):]

def get_prices_from_subjects(subjects):
    prices = dict()
    for subject in subjects:
        place, nis = subject.split(' NIS ')
        place = ' - '.join([part.strip() for part in place.split('-')])
        prices.setdefault(place, list()).append(float(nis))
    for place, pricelist in prices.items():
        average = sum(pricelist) / len(pricelist)
        yield place, average, len(pricelist)


def main():
    import sys
    _, username, passw = sys.argv
    mails = get_mails_from(username, passw, "Cibus")
    subjects = list(get_cibus_subjects(mails))
    items = sorted(get_prices_from_subjects(subjects), key=lambda x: x[1])
    open("cibus.txt", "wb").writelines(['{} {:.2f} {}\n'.format(*item) for item in items])
    
if __name__ == '__main__':
    main()