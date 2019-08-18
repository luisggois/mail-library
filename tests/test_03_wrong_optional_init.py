import unittest
import Mailer


class TestWrongOptionalInit(unittest.TestCase):

    # password mentioned, but empty
    @unittest.expectedFailure
    def test_init01(self):
        Mailer.Mailer(
            auth='login',
            host='localhost',
            port=25,
            password=None
        )

    # password mentioned, but empty
    @unittest.expectedFailure
    def test_init02(self):
        Mailer.Mailer(
            auth='login',
            host='localhost',
            port=25,
            password=''
        )

    # password given, but no username
    @unittest.expectedFailure
    def test_init03(self):
        Mailer.Mailer(
            auth='login',
            host='localhost',
            port=25,
            password='sdkfj',
            username=None
        )

    # password given, but no username
    @unittest.expectedFailure
    def test_init04(self):
        Mailer.Mailer(
            auth='login',
            host='localhost',
            port=25,
            password='sdkfj',
            username=''
        )

    # password given, but no username
    @unittest.expectedFailure
    def test_init05(self):
        Mailer.Mailer(
            auth='login',
            host='localhost',
            port=25,
            password='sdkfj',
        )

    # username given, but no password
    @unittest.expectedFailure
    def test_init06(self):
        Mailer.Mailer(
            auth='login',
            host='localhost',
            port=25,
            username='sdkfj',
        )


if __name__ == '__main__':
    unittest.main()
