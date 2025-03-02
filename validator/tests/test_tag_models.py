from django.test import TestCase
from validator.models.tag import Tag

class TagModelTest(TestCase):
    
    def setUp(self):
        """
        setUp Tag object
        """
        self.tag_name = "economy"
        
        Tag.objects.create(name=self.tag_name)
    
    def test_tag(self):
        tag = Tag.objects.get(name=self.tag_name)
        self.assertIsNotNone(tag)
        self.assertEqual(tag.name, self.tag_name)

    def test_tag_str_representation(self):
        tag = Tag.objects.get(name=self.tag_name)
        self.assertEqual(str(tag), self.tag_name)