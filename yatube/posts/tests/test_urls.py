import shutil
import tempfile

from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, User


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

SLUG = 'test-slug'
SLUG2 = 'test-slug-2'
USERNAME = 'Joshua'
USERNAME2 = 'Jony'

HOME_URL = reverse('posts:index')
CREATE_URL = reverse('posts:post_create')
GROUP_URL = reverse('posts:group_list', args=[SLUG])
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
FOLLOW_URL = reverse('posts:follow_index')
UNEXISTING_PAGE_URL = 'pythondeveloper/best/'
LOGIN_URL = reverse('users:login')
REDIRECT_CREATE_URL = (LOGIN_URL + '?next=' + CREATE_URL)
REDIRECT_FOLLOW_URL = (LOGIN_URL + '?next=' + FOLLOW_URL)

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_one = User.objects.create_user(username=USERNAME)
        cls.user_two = User.objects.create_user(username=USERNAME2)
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug=SLUG
        )
        cls.post = Post.objects.create(
            author=cls.user_two,
            group=cls.group,
            text='text'
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user_one)
        cls.authorized_client2 = Client()
        cls.authorized_client2.force_login(cls.user_two)
        
        cls.POST_URL = reverse('posts:post_detail', args=[cls.post.pk])
        cls.EDIT_URL = reverse('posts:post_edit', args=[cls.post.pk])
        cls.REDIRECT_EDIT_URL = (LOGIN_URL + '?next=' + cls.EDIT_URL)

        
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_url_pages(self):
        cases = [
            [HOME_URL, self.guest_client, 200],
            [GROUP_URL, self.guest_client, 200],
            [PROFILE_URL, self.guest_client, 200],
            [self.POST_URL, self.guest_client, 200],
            [self.EDIT_URL, self.authorized_client2, 200],
            [CREATE_URL, self.authorized_client, 200],
            [UNEXISTING_PAGE_URL, self.guest_client, 404],
            [CREATE_URL, self.guest_client, 302],
            [self.EDIT_URL, self.authorized_client, 302],
            [self.EDIT_URL, self.guest_client, 302],
            [FOLLOW_URL, self.authorized_client, 200],
            [FOLLOW_URL, self.guest_client, 302],
        ]
        for url, client, code in cases:
            with self.subTest(url=url, client=client, code=code):
                self.assertEqual(client.get(url).status_code, code)

    def test_template_pages(self):
        cases = [
            [HOME_URL, self.guest_client, 'posts/index.html'],
            [GROUP_URL, self.guest_client, 'posts/group_list.html'],
            [PROFILE_URL, self.guest_client, 'posts/profile.html'],
            [self.POST_URL, self.guest_client, 'posts/post_detail.html'],
            [self.EDIT_URL, self.authorized_client2, 'posts/create_post.html'],
            [CREATE_URL, self.authorized_client, 'posts/create_post.html'],
            [UNEXISTING_PAGE_URL, self.guest_client, 'core/404.html'],
            [FOLLOW_URL, self.authorized_client, 'posts/follow.html']
        ]
        for url, client, template in cases:
            with self.subTest(url=url):
                self.assertTemplateUsed(client.get(url), template)

    def test_redirect_pages(self):
        cases = [
            [CREATE_URL, True, self.guest_client, REDIRECT_CREATE_URL],
            [self.EDIT_URL, True, self.authorized_client, HOME_URL],
            [self.EDIT_URL, True, self.guest_client, self.REDIRECT_EDIT_URL],
            [FOLLOW_URL, True, self.guest_client, REDIRECT_FOLLOW_URL],
        ]
        for url, follow, client, redirect in cases:
            with self.subTest(url=url, client=client, redirect=redirect):
                self.assertRedirects(client.get(url, follow=follow), redirect)
