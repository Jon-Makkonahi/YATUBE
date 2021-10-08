import shutil
import tempfile

from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, User


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

SLUG = 'test-slug'
USERNAME = 'Joshua'

HOME_URL = reverse('posts:index')
CREATE_URL = reverse('posts:post_create')
GROUP_URL = reverse('posts:group_list', args=[SLUG])
PROFILE_URL = reverse('posts:profile', args=[USERNAME])

HOME_URL2 = '/'
GROUP_URL2 = f'/group/{SLUG}/'
PROFILE_URL2  = f'/profile/{USERNAME}/'
CREATE_URL2 = '/create/'

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsROUTERSTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug=SLUG
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='text'
        )
        cls.POST_URL = reverse('posts:post_detail', args=[cls.post.pk])
        cls.EDIT_URL = reverse('posts:post_edit', args=[cls.post.pk])
        cls.POST_URL2 = f'/posts/{ cls.post.pk }/' 
        cls.EDIT_URL2 = f'/posts/{ cls.post.pk }/edit/'

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_routers_pages(self):
        cases = [
            [HOME_URL, HOME_URL2],
            [GROUP_URL, GROUP_URL2],
            [PROFILE_URL, PROFILE_URL2],
            [self.POST_URL, self.POST_URL2],
            [self.EDIT_URL, self.EDIT_URL2],
            [CREATE_URL, CREATE_URL2],
        ]
        for urlname, url in cases:
            with self.subTest(urlname=urlname):
                self.assertEqual(urlname, url)