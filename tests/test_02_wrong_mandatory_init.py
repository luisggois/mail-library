import unittest
import Mailer


class TestWrongMandatoryInit(unittest.TestCase):

    # no mandatory fields at all
    @unittest.expectedFailure
    def test_init01(self):
        Mailer.Mailer()

    # host missing
    @unittest.expectedFailure
    def test_init02(self):
        Mailer.Mailer(
            auth='login',
            port=25
        )

    # port missing
    @unittest.expectedFailure
    def test_init03(self):
        Mailer.Mailer(
            auth='login',
            host='10.1.10.99',
        )

    # empty port
    @unittest.expectedFailure
    def test_init04(self):
        Mailer.Mailer(
            auth='login',
            host='10.1.10.99',
            port=None
        )

    # empty port
    @unittest.expectedFailure
    def test_init05(self):
        Mailer.Mailer(
            auth='login',
            host='10.1.10.99',
            port=''
        )

    # empty host
    @unittest.expectedFailure
    def test_init06(self):
        Mailer.Mailer(
            auth='login',
            host=None,
            port=25
        )

    # empty host
    @unittest.expectedFailure
    def test_init07(self):
        Mailer.Mailer(
            auth='login',
            host='',
            port=25
        )

    # empty auth method
    @unittest.expectedFailure
    def test_init8(self):
        Mailer.Mailer(
            auth='',
            host='10.1.10.99',
            port=25
        )

    # incorrect auth method
    @unittest.expectedFailure
    def test_init9(self):
        Mailer.Mailer(
            auth='gssapi',
            host='10.1.10.99',
            port=25
        )


if __name__ == '__main__':
    unittest.main()
