from django.test import TestCase
from question.models import Question
from tag.models import Tag
import uuid

class QuestionModelTest(TestCase):
    
    def setUp(self):
        """
        setUp Question object without user (Guest)
        """
        self.question_uuid = uuid.uuid4()
        self.tag_name = "economy"
        
        tag = Tag.objects.create(name=self.tag_name)
        
        # Create a question without a user (Guest)
        Question.objects.create(
            id=self.question_uuid,
            title="Test Title",
            question='pertanyaan',
            mode=Question.ModeChoices.PRIBADI
        ).tags.add(tag)
    
    def test_question(self):
        question = Question.objects.get(id=self.question_uuid)
        self.assertIsNotNone(question)        
        self.assertEqual(question.title, "Test Title")
        self.assertEqual(question.question, 'pertanyaan')
        self.assertEqual(question.mode, Question.ModeChoices.PRIBADI)
        self.assertEqual(question.tags.first().name, self.tag_name)
