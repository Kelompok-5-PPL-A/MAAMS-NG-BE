from django.test import TestCase
from validator.models.questions import Question
from validator.models.tag import Tag
from validator.services.questions import QuestionService 
from validator.exceptions import UniqueTagException

class QuestionServiceTest(TestCase):
    def setUp(self):
        """Set up test data."""
        self.service = QuestionService()


    def test_create_question_with_tags(self):
        title = "Test Question 1"
        question_text = "Mengapa harga BBM mahal?"
        mode = Question.ModeChoices.PRIBADI
        tags = ["economy", "love"]

        # Call service with guest user
        created_question = self.service.create(user=None, title=title, question=question_text, mode=mode, tags=tags)

        # Check if question is created
        self.assertEqual(created_question.title, title)
        self.assertEqual(created_question.question, question_text)
        self.assertEqual(created_question.mode, mode)

        # Check if tags are associated correctly
        question_tags = list(created_question.tags.values_list("name", flat=True))
        self.assertCountEqual(question_tags, tags)  


    def test_create_question_without_tags(self):
        title = "Test Question 2"
        question_text = "Mengapa bahan pokok mahal?"
        mode = Question.ModeChoices.PRIBADI

        created_question = self.service.create(user=None, title=title, question=question_text, mode=mode, tags=[])

        self.assertEqual(created_question.title, title)
        self.assertEqual(created_question.question, question_text)
        self.assertEqual(created_question.mode, mode)
        self.assertEqual(created_question.tags.count(), 0)
    

    def test_create_question_with_duplicate_tags(self):
        title = "Test Question 3"
        question_text = "Mengapa harga BBM mahal?"
        mode = Question.ModeChoices.PRIBADI
        tags = ["economy", "economy"]

        with self.assertRaises(UniqueTagException):
            self.service.create(user=None, title=title, question=question_text, mode=mode, tags=tags)