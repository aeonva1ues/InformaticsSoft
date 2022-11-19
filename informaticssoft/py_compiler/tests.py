from django.test import TestCase, Client


class StaticUrlTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_code_editor_page(self):
        response = self.client.get('/code-editor/')
        self.assertEqual(
            response.status_code,
            200,
            f'Главная страница редактора выдает код: {response.status_code}'
        )

    def test_code_input_page(self):
        response = self.client.get('/code-editor/input/')
        self.assertEqual(
            response.status_code,
            301,
            'Редирект на страницу редактора не произошел'
        )
        session = self.client.session
        session['inputs_lines'] = [
            {
                'code_line': 'a = input()\r',
                'line_index': 0
            }
            ]
        session.save()
        response = self.client.get('/code-editor/input/')
        self.assertEqual(
            response.status_code,
            200,
            f'Страница с вводом данных вернула код: {response.status_code}'
        )

    def test_manual_page(self):
        response = self.client.get('/manual/')
        self.assertEqual(
            response.status_code,
            200,
            f'Страница с мануалом не открылась. Код: {response.status_code}'
        )

    def test_contacts_page(self):
        response = self.client.get('/contacts/')
        self.assertEqual(
            response.status_code,
            200,
            (
                'Страница для обратной связи не открылась.'
                f' Код: {response.status_code}'
            )
        )

    def test_example_page(self):
        response = self.client.get('/examples/')
        self.assertEqual(
            response.status_code,
            200,
            f'Страница с примерами не открылась. Код: {response.status_code}'
        )
