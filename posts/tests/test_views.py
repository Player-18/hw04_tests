from django import forms
from django.contrib.auth import get_user_model
from django.http import response
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class ViewPageContextTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        

    def setUp(self):
        self.guest_client = Client()

        self.user_1 = User.objects.create_user(username='user1')
        self.user_1_client = Client()
        self.user_1_client.force_login(self.user_1)
        
        self.user_2 = User.objects.create_user(username='user2')
        self.user_2_client = Client()
        self.user_2_client.force_login(self.user_2)

        self.test_group_1 = Group.objects.create(
            title = 'Тестовая группа',
            slug = 'slug',
            description = 'Тестовое описание',
        )
        self.test_group_2 = Group.objects.create(
            title = 'Тестовая группа 2',
            slug = 'slug-2',
            description = 'Тестовое описание 2',
        )

        self.test_post = Post.objects.create(
            text = 'Тестовый текст',
            author = self.user_1,
            group = self.test_group_1,
        )

    def test_pages_uses_correct_template(self):
        """Соответсвие вызываемых шаблонов"""
        user = self.user_1
        post_id = self.test_post.id
        templates_pages_names = {
            reverse('index'): 'index.html',
            reverse('new_post'): 'new.html', 
            reverse('group_posts', args=['slug']): 'group.html',
            reverse('post_edit', args=[user, post_id]): 'new_post.html',
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',

        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest():
                response = self.user_1_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_context(self):
        response = self.user_1_client.get(reverse('index'))
        cont = self.test_post
        self.assertEqual(response.context['page'][0], cont)

    def test_group_context(self):
        url = reverse("group_posts", args=["slug"])
        response = self.user_1_client.get(url)
        cont = self.test_group_1
        self.assertEqual(response.context['group'], cont)

    def test_new_post_context(self):
        fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }

        response = self.user_1_client.get(reverse('new_post'))
        form = response.context['form']

        for field, expected in fields.items():
            with self.subTest(field=field):
                self.assertIsInstance(form.fields[field], expected)
    
    def test_post_edit_context(self):
        url = reverse('post_edit', args=[self.user_1, self.test_post.id])
        response = self.user_1_client.get(url)
        form = response.context['form']

        context = {
            'post': self.test_post,
            'is_edit': True,
        }

        for value, expected in context.items():
            with self.subTest(value=value):
                self.assertEqual(response.context[value], expected)

        fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }

        for field, expected in fields.items():
            with self.subTest(field=field):
                self.assertIsInstance(form.fields[field], expected)
    
    def test_profile_context(self):
        user = self.user_1
        url = reverse('profile', args=[user])
        response = self.user_1_client.get(url)

        context = {
            'author': user
        }

        for key, val in context.items():
            with self.subTest(key=key):
                self.assertEqual(response.context[key], val)

    def test_post_view_context(self):
        url = reverse('post', args=[self.user_1, self.test_post.id])
        response = self.user_1_client.get(url)

        context = {
            'post': self.test_post,
            'author': self.user_1
        }

        for key, val in context.items():
            with self.subTest(key=key):
                self.assertEqual(response.context[key], val)
    
    def test_group_post(self):
        response = self.user_1_client.get(reverse('group_posts', args=['slug']))
        cont = self.test_post
        self.assertEqual(response.context['page'][0], cont)
    
    def test_another_group_post(self):
        response = self.user_1_client.get(reverse('group_posts', args=['slug-2']))
        cont = self.test_post
        self.assertIsNot(cont, response.context['page'])
        