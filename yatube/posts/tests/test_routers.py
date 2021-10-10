from django.test import TestCase
from django.urls import reverse

from ..models import Post, User


SLUG = 'test-slug'
USERNAME = 'Joshua'

HOME_URL = reverse('posts:index')
CREATE_URL = reverse('posts:post_create')
GROUP_URL = reverse('posts:group_list', args=[SLUG])
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
FOLLOW_INDEX_URL = reverse('posts:follow_index')
FOLLOW_URL = reverse('posts:profile_follow', args=[USERNAME])
UNFOLLOW_URL = reverse('posts:profile_unfollow', args=[USERNAME])

HOME_URL2 = '/'
GROUP_URL2 = f'/group/{SLUG}/'
PROFILE_URL2 = f'/profile/{USERNAME}/'
FOLLOW_URL2 = f'/profile/{USERNAME}/follow/'
UNFOLLOW_URL2 = f'/profile/{USERNAME}/unfollow/'
CREATE_URL2 = '/create/'
FOLLOW_INDEX_URL2 = '/follow/'


class PostsRoutersTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.post = Post.objects.create(
            author=cls.user,
            text='text'
        )

    def test_routers_pages(self):
        POST_URL = reverse('posts:post_detail', args=[self.post.pk])
        EDIT_URL = reverse('posts:post_edit', args=[self.post.pk])
        POST_URL2 = f'/posts/{ self.post.pk }/'
        EDIT_URL2 = f'/posts/{ self.post.pk }/edit/'
        cases = [
            [HOME_URL, HOME_URL2],
            [GROUP_URL, GROUP_URL2],
            [PROFILE_URL, PROFILE_URL2],
            [POST_URL, POST_URL2],
            [EDIT_URL, EDIT_URL2],
            [CREATE_URL, CREATE_URL2],
            [FOLLOW_INDEX_URL, FOLLOW_INDEX_URL2],
            [FOLLOW_URL, FOLLOW_URL2],
            [UNFOLLOW_URL, UNFOLLOW_URL2],
        ]
        for urlname, url in cases:
            with self.subTest(urlname=urlname):
                self.assertEqual(urlname, url)
