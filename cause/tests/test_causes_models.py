from django.test import TestCase
from question.models import Question
from ..models import Causes
import uuid

class CausesModelTest(TestCase):
# Sebagai guest
    def setUp(self):
        """
        Set up Question object without user (Guest)
        """
        self.question_uuid = uuid.uuid4()

        self.question = Question.objects.create(
            id=self.question_uuid,
            question='pertanyaan',
            mode=Question.ModeChoices.PRIBADI
        )

        """
        Set up Causes object
        """
        self.causes_uuid = uuid.uuid4()

        Causes.objects.create(
            question=self.question,
            id=self.causes_uuid,
            row=1,
            column=1,
            mode=Causes.ModeChoices.PRIBADI,
            cause='cause'
        )

    def test_causes(self):
        causes = Causes.objects.get(id=self.causes_uuid)
        self.assertIsNotNone(causes)
        self.assertEqual(causes.question.id, self.question.id)
        self.assertEqual(causes.row, 1)
        self.assertEqual(causes.column, 1)
        self.assertEqual(causes.mode, Causes.ModeChoices.PRIBADI)
        self.assertEqual(causes.cause, 'cause')
