import unittest
import Mailer


class TestWrongInit(unittest.TestCase):

    # empty hostname
    @unittest.expectedFailure
    def test_init01(self):
        Mailer.Mailer(
            auth='login',
            host=None,
            port=25
        )

    # incorrect IP-address
    @unittest.expectedFailure
    def test_init02(self):
        Mailer.Mailer(
            auth='login',
            host='10.1.10.999',
            port=25
        )

    # port smaller than 1
    @unittest.expectedFailure
    def test_init03(self):
        Mailer.Mailer(
            auth='login',
            host='10.1.10.99',
            port=0
        )

    # port bigger that 65535
    @unittest.expectedFailure
    def test_init04(self):
        Mailer.Mailer(
            auth='login',
            host='10.1.10.99',
            port=10241024
        )

    # No credentials
    @unittest.expectedFailure
    def test_init05(self):
        Mailer.Mailer(
            auth='ntlm',
            host='127.0.0.2',
            port=587
        )

    # username without dmain
    @unittest.expectedFailure
    def test_init06(self):
        Mailer.Mailer(
            auth='ntlm',
            host='127.0.0.2',
            username='admin',
            password='12345',
            port=587
        )


if __name__ == '__main__':
    unittest.main()
