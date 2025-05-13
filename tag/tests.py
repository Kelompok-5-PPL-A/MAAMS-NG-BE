from django.test import TestCase
from django.db.utils import IntegrityError
from tag.models import Tag
import uuid

class TagModelTests(TestCase):
    def test_create_tag(self):
        """Test creating a Tag instance with valid data."""
        tag = Tag.objects.create(name='TestTag')
        self.assertEqual(tag.name, 'TestTag')
        self.assertIsInstance(tag.id, uuid.UUID)

    def test_create_tag_with_duplicate_name(self):
        """Test that creating a Tag with a duplicate name."""
        Tag.objects.create(name='UniqueTag')
    
        with self.assertRaises(IntegrityError):
            Tag.objects.create(name='UniqueTag')

    def test_tag_string_representation(self):
        """Test the string representation of the Tag instance."""
        tag = Tag(name='TestTag')
        self.assertEqual(str(tag), 'TestTag')