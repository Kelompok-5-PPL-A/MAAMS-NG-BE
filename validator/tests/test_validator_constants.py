from django.test import TestCase
from validator.constants import FeedbackMsg


class FeedbackMsgTest(TestCase):
    def test_feedback_messages_format(self):
        column = 'B'
        row = 2
        prev_row = 1

        self.assertEqual(
            FeedbackMsg.FALSE_ROW_1_NOT_CAUSE.format(column=column),
            f"Sebab {column}1 bukan merupakan sebab dari pertanyaan"
        )

        self.assertEqual(
            FeedbackMsg.FALSE_ROW_N_NOT_CAUSE.format(column=column, row=row, prev_row=prev_row),
            f"Sebab {column}{row} bukan merupakan sebab dari {column}{prev_row}"
        )

        self.assertEqual(
            FeedbackMsg.FALSE_ROW_N_POSITIVE_NEUTRAL.format(column=column, row=row),
            f"Sebab {column}{row} merupakan sebab positif atau netral"
        )

        self.assertEqual(
            FeedbackMsg.FALSE_ROW_N_SIMILAR_PREVIOUS.format(column=column, row=row),
            f"Sebab {column}{row} mirip dengan sebab sebelumnya"
        ) 