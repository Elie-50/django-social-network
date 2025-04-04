from rest_framework_simplejwt.tokens import RefreshToken
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

def get_jwt_token(user):
    """
    Helper method to get JWT token for a user.
    """
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

def create_dummy_image():
        """Create a dummy image for testing."""
        # Create an image in memory
        image = Image.new('RGB', (100, 100), color = (255, 0, 0))
        image_file = io.BytesIO()
        image.save(image_file, format='JPEG')
        image_file.name = 'test_image.jpg'
        image_file.seek(0)
        return SimpleUploadedFile(image_file.name, image_file.read(), content_type='image/jpeg')