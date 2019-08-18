import unittest
import Mailer


# noinspection PyTypeChecker
class TestWrongHeaders(unittest.TestCase):

    def setUp(self) -> None:
        self.mailer = Mailer.Mailer(
            auth='login',
            host='127.0.0.2',
            port=25
        )

    # malformed email From
    @unittest.expectedFailure
    def test_header01(self):
        self.mailer.add_from('asdasd')

    # only single email address allowed in From
    @unittest.expectedFailure
    def test_header02(self):
        self.mailer.add_from('mail1@domain.tld, mail2@domain.tld')

    # empty email From
    @unittest.expectedFailure
    def test_header03(self):
        self.mailer.add_from(None)

    # malformed email To
    @unittest.expectedFailure
    def test_header04(self):
        self.mailer.add_to(None)

    # malformed email To
    @unittest.expectedFailure
    def test_header05(self):
        self.mailer.add_to('asdasd')

    # empty email CC
    @unittest.expectedFailure
    def test_header06(self):
        self.mailer.add_cc(None)

    # malformed email CC
    @unittest.expectedFailure
    def test_header07(self):
        self.mailer.add_cc('asdasd')


if __name__ == '__main__':
    unittest.main()
