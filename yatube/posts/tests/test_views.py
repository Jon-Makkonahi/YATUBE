import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post, User

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
FOLLOW_INDEX_URL = reverse('posts:follow_index')
FOLLOW_URL = reverse('posts:profile_follow', args=[USERNAME2])
UNFOLLOW_URL = reverse('posts:profile_unfollow', args=[USERNAME2])
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.user2 = User.objects.create_user(username=USERNAME2)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client2 = Client()
        cls.authorized_client2.force_login(cls.user2)
        cls.group = Group.objects.create(
            title='Тест заголовок',
            slug=SLUG,
            description='Тест описание',
        )
        cls.group2 = Group.objects.create(
            title='Тест заголовок',
            slug=SLUG2,
            description='Тест описание',
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тест текст',
            author=cls.user2,
            group=cls.group,
            image=uploaded,
        )
        cls.POST_URL = reverse('posts:post_detail', args=[cls.post.pk])
        cls.EDIT_URL = reverse('posts:post_edit', args=[cls.post.pk])
        Follow.objects.create(user=cls.user, author=cls.user2)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_main_context(self):
        addresses = [
            HOME_URL,
            PROFILE_URL2,
            self.POST_URL,
            GROUP_URL,
            FOLLOW_INDEX_URL,
        ]
        for address in addresses:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                if address == self.POST_URL:
                    post = response.context['post']
                else:
                    self.assertEqual(len(response.context['page_obj']), 1)
                    post = response.context['page_obj'][0]
                self.assertEqual(post.text, self.post.text)
                self.assertEqual(post.author, self.post.author)
                self.assertEqual(post.group, self.post.group)
                self.assertEqual(post.image, self.post.image)

    def test_paginator(self):
        for post in range(settings.POSTS_QUANTITY):
            Post.objects.create(
                author=self.user2,
                group=self.group,
                text='text'
            )
        pages_for_paginator = [
            HOME_URL,
            GROUP_URL,
            PROFILE_URL2,
            FOLLOW_INDEX_URL
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
        response = self.authorized_client2.get(PROFILE_URL)
        self.assertEqual(response.context['author'], self.user)

    def test_fixtures_group(self):
        response = self.authorized_client.get(GROUP_URL)
        group = response.context['group']
        self.assertEqual(group.slug, self.group.slug)
        self.assertEqual(group.title, self.group.title)
        self.assertEqual(group.description, self.group.description)

    def test_follow(self):
        Follow.objects.all().delete()
        follow_count = Follow.objects.count()
        self.authorized_client.get(FOLLOW_URL)
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertTrue(
            Follow.objects.filter(user=self.user, author=self.user2).exists()
        )
    
    def test_unfollow(self):
        follow_count = Follow.objects.count()
        self.assertTrue(
            Follow.objects.filter(user=self.user, author=self.user2).exists()
        )
        self.authorized_client.get(UNFOLLOW_URL)
        self.assertEqual(Follow.objects.count(), follow_count - 1)

    def test_cache(self):
        page = self.authorized_client.get(HOME_URL).content
        Post.objects.create(
            text='text', author=self.user, group=self.group
        )
        self.assertEqual(
            page, self.authorized_client.get(HOME_URL).content)
        cache.clear()
        self.assertNotEqual(
            page, self.authorized_client.get(HOME_URL).content)
