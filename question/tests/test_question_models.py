from django.test import TestCase
from question.models import Question
from tag.models import Tag
import uuid
from django.contrib.auth import get_user_model

class QuestionModelTest(TestCase):
    
    def setUp(self):
        """
        setUp Question object without user (Guest)
        """
        self.question_uuid = uuid.uuid4()
        self.tag_name = "economy"

        # Create test user
        User = get_user_model()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            username='testuser'
        )
        
        tag = Tag.objects.create(name=self.tag_name)
        
        # Create a question without a user (Guest)
        Question.objects.create(
            id=self.question_uuid,
            title="Test Title",
            question='pertanyaan',
            mode=Question.ModeChoices.PRIBADI
        ).tags.add(tag)

        # Create a question with user
        self.user_question = Question.objects.create(
            id=uuid.uuid4(),
            title="User Question",
            question='user question',
            mode=Question.ModeChoices.PRIBADI,
            user=self.user
        )
        self.user_question.tags.add(tag)
    
    def test_question(self):
        question = Question.objects.get(id=self.question_uuid)
        self.assertIsNotNone(question)        
        self.assertEqual(question.title, "Test Title")
        self.assertEqual(question.question, 'pertanyaan')
        self.assertEqual(question.mode, Question.ModeChoices.PRIBADI)
        self.assertEqual(question.tags.first().name, self.tag_name)

    def test_user_question(self):
        question = Question.objects.get(id=self.user_question.id)
        self.assertIsNotNone(question)
        self.assertEqual(question.title, "User Question")
        self.assertEqual(question.question, 'user question')
        self.assertEqual(question.mode, Question.ModeChoices.PRIBADI)
        self.assertEqual(question.tags.first().name, self.tag_name)
        self.assertEqual(question.user, self.user)  # Test that user is correctly assigned