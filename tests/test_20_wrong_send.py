import unittest
import Mailer


class TestWrongSend(unittest.TestCase):

    def setUp(self) -> None:
        self.mailer = Mailer.Mailer(
            auth='login',
            host='127.0.0.2',
            port=4242
        )
        self.mailer.add_to('mail1@domain.tld')
        self.mailer.add_from('mail2@domain.tld')

    # unable to connecto to a smtp
    @unittest.expectedFailure
    def test_send01(self):
        self.mailer.send()


if __name__ == '__main__':
    unittest.main()
