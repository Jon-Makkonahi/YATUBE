import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Post, Group, User


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

SLUG = 'test-slug'
SLUG2 = 'test-slug-2'
SLUG3 = 'test-slug-3'
USERNAME = 'Joshua'
USERNAME2 = 'Jony'
TEXT = 'Текстовый текст'
TEXT2 = 'Текстовый текст 2'

HOME_URL = reverse('posts:index')
CREATE_URL = reverse('posts:post_create')
GROUP_URL = reverse('posts:group_list', args=[SLUG])
PROFILE_URL = reverse('posts:profile', args=[USERNAME])


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug=SLUG
        )
        cls.group2 = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug=SLUG2
        )
        cls.group3 = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug=SLUG3
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text=TEXT
        )
        cls.post2 = Post.objects.create(
            author=cls.user,
            group=cls.group3,
            text=TEXT2
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

    def test_create_post(self):
        Post.objects.all().delete()
        posts_count = Post.objects.count()
        small_gif = (          
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': TEXT,
            'group': self.group2.id,
            'image': uploaded
        }
        response = self.authorized_client.post(
            CREATE_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, PROFILE_URL)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.all()[0]
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group.id, form_data['group'])

    def test_post_edit(self):
        small_gif = (     
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': TEXT2,
            'group': self.group3.id,
            'image': uploaded
        }
        response = self.authorized_client.post(
            self.EDIT_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.POST_URL)
        post = response.context['post']
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group.id, form_data['group'])
