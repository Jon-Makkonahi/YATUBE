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
COMMENT = 'Комментарий'

HOME_URL = reverse('posts:index')
CREATE_URL = reverse('posts:post_create')
GROUP_URL = reverse('posts:group_list', args=[SLUG])
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
LOGIN_URL = reverse('users:login')
REDIRECT_CREATE_URL = (LOGIN_URL + '?next=' + CREATE_URL)

SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.user2 = User.objects.create_user(username=USERNAME2)
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client2 = Client()
        cls.authorized_client.force_login(cls.user)
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
        cls.group3 = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug=SLUG3
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text=TEXT,
        )
        cls.POST_URL = reverse('posts:post_detail', args=[cls.post.pk])
        cls.EDIT_URL = reverse('posts:post_edit', args=[cls.post.pk])
        cls.COMMENT_URL = reverse('posts:add_comment', args=[cls.post.pk])
        cls.REDIRECT_EDIT_URL = (LOGIN_URL + '?next=' + cls.EDIT_URL)
        cls.REDIRECT_COMMENT_URL = (LOGIN_URL + '?next=' + cls.COMMENT_URL)


    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        Post.objects.all().delete()
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
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
        post = response.context['page_obj'][0]
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(
            post.image.name,
            f'{ settings.UPLOAD_POST }/{ uploaded.name }'
        )

    def test_post_edit(self):
        uploaded = SimpleUploadedFile(
            name='small2.gif',
            content=SMALL_GIF,
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
        self.assertEqual(
            post.image.name,
            f'{ settings.UPLOAD_POST }/{ uploaded.name }'
        )

    def test_anonimys_create_post(self):
        Post.objects.all().delete()
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': TEXT,
            'group': self.group2.id,
            'image': uploaded
        }
        response = self.guest_client.post(
            CREATE_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, REDIRECT_CREATE_URL)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_create_comment(self):
        self.post.comments.all().delete()
        form_data = {
            'text': COMMENT
        }
        response = self.authorized_client.post(
            self.COMMENT_URL,
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.post.comments.count(), 1)
        comment = self.post.comments.all()[0]
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, self.post)
        
    def test_anonimys_create_comment(self):
        self.post.comments.all().delete()
        form_data = {
            'text': COMMENT
        }
        response = self.guest_client.post(
            self.COMMENT_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.REDIRECT_COMMENT_URL)
        self.assertEqual(self.post.comments.count(), 0)

    def test_anonimys_and_non_author_post_edit(self):
        text = self.post.text
        author = self.post.author
        group = self.post.group.pk
        image = self.post.image
        uploaded = SimpleUploadedFile(
            name='small3.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': TEXT2,
            'group': self.group3.id,
            'image': uploaded
        }
        clients = [
            [self.guest_client, self.REDIRECT_EDIT_URL],
            [self.authorized_client2, HOME_URL]
        ]
        for client, url in clients:
            with self.subTest(client=client, url=url):
                response = client.post(
                    self.EDIT_URL,
                    data=form_data,
                    follow=True
                )
                self.assertRedirects(response, url)
                self.assertEqual(self.post.text, text)
                self.assertEqual(self.post.author, author)
                self.assertEqual(self.post.group.pk, group)
                self.assertEqual(self.post.image, image)
