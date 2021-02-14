from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class UrlTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

        self.user_1 = User.objects.create_user(username='Mike1')
        self.authorized_client_1 = Client()
        self.authorized_client_1.force_login(self.user_1)

        self.user_2 = User.objects.create_user(username='Mike2')
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)

        self.test_group = Group.objects.create(
            title = "Тестова группа",
            slug = "slag",
            description = "Тестовое описание"
        )
        self.test_post = Post.objects.create(
            text = "Тестовый пост",
            author = self.user_1,
            group = self.test_group
        )
    """Страницы c доступом для неавторизованного пользователя"""
    def test_urls_allowed_guests(self):
        urls = [
            reverse('index'),
            reverse('about:author'),
            reverse('about:tech'),
            reverse('post', args=[self.user_1, self.test_post.id]),
            reverse('group_posts', args=['slag']),
            reverse('profile', args=[self.user_1]),
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    """Страницы без доступа для неавторизованного пользователя"""
    def test_urls_forbidden_guests(self):
        urls = [
            reverse('new_post'),
            reverse('post_edit', args=[self.user_1, self.test_post.id])
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                redir = f'/auth/login/?next={url}'
                self.assertRedirects(response, redir)

    def test_urls_allowed_for_users(self):
        """Страницы для авторизованного пользователя."""
        urls = [
            reverse('new_post'),
            reverse('post_edit', args=[self.user_1, self.test_post.id]),
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client_1.get(url)
                self.assertEqual(response.status_code, 200)
                
