from django.test import TestCase
from .models import Tag
import uuid

class TagModelTests(TestCase):
    def test_create_tag(self):
        """Test creating a Tag instance with valid data."""
        tag = Tag.objects.create(name='TestTag')
        self.assertEqual(tag.name, 'TestTag')
        self.assertIsInstance(tag.id, uuid.UUID)  # Check that the ID is a UUID

    def test_create_tag_with_duplicate_name(self):
        """Test that creating a Tag with a duplicate name raises an IntegrityError."""
        Tag.objects.create(name='UniqueTag')  # Create the first tag
        with self.assertRaises(Exception) as context:
            Tag.objects.create(name='UniqueTag')  # Attempt to create a duplicate tag
        self.assertTrue('UNIQUE constraint failed' in str(context.exception))  # Check for unique constraint error

    def test_tag_string_representation(self):
        """Test the string representation of the Tag instance."""
        tag = Tag(name='TestTag')
        self.assertEqual(str(tag), 'TestTag')  # Check that the string representation is correct