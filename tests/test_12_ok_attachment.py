import unittest
import Mailer


# noinspection PyTypeChecker
class TestOkAttachment(unittest.TestCase):

    def setUp(self) -> None:
        self.mailer = Mailer.Mailer(
            auth='login',
            host='127.0.0.2',
            port=25
        )

    def test_attach01(self):
        self.mailer.add_attachment(__file__)

    def test_attach02(self):
        self.mailer.add_attachment("test_02_wrong_mandatory_init.py")
        self.mailer.add_attachment("test_01_wrong_init.py")


if __name__ == '__main__':
    unittest.main()
