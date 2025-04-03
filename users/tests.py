from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from users.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from PIL import Image
import io

def get_jwt_token(user):
    """
    Helper method to get JWT token for a user.
    """
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

class UserTests(APITestCase):
    def setUp(self):
        # Set up a test user
        image = self.create_dummy_image()
        self.user_data = {
            'username': 'testuser',
            'password': 'testpassword123',
            'email': 'testuser@example.com',
            'profile_picture': image
        }
        self.user = User.objects.create_user(**self.user_data)
        self.url = reverse('user-details')
    
    def create_dummy_image(self):
        """Create a dummy image for testing."""
        # Create an image in memory
        image = Image.new('RGB', (100, 100), color = (255, 0, 0))
        image_file = io.BytesIO()
        image.save(image_file, format='JPEG')
        image_file.name = 'profile_picture.jpg'  # Ensure it has a name
        image_file.seek(0)  # Go to the beginning of the file
        return SimpleUploadedFile(image_file.name, image_file.read(), content_type='image/jpeg')


    def test_create_user(self):
        """
        Test user creation (POST request).
        """
        data = {
            'username': 'newuser',
            'password': 'newpassword123',
            'email': 'newuser@example.com',
        }
        response = self.client.post(self.url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.get(username='newuser').email, 'newuser@example.com')

    def test_get_user(self):
        """
        Test retrieving a user by ID (GET request).
        """
        url = reverse('user-details', kwargs={'id': self.user.id})  # Ensure URL is correct
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['email'], self.user.email)

    def test_get_user_not_found(self):
        """
        Test retrieving a user that does not exist (GET request).
        """
        url = reverse('user-details', kwargs={'id': 99999})  # Non-existing user ID
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_user(self):
        """
        Test updating user information (PUT request).
        """
        token = get_jwt_token(self.user)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        url = reverse('user-details', kwargs={'id': self.user.id})
        updated_data = {
            'username': 'updateduser',
            'password': 'newpassword123',
            'email': 'updateduser@example.com',
        }
        response = self.client.put(url, updated_data, format='multipart')

        self.user.refresh_from_db()  # Refresh the user instance from the database
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.username, 'updateduser')
        self.assertEqual(self.user.email, 'updateduser@example.com')

    def test_update_user_permission_denied(self):
        """
        Test updating another user (PermissionDenied).
        """
        # Create a second user
        second_user = User.objects.create_user(username='seconduser', password='secondpassword123', email='seconduser@example.com')

        token = get_jwt_token(second_user)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        
        url = reverse('user-details', kwargs={'id': self.user.id})

        # Log in as the second user and try to update the first user
        updated_data = {
            'username': 'updateduser',
            'password': 'newpassword123',
            'email': 'updateduser@example.com',
        }
        response = self.client.put(url, updated_data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user(self):
        """
        Test deleting a user (DELETE request).
        """
        url = reverse('user-details', kwargs={'id': self.user.id})

        token = get_jwt_token(self.user)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 0) 

    def test_delete_user_permission_denied(self):
        """
        Test deleting another user (PermissionDenied).
        """
        # Create a second user
        second_user = User.objects.create_user(username='seconduser', password='secondpassword123', email='seconduser@example.com')

        token = get_jwt_token(second_user)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        
        url = reverse('user-details', kwargs={'id': self.user.id})

        # Log in as the second user and try to delete the first user
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_user_no_permission(self):
        """
        Test the case where a user tries to create a user without providing required fields.
        """
        data = {
            'username': '',
            'password': '',
        }
        response = self.client.post(self.url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)
        self.assertIn('password', response.data)


class FollowUnfollowUserTest(APITestCase):
    def setUp(self):
        # Create two users for testing (follower and user to follow)
        self.user1 = User.objects.create_user(username="user1", password="password")
        self.user2 = User.objects.create_user(username="user2", password="password")
        
        # Authenticate user1 for follow/unfollow actions
        self.token = get_jwt_token(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        # URLs
        self.follow_url = reverse('follow', kwargs={'id': self.user2.id})
        self.unfollow_url = reverse('follow', kwargs={'id': self.user2.id})

    def test_follow_user(self):
        """Test following a user."""
        response = self.client.post(self.follow_url)
        
        # Check that the response status is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that user1 is now following user2
        self.user2.refresh_from_db()
        self.assertIn(self.user1, self.user2.followers.all())

    def test_unfollow_user(self):
        """Test unfollowing a user."""
        # First, follow user2
        self.user1.followers.add(self.user2)

        response = self.client.delete(self.unfollow_url)

        # Check that the response status is 204 No Content (successful deletion)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Check that user1 is no longer following user2
        self.user2.refresh_from_db()
        self.assertNotIn(self.user1, self.user2.followers.all())

    def test_follow_nonexistent_user(self):
        """Test following a user that does not exist."""
        invalid_url = reverse('follow', kwargs={'id': 999999})  # ID that doesn't exist
        response = self.client.post(invalid_url)

        # Check that the response is a 404 Not Found
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class BlockUnblockUserTest(APITestCase):
    def setUp(self):
        # Create two users for testing (blocker and user to block)
        self.user1 = User.objects.create_user(username="user1", password="password")
        self.user2 = User.objects.create_user(username="user2", password="password")
        
        # Authenticate user1 for block/unblock actions
        self.token = get_jwt_token(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        # URLs
        self.block_url = reverse('block', kwargs={'id': self.user2.id})
        self.unblock_url = reverse('block', kwargs={'id': self.user2.id})

    def test_block_user(self):
        """Test blocking a user."""
        response = self.client.post(self.block_url)
        
        # Check that the response status is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that user2 is now in the blocked_users list of user1
        self.user1.refresh_from_db()
        self.assertIn(self.user2, self.user1.blocked_users.all())

    def test_unblock_user(self):
        """Test unblocking a user."""
        # First, block user2
        self.user1.blocked_users.add(self.user2)

        response = self.client.delete(self.unblock_url)

        # Check that the response status is 204 No Content (successful deletion)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Check that user2 is no longer in the blocked_users list of user1
        self.user1.refresh_from_db()
        self.assertNotIn(self.user2, self.user1.blocked_users.all())

    def test_block_nonexistent_user(self):
        """Test blocking a user that does not exist."""
        invalid_url = reverse('block', kwargs={'id': 999999})  # ID that doesn't exist
        response = self.client.post(invalid_url)

        # Check that the response is a 404 Not Found
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)