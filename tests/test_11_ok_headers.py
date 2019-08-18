import unittest
import Mailer


# noinspection PyTypeChecker
class TestOkHeaders(unittest.TestCase):

    def setUp(self) -> None:
        self.mailer = Mailer.Mailer(
            auth='login',
            host='127.0.0.2',
            port=25
        )

    def test_header01(self):
        self.mailer.add_from('mail@domain.tld')

    def test_header02(self):
        self.mailer.add_to('mail1@domain.tld, mail2@domain.tld')
        self.mailer.add_to(['mail1@domain.tld', 'mail2@domain.tld'])

    def test_header03(self):
        self.mailer.add_cc('mail1@domain.tld, mail2@domain.tld')
        self.mailer.add_cc(['mail1@domain.tld', 'mail2@domain.tld'])

    def test_header04(self):
        self.mailer.add_subject('kjaksjhda')
        self.mailer.add_subject('')
        self.mailer.add_subject(None)

    def test_header05(self):
        self.mailer.add_text(None)
        self.mailer.add_text('')
        self.mailer.add_text('lkjsldkjf')
        self.mailer.add_text('<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Title</title></head><body></body></html>')

    def test_header06(self):
        self.mailer.add_to('mail1@domain.tld; mail2@domain.tld')
        self.mailer.add_cc('mail1@domain.tld; mail2@domain.tld')

    def test_header07(self):
        self.mailer.add_to('mail1@domain.tld;mail2@domain.tld')
        self.mailer.add_cc('mail1@domain.tld;mail2@domain.tld')

    def test_header08(self):
        self.mailer.add_to('mail1@domain.tld;mail2@domain.tld,mail3@domain.tld')
        self.mailer.add_cc('mail1@domain.tld;mail2@domain.tld,mail3@domain.tld')


if __name__ == '__main__':
    unittest.main()
