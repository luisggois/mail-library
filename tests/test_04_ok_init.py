import unittest
import Mailer


class TestOkInit(unittest.TestCase):

    def test_init01(self):
        Mailer.Mailer(
            auth='login',
            host='127.0.0.2',
            port=25
        )

    def test_init02(self):
        Mailer.Mailer(
            auth='login',
            host='127.0.0.2',
            port=25,
            asdasd='randomstuff'
        )

    def test_init03(self):
        Mailer.Mailer(
            auth=None,
            host='127.0.0.1',
            port=25
        )

    def test_init04(self):
        Mailer.Mailer(
            auth='ntlm',
            host='127.0.0.2',
            username=r'domain\admin',
            password='12345',
            port=587
        )

    def test_init05(self):
        Mailer.Mailer(
            auth='ntlm',
            host='127.0.0.2',
            username='domain\\admin',
            password='12345',
            port=587
        )


if __name__ == '__main__':
    unittest.main()
