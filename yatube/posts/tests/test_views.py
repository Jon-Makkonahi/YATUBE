import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, User, Comment


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

SLUG = 'test-slug'
SLUG2 = 'test-slug-2'
SLUG3 = 'test-slug-3'
USERNAME = 'Joshua'
USERNAME2 = 'Jony'

HOME_URL = reverse('posts:index')
CREATE_URL = reverse('posts:post_create')
GROUP_URL = reverse('posts:group_list', args=[SLUG])
GROUP_URL2 = reverse('posts:group_list', args=[SLUG2])
GROUP_URL3 = reverse('posts:group_list', args=[SLUG3])
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
PROFILE_URL2 = reverse('posts:profile', args=[USERNAME2])


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug=SLUG
        )
        cls.group2 = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug=SLUG2
        )
        cls.group3 = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug=SLUG3
        )
        cls.user = User.objects.create_user(username=USERNAME)
        cls.user2 = User.objects.create_user(username=USERNAME2)
        cls.small_gif = (         
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='text',
            image=cls.uploaded
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            post=cls.post,
            text='comments'
        )
        cls.POST_URL = reverse('posts:post_detail', args=[cls.post.pk])
        cls.EDIT_URL = reverse('posts:post_edit', args=[cls.post.pk])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_main_context(self):
        addresses = [
            HOME_URL,
            self.POST_URL,
            PROFILE_URL,
            GROUP_URL
        ]
        for address in addresses:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                if address == self.POST_URL:
                    post = response.context['post']
                else:
                    self.assertEqual(len(response.context['page_obj']), 1)
                    post = response.context['page_obj'][0]
                self.assertEqual(post.author, self.post.author)
                self.assertEqual(post.group, self.post.group)
                self.assertEqual(post.text, self.post.text)
                self.assertTrue(post.image, self.post.image)

    def test_paginator(self):
        for post in range(settings.POSTS_QUANTITY):
            Post.objects.create(
                author=self.user2,
                group=self.group3,
                text='text'
            )
        pages_for_paginator = [
            HOME_URL,
            GROUP_URL3,
            PROFILE_URL2,
        ]
        for page in pages_for_paginator:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertEqual(
                    len(response.context['page_obj']),
                    settings.POSTS_QUANTITY
                )

    def test_post_not_in_group(self):
        response = self.authorized_client.get(GROUP_URL2)
        self.assertNotIn(self.post, response.context['page_obj'])

    def test_fixtures_profile(self):
        response = self.authorized_client.get(PROFILE_URL)
        self.assertEqual(response.context['author'], self.user)

    def test_fixtures_profile(self):
        response = self.authorized_client.get(PROFILE_URL)
        self.assertEqual(response.context['author'], self.user)

    def test_fixtures_group(self):
        response = self.authorized_client.get(GROUP_URL)
        group = response.context['group']
        self.assertEqual(group.slug, self.group.slug)
        self.assertEqual(group.title, self.group.title)
        self.assertEqual(group.description, self.group.description)

    def test_add_comment(self):
        response = self.authorized_client.get(self.POST_URL)
        post = response.context['comments'][0]
        self.assertEqual(post, self.comment)

    def test_cache(self):
        posts_count = Post.objects.count()
        response = self.authorized_client.get(HOME_URL).content
        Post.objects.create(
            text='text', author=self.user, group=self.group
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(
            response, self.authorized_client.get(HOME_URL).content)
        cache.clear()
        self.assertNotEqual(
            response, self.authorized_client.get(HOME_URL).content)
