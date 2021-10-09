from django.test import TestCase
from django.urls import reverse

from ..models import Group, Post, User


SLUG = 'test-slug'
USERNAME = 'Joshua'

HOME_URL = reverse('posts:index')
CREATE_URL = reverse('posts:post_create')
GROUP_URL = reverse('posts:group_list', args=[SLUG])
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
FOLLOW_URL = reverse('posts:follow_index')
LOGIN_URL = reverse('users:login')
REDIRECT_CREATE_URL = (LOGIN_URL + '?next=' + CREATE_URL)

HOME_URL2 = '/'
GROUP_URL2 = f'/group/{SLUG}/'
PROFILE_URL2 = f'/profile/{USERNAME}/'
CREATE_URL2 = '/create/'
FOLLOW_URL2 = '/follow/'
REDIRECT_CREATE_URL2 = '/auth/login/?next=/create/'


class PostsRoutersTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            slug=SLUG
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='text'
        )
        cls.POST_URL = reverse('posts:post_detail', args=[cls.post.pk])
        cls.EDIT_URL = reverse('posts:post_edit', args=[cls.post.pk])
        cls.REDIRECT_EDIT_URL = (LOGIN_URL + '?next=' + cls.EDIT_URL)
        cls.POST_URL2 = f'/posts/{ cls.post.pk }/'
        cls.EDIT_URL2 = f'/posts/{ cls.post.pk }/edit/'

    def test_routers_pages(self):
        cases = [
            [HOME_URL, HOME_URL2],
            [GROUP_URL, GROUP_URL2],
            [PROFILE_URL, PROFILE_URL2],
            [self.POST_URL, self.POST_URL2],
            [self.EDIT_URL, self.EDIT_URL2],
            [CREATE_URL, CREATE_URL2],
            [FOLLOW_URL, FOLLOW_URL2],
            [REDIRECT_CREATE_URL, REDIRECT_CREATE_URL2],

        ]
        for urlname, url in cases:
            with self.subTest(urlname=urlname):
                self.assertEqual(urlname, url)
