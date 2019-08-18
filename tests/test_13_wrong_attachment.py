import unittest
import Mailer


# noinspection PyTypeChecker
class TestWrongAttachment(unittest.TestCase):

    def setUp(self) -> None:
        self.mailer = Mailer.Mailer(
            auth='login',
            host='127.0.0.2',
            port=25
        )

    # inexisting file to attach
    @unittest.expectedFailure
    def test_attach01(self):
        self.mailer.add_attachment('asdasd.txt')

    # two files with the same name
    @unittest.expectedFailure
    def test_attach02(self):
        self.mailer.add_attachment(__file__)
        self.mailer.add_attachment(__file__)


if __name__ == '__main__':
    unittest.main()
