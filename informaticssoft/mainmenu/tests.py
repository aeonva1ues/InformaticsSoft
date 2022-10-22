from django.test import TestCase, Client


class StaticUrlTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_mainmenu(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_faqpage(self):
        response = self.client.get('/FAQ/terms/')
        self.assertEqual(
            response.status_code,
            200,
            'Верный адрес не вернул код 200: {}'.format(response.status_code))
        response = self.client.get('/FAQ/Test/')
        self.assertEqual(
            response.status_code,
            404,
            'Неверный адрес не вернул код 404')
        response = self.client.get('/FAQ/')
        self.assertEqual(
            response.status_code,
            404,
            'Неверный адрес не вернул код 404')
