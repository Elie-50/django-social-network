from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Post, Comment, Reply, PostFile
from users.models import User
from helpers.util import *

class PostViewTest(APITestCase):

    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username="user1", password="password")
        self.user2 = User.objects.create_user(username="user2", password="password")

         # Create a post by user1
        self.post = Post.objects.create(content="Test Post", author=self.user1)

        # Authenticate user1 for the tests
        self.token = get_jwt_token(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_create_post(self):
        url = reverse('post-details')
        data = {
            'content': 'New Post',
        }
        response = self.client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'New Post')
        self.assertEqual(response.data['author']['id'], self.user1.id)

    def test_update_post_as_author(self):
        url = reverse('post-details', kwargs={'id': self.post.id})
        data = {
            'content': 'Updated Post',
        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Updated Post')

    def test_update_post_as_non_author(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + get_jwt_token(self.user2))  # Login as user2
        url = reverse('post-details', kwargs={'id': self.post.id})
        data = {
            'content': 'Attempted Update',
        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_post_as_author(self):
        url = reverse('post-details', kwargs={'id': self.post.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())

    def test_delete_post_as_non_author(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + get_jwt_token(self.user2))  # Login as user2
        url = reverse('post-details', kwargs={'id': self.post.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_nonexistent_post(self):
        url = reverse('post-details', kwargs={'id': 999999})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class CommentViewTest(APITestCase):

    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username="user1", password="password")
        self.user2 = User.objects.create_user(username="user2", password="password")
        
        # Authenticate user1 for the tests
        self.token = get_jwt_token(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        
        # Create a post by user1
        self.post = Post.objects.create(content="Test Post", author=self.user1)

        # Create a comment by user1 on the post
        self.comment = Comment.objects.create(content="Test Comment", author=self.user1, post=self.post)

    def test_create_comment(self):
        url = reverse('comment-details', kwargs={'id': self.comment.id})
        data = {
            'content': 'New Comment',
            'post': self.post.id,
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'New Comment')
        self.assertEqual(response.data['author']['id'], self.user1.id)

    def test_update_comment_as_author(self):
        url = reverse('comment-details', kwargs={'id': self.comment.id})
        data = {
            'content': 'Updated Comment',
            'post': self.post.id
        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Updated Comment')

    def test_update_comment_as_non_author(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + get_jwt_token(self.user2))  # Login as user2
        url = reverse('comment-details', kwargs={'id': self.comment.id})
        data = {
            'content': 'Attempted Update',
        }

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_comment_as_author(self):
        url = reverse('comment-details', kwargs={'id': self.comment.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_delete_comment_as_non_author(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + get_jwt_token(self.user2))  # Login as user2
        url = reverse('comment-details', kwargs={'id': self.comment.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_nonexistent_comment(self):
        url = reverse('comment-details', kwargs={'id': 999999})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class ReplyViewTest(APITestCase):

    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username="user1", password="password")
        self.user2 = User.objects.create_user(username="user2", password="password")

        # Authenticate user1 for the tests
        self.token = get_jwt_token(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        # Create a post, comment, and reply by user1
        self.post = Post.objects.create(content="Test Post", author=self.user1)
        self.comment = Comment.objects.create(content="Test Comment", author=self.user1, post=self.post)
        self.reply = Reply.objects.create(content="Test Reply", author=self.user1, comment=self.comment)

    def test_create_reply(self):
        url = reverse('reply-details', kwargs={'id': self.reply.id})
        data = {
            'content': 'New Reply',
            'comment': self.comment.id,
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'New Reply')
        self.assertEqual(response.data['author']['id'], self.user1.id)

    def test_update_reply_as_author(self):
        url = reverse('reply-details', kwargs={'id': self.reply.id})
        data = {
            'content': 'Updated Reply',
            'comment': self.comment.id
        }

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Updated Reply')

    def test_update_reply_as_non_author(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + get_jwt_token(self.user2))  # Login as user2
        url = reverse('reply-details', kwargs={'id': self.reply.id})
        data = {
            'content': 'Attempted Update',
        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_reply_as_author(self):
        url = reverse('reply-details', kwargs={'id': self.reply.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Reply.objects.filter(id=self.reply.id).exists())

    def test_delete_reply_as_non_author(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + get_jwt_token(self.user2))  # Login as user2
        url = reverse('reply-details', kwargs={'id': self.reply.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_nonexistent_reply(self):
        url = reverse('reply-details', kwargs={'id': 999999})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LikeTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='testuser',
            password='testpassword123'
        )

        self.user2 = User.objects.create_user(
            username='testuser2',
            password='testpassword123'
        )

        # Authenticate user1 for the tests
        self.token = get_jwt_token(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        # Create a post, comment, and reply by user1
        self.post = Post.objects.create(content="Test Post", author=self.user2)
        self.comment = Comment.objects.create(content="Test Comment", author=self.user1, post=self.post)
        self.reply = Reply.objects.create(content="Test Reply", author=self.user2, comment=self.comment)

    def test_like_post(self):
        # url for the post like
        url = reverse('post-like', kwargs={'id': self.post.id})

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.post.refresh_from_db()
        self.assertIn(self.user1, self.post.likers.all())

        # test like post again

        response2 = self.client.post(url)
        self.post.refresh_from_db()
        self.assertEqual(self.post.likers.count(), 1)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

    def test_unlike_post(self):
        # add user1 to post likers
        self.post.likers.add(self.user1)

        # unlike the post
        url = reverse('post-like', kwargs={'id': self.post.id})
        response = self.client.delete(url)

        self.post.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertNotIn(self.user1, self.post.likers.all())

    def test_like_comment(self):
        # url for the comment like
        url = reverse('comment-like', kwargs={'id': self.comment.id})

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.post.refresh_from_db()
        self.assertIn(self.user1, self.comment.likers.all())

        # test like comement again

        response2 = self.client.post(url)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.likers.count(), 1)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

    def test_unlike_comment(self):
        # add user1 to comment likers
        self.comment.likers.add(self.user1)

        # unlike the comment
        url = reverse('comment-like', kwargs={'id': self.comment.id})
        response = self.client.delete(url)

        self.comment.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertNotIn(self.user1, self.comment.likers.all())

    def test_like_reply(self):
        # url for the reply like
        url = reverse('reply-like', kwargs={'id': self.reply.id})

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.post.refresh_from_db()
        self.assertIn(self.user1, self.reply.likers.all())

        # test like reply again
        response2 = self.client.post(url)
        self.post.refresh_from_db()
        self.assertEqual(self.reply.likers.count(), 1)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

    def test_unlike_reply(self):
        # add user1 to reply likers
        self.reply.likers.add(self.user1)

        # unlike the reply
        url = reverse('reply-like', kwargs={'id': self.reply.id})
        response = self.client.delete(url)

        self.reply.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertNotIn(self.user1, self.reply.likers.all())


class PostFileTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="testuser",
            password='testpassword123'
        )

        # Authenticate user1 for the tests
        self.token = get_jwt_token(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        self.post = Post.objects.create(content="Post content", author=self.user1)
        self.image = create_dummy_image()

    def test_upload_image_to_file(self):
        data = {
            'file': self.image,
            'post': self.post.id
        }
        url = reverse('post-file')
        response = self.client.post(url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.post.refresh_from_db()

        self.assertEqual(self.post.files.count(), 1)

    def test_remove_post_file(self):
        post_file = PostFile.objects.create(post=self.post, file=self.image)

        url = reverse('post-file', kwargs={'id': post_file.id})

        response = self.client.delete(url)

        self.post.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertNotIn(post_file, self.post.files.all())

