from tag.models import Tag
from validator.exceptions import InvalidFiltersException, UniqueTagException, ForbiddenRequestException, InvalidTimeRangeRequestException, ValueNotUpdatedException
from validator.constants import ErrorMsg
from django.test import TestCase
from unittest.mock import Mock, patch
from question.models import Question 
from question.services import QuestionService
import uuid
from django.core.exceptions import ObjectDoesNotExist
from validator.exceptions import NotFoundRequestException
from authentication.models import CustomUser
from django.db.models import Q
from datetime import datetime, timezone, timedelta
from django.db.models.query import QuerySet
from django.contrib.auth import get_user_model

User = get_user_model()

class TestQuestionService(TestCase):
    def setUp(self):
        self.service = QuestionService()
        self.question_id = uuid.uuid4()
        self.user = CustomUser.objects.create(username="testuser68", password="password12389", email='testuser969@gmail.com')
        self.user.save()

        self.user_admin = CustomUser.objects.create(
            username="admin_user",
            password="admin_password",
            email='admin_user@gmail.com',
            is_staff=True,
            is_superuser=True,
        )
        self.user_admin.save()

        self.question = Question.objects.create(
            id=self.question_id,
            title="Test Title",
            question="Test Question",
            mode="Test Mode",
            user=self.user,
            created_at=datetime.now(timezone.utc)
        )
        self.tag = Tag.objects.create(name="test_tag")
        self.question.tags.add(self.tag)

    def test_create_question_with_valid_data(self):
        # Arrange
        title = "Test Title"
        question = "Test Question"
        mode = Question.ModeChoices.PRIBADI
        tags = ["tag1", "tag2"]
        user = self.user

        with patch('question.models.Question.objects.create') as mock_create:
            with patch.object(self.service, '_validate_tags') as mock_validate:
                mock_question = Mock()
                mock_create.return_value = mock_question
                mock_validate.return_value = [Mock(spec=Tag), Mock(spec=Tag)]
                
                # Act
                result = self.service.create(title, question, mode, tags, user)
                
                # Assert
                mock_create.assert_called_once_with(
                    title=title,
                    question=question,
                    mode=mode,
                    user=user
                )
                self.assertEqual(result, mock_question)

    def test_create_question_with_guest_user(self):
        # Arrange
        title = "Guest Title"
        question = "Guest Question"
        mode = Question.ModeChoices.PRIBADI
        tags = ["tag1", "tag2"]
        user = None  # Guest user

        with patch('question.models.Question.objects.create') as mock_create:
            with patch.object(self.service, '_validate_tags') as mock_validate:
                mock_question = Mock()
                mock_create.return_value = mock_question
                mock_validate.return_value = [Mock(spec=Tag), Mock(spec=Tag)]
                
                # Act
                result = self.service.create(title, question, mode, tags, user)
                
                # Assert
                mock_create.assert_called_once_with(
                    title=title,
                    question=question,
                    mode=mode,
                    user=None
                )
                self.assertEqual(result, mock_question)

    def test_get_question_not_found(self):
        # Test getting a question with non-existent ID
        with self.assertRaises(NotFoundRequestException) as context:
            self.service.get(uuid.uuid4())
        self.assertEqual(str(context.exception), ErrorMsg.NOT_FOUND)

    def test_get_recent_with_authenticated_user(self):
        # Test get_recent with authenticated user
        with patch('question.models.Question.objects.filter') as mock_filter:
            mock_query = Mock()
            mock_filter.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.first.return_value = self.question

            # Act
            result = self.service.get_recent(self.user)
            
            # Assert
            mock_filter.assert_called_once_with(user=self.user)
            mock_query.order_by.assert_called_once_with('-created_at')
            self.assertEqual(result, self.question)

    def test_get_recent_with_guest_user(self):
        # Test get_recent with guest user (should return None)
        result = self.service.get_recent(user=None)
        self.assertIsNone(result)

    def test_get_recent_no_questions(self):
        # Test get_recent when user has no questions
        user_without_questions = CustomUser.objects.create(
            username="no_questions", 
            password="password12389", 
            email='no_questions@gmail.com'
        )
        
        result = self.service.get_recent(user_without_questions)
        self.assertIsNone(result, "Should return None when no questions exist")

    def test_make_question_response_empty_list(self):
        # Test _make_question_response with empty list
        response = self.service._make_question_response([])
        self.assertEqual(response, [])
    
    def test_make_question_response_with_question(self):
        # Test _make_question_response with a question object
        response = self.service._make_question_response([self.question])
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0].id, self.question.id)
        self.assertEqual(response[0].title, self.question.title)
        self.assertEqual(response[0].question, self.question.question)
        self.assertEqual(response[0].mode, self.question.mode)
        self.assertEqual(response[0].username, self.user.username)  # Check username field

    def test_make_question_response_with_guest_question(self):
        # Test _make_question_response with a question created by guest
        guest_question = Question.objects.create(
            id=uuid.uuid4(),
            title="Guest Title",
            question="Guest Question",
            mode="Test Mode",
            user=None,  # Guest user
        )
        guest_question.tags.add(self.tag)
        
        response = self.service._make_question_response([guest_question])
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0].id, guest_question.id)
        self.assertEqual(response[0].title, guest_question.title)
        self.assertEqual(response[0].question, guest_question.question)
        self.assertEqual(response[0].mode, guest_question.mode)
        self.assertIsNone(response[0].username)  # Username should be None for guest

    def test_validate_tags_with_existing_tags(self):
        # Arrange
        tags = ["existing_tag"]
        
        with patch('tag.models.Tag.objects.get') as mock_get:
            mock_tag = Mock(spec=Tag)
            mock_get.return_value = mock_tag
            
            # Act
            result = self.service._validate_tags(tags)
            
            # Assert
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0], mock_tag)

    def test_validate_tags_with_new_tags(self):
        # Arrange
        tags = ["new_tag"]
        
        with patch('tag.models.Tag.objects.get') as mock_get:
            with patch('tag.models.Tag.objects.create') as mock_create:
                mock_tag = Mock(spec=Tag)
                mock_get.side_effect = Tag.DoesNotExist()
                mock_create.return_value = mock_tag
                
                # Act
                result = self.service._validate_tags(tags)
                
                # Assert
                self.assertEqual(len(result), 1)
                mock_create.assert_called_once_with(name="new_tag")

    def test_validate_tags_with_duplicate_tags(self):
        # Arrange
        tags = ["tag1", "tag1"]
        
        with patch('tag.models.Tag.objects.get') as mock_get:
            mock_tag = Mock(spec=Tag)
            mock_get.return_value = mock_tag
            
            # Act & Assert
            with self.assertRaises(UniqueTagException) as context:
                self.service._validate_tags(tags)
            self.assertEqual(str(context.exception), ErrorMsg.TAG_MUST_BE_UNIQUE)

    def test_validate_tags_duplicate_tag(self):
        # Test _validate_tags with duplicate tag
        tag_name = "duplicate"
        Tag.objects.create(name=tag_name)
        
        with self.assertRaises(UniqueTagException) as context:
            self.service._validate_tags([tag_name, tag_name])
        self.assertEqual(str(context.exception), ErrorMsg.TAG_MUST_BE_UNIQUE)

    def test_get_privileged_with_admin_and_valid_filter(self):
        # Arrange
        admin_user = CustomUser.objects.create(
            username="admin", 
            password="password123", 
            email="admin@example.com",
            is_superuser=True, 
            is_staff=True,
            role = "admin"
        )
        question_pengawasan = Question.objects.create(
            id=uuid.uuid4(),
            title="Pengawasan Question",
            question="Should be visible to admin",
            mode=Question.ModeChoices.PENGAWASAN,
            user=admin_user,
        )
        
        # Act
        result = self.service.get_privileged("semua", admin_user, "")

        # Assert
        self.assertIn(question_pengawasan, result)

    def test_get_privileged_forbidden_for_non_admin(self):
        # Arrange
        non_admin = CustomUser.objects.create(
            username="user", 
            password="password123", 
            email="user@example.com",
            is_superuser=False, 
            is_staff=False
        )

        # Act & Assert
        with self.assertRaises(ForbiddenRequestException) as context:
            self.service.get_privileged("semua", non_admin, "keyword")
        self.assertEqual(str(context.exception), ErrorMsg.FORBIDDEN_GET)
    
    def test_get_privileged_sets_default_q_filter_when_empty(self):
        # Arrange
        admin_user = CustomUser.objects.create(
            username="admin_default", 
            password="password123", 
            email="admin_default@example.com",
            is_superuser=True, 
            is_staff=True,
            role = "admin"
        )
        question_pengawasan = Question.objects.create(
            id=uuid.uuid4(),
            title="Pengawasan Question",
            question="Should be visible when q_filter is empty",
            mode=Question.ModeChoices.PENGAWASAN,
            user=admin_user,
        )

        # Patch _resolve_filter_type to check input q_filter value
        with patch.object(self.service, '_resolve_filter_type') as mock_resolve_filter:
            mock_resolve_filter.return_value = Q()  # dummy filter
            result = self.service.get_privileged('', admin_user, '')

        # Assert _resolve_filter_type menerima q_filter 'semua' sebagai fallback
        mock_resolve_filter.assert_called_once_with('semua', '', True)
        self.assertIn(question_pengawasan, result)


    # ini test buat filter
    def test_resolve_filter_type_pengguna(self):
        # Arrange
        keyword = "john"
        expected_clause = (
            Q(user__username__icontains=keyword) |
            Q(user__first_name__icontains=keyword) |
            Q(user__last_name__icontains=keyword)
        )

        # Act
        clause = self.service._resolve_filter_type("pengguna", keyword, True)

        # Assert
        self.assertEqual(str(clause), str(expected_clause))


    def test_resolve_filter_type_judul(self):
        # Arrange
        keyword = "judul test"
        expected_clause = (
            Q(title__icontains=keyword) |
            Q(question__icontains=keyword)
        )

        # Act
        clause = self.service._resolve_filter_type("judul", keyword, True)

        # Assert
        self.assertEqual(str(clause), str(expected_clause))


    def test_resolve_filter_type_topik(self):
        # Arrange
        keyword = "ekonomi"
        expected_clause = Q(tags__name__icontains=keyword)

        # Act
        clause = self.service._resolve_filter_type("topik", keyword, True)

        # Assert
        self.assertEqual(str(clause), str(expected_clause))


    def test_resolve_filter_type_semua_with_admin(self):
        # Arrange
        keyword = "cari"
        clause = self.service._resolve_filter_type("semua", keyword, True)

        # Assert
        self.assertIn("title__icontains", str(clause))
        self.assertIn("question__icontains", str(clause))
        self.assertIn("tags__name__icontains", str(clause))
        self.assertIn("user__username__icontains", str(clause))  # karena admin


    def test_resolve_filter_type_semua_without_admin(self):
        # Arrange
        keyword = "cari"
        clause = self.service._resolve_filter_type("semua", keyword, False)

        # Assert
        self.assertIn("title__icontains", str(clause))
        self.assertIn("question__icontains", str(clause))
        self.assertIn("tags__name__icontains", str(clause))
        self.assertNotIn("user__username__icontains", str(clause))  # karena bukan admin


    def test_resolve_filter_type_invalid_filter_raises_exception(self):
        # Act & Assert
        with self.assertRaises(InvalidFiltersException) as context:
            self.service._resolve_filter_type("invalid", "keyword", True)
        self.assertEqual(str(context.exception), ErrorMsg.INVALID_FILTERS)

    def test_get_matched_time_range_exception(self):
        user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        service = QuestionService()

        with self.assertRaises(InvalidTimeRangeRequestException) as context:
            service.get_matched(
                q_filter="semua",
                user=user,
                time_range="invalid_range", 
                keyword="tes"
            )
        self.assertEqual(str(context.exception), ErrorMsg.INVALID_TIME_RANGE)
    

    def test_get_matched_question_found_last_week(self):
        keyword = "test"
        question1 = Question.objects.create(
            title="Test Title 1",
            question="Test Question 1",
            mode=Question.ModeChoices.PRIBADI,
            user=self.user,
        )
        question2 = Question.objects.create(
            title="Test Title 2",
            question="Test Question 2",
            mode=Question.ModeChoices.PRIBADI,
            user=self.user,
        )

        # Act
        result = self.service.get_matched(
            user=self.user,
            keyword=keyword,
            time_range='last_week',
            q_filter=None
        )

        result_ids = [item.id for item in result]
        self.assertIn(question1.id, result_ids)
        self.assertIn(question2.id, result_ids)
    

    def test_get_matched_question_not_found_last_week(self):
        keyword = "haha"
        question1 = Question.objects.create(
            title="Test Question 1",
            question="Test Question 1",
            mode=Question.ModeChoices.PRIBADI,
            user=self.user,
        )
        # Act
        result = self.service.get_matched(
            user=self.user,
            keyword=keyword,
            time_range='last_week',
            q_filter=None
        )

        result_ids = [item.id for item in result]
        self.assertNotIn(question1.id, result_ids)
    

    def test_get_matched_question_found_older(self):
        keyword = "test"
        question1 = Question.objects.create(
            title="Test Title 1",
            question="Test Question 1",
            mode=Question.ModeChoices.PRIBADI,
            user=self.user,
        )
        question1.created_at = datetime.now(timezone.utc) - timedelta(days=8)  # Set to older than 7 days
        question1.save()

        question2 = Question.objects.create(
            title="Test Title 2",
            question="Test Question 2",
            mode=Question.ModeChoices.PRIBADI,
            user=self.user,
        )
        question2.created_at = datetime.now(timezone.utc) - timedelta(days=10)
        question2.save()

        # Act
        result = self.service.get_matched(
            user=self.user,
            keyword=keyword,
            time_range='older',
            q_filter=None
        )

        result_ids = [item.id for item in result]
        self.assertIn(question1.id, result_ids)
        self.assertIn(question2.id, result_ids)
    

    def test_get_matched_question_not_found_older(self):
        keyword = "haha"
        question1 = Question.objects.create(
            title="Test Title 1",
            question="Test Question 1",
            mode=Question.ModeChoices.PRIBADI,
            user=self.user,
        )
        question1.created_at = datetime.now(timezone.utc) - timedelta(days=8)
        question1.save()

        result = self.service.get_matched(
            user=self.user,
            keyword=keyword,
            time_range='older',
            q_filter=None
        )
        result_ids = [item.id for item in result]
        self.assertNotIn(question1.id, result_ids)
    
    def test_get_matched_empty_keyword(self):
        # Act & Assert
        with self.assertRaises(InvalidFiltersException) as context:
            self.service.get_matched(
                user=self.user,
                keyword="",
                time_range='last_week',
                q_filter=None
            )
        
        # Check that the right error message is returned
        self.assertEqual(str(context.exception), ErrorMsg.EMPTY_KEYWORD)
    
    def test_get_all_questions_last_week(self):
        self.question.delete()
        question1 = Question.objects.create(
            title="Test Title 1",
            question="Test Question 1",
            mode=Question.ModeChoices.PRIBADI,
            user=self.user,
        )
        question2 = Question.objects.create(
            title="Test Title 2",
            question="Test Question 2",
            mode=Question.ModeChoices.PRIBADI,
            user=self.user,
        )
        question3 = Question.objects.create(
            title="Test Title 3",
            question="Test Question 3",
            mode=Question.ModeChoices.PENGAWASAN,
            user=self.user,
        )
        question4 = Question.objects.create(
            title="Test Title 4",
            question="Test Question 4",
            mode=Question.ModeChoices.PENGAWASAN,
            user=self.user,
        )
        result = self.service.get_all(user=self.user, time_range='last_week')
        result_ids = [item.id for item in result]
        self.assertIn(question4.id, result_ids)
        self.assertIn(question3.id, result_ids)
        self.assertIn(question2.id, result_ids)
        self.assertIn(question1.id, result_ids)
        self.assertEqual(len(result), 4)
    
    def test_get_all_questions_last_week_not_found(self):
        # Test get_all with last_week time range and no questions found
        self.question.delete()
        question1 = Question.objects.create(
            title="Test Title 1",
            question="Test Question 1",
            mode=Question.ModeChoices.PRIBADI,
            user=self.user,
        )
        question1.created_at = datetime.now(timezone.utc) - timedelta(days=8)
        question1.save()

        question2 = Question.objects.create(
            title="Test Title 2",
            question="Test Question 2",
            mode=Question.ModeChoices.PRIBADI,
            user=self.user,
        )
        question2.created_at = datetime.now(timezone.utc) - timedelta(days=10)
        question2.save()
        result = self.service.get_all(user=self.user, time_range='last_week')
        self.assertEqual(list(result), [])
        self.assertEqual(len(result), 0)

    def test_get_all_questions_older(self):
        self.question.delete()
        question1 = Question.objects.create(
            title="Test Title 1",
            question="Test Question 1",
            mode=Question.ModeChoices.PRIBADI,
            user=self.user,
        )
        question1.created_at = datetime.now(timezone.utc) - timedelta(days=8)  # Set to older than 7 days
        question1.save()

        question2 = Question.objects.create(
            title="Test Title 2",
            question="Test Question 2",
            mode=Question.ModeChoices.PRIBADI,
            user=self.user,
        )
        question2.created_at = datetime.now(timezone.utc) - timedelta(days=10)
        question2.save()

        question3 = Question.objects.create(
            title="Test Title 3",
            question="Test Question 3",
            mode=Question.ModeChoices.PENGAWASAN,
            user=self.user,
        )
        question3.created_at = datetime.now(timezone.utc) - timedelta(days=8)
        question3.save()

        question4 = Question.objects.create(
            title="Test Title 4",
            question="Test Question 4",
            mode=Question.ModeChoices.PENGAWASAN,
            user=self.user,
        )
        question4.created_at = datetime.now(timezone.utc) - timedelta(days=8)
        question4.save()
        

        result = self.service.get_all(user=self.user, time_range='older')
        result_ids = [item.id for item in result]
        self.assertIn(question4.id, result_ids)
        self.assertIn(question3.id, result_ids)
        self.assertIn(question2.id, result_ids)
        self.assertIn(question1.id, result_ids)
        self.assertEqual(len(result), 4)
    
    def test_get_all_questions_older_not_found(self):
        # Test get_all with older time range and no questions found
        self.question.delete()
        question1 = Question.objects.create(
            title="Test Title 1",
            question="Test Question 1",
            mode=Question.ModeChoices.PRIBADI,
            user=self.user,
        )
        question1.save()

        question2 = Question.objects.create(
            title="Test Title 2",
            question="Test Question 2",
            mode=Question.ModeChoices.PRIBADI,
            user=self.user,
        )
        question2.save()
        question3 = Question.objects.create(
            title="Test Title 3",
            question="Test Question 3",
            mode=Question.ModeChoices.PENGAWASAN,
            user=self.user,
        )
        question3.save()

        result = self.service.get_all(user=self.user, time_range='older')
        self.assertEqual(list(result), [])
        self.assertEqual(len(result), 0)

    def test_get_all_questions_empty(self):
        self.question.delete()
        result = self.service.get_all(user=self.user, time_range='last_week')
        self.assertEqual(list(result), [])
        self.assertEqual(len(result), 0)
    
    def test_get_field_values_user(self):
        self.question.delete()
        question1 = Question.objects.create(
            title="Question 1",
            question="Content 1",
            mode=Question.ModeChoices.PRIBADI,
            user=self.user,
        )
        question2 = Question.objects.create(
            title="Question 2",
            question="Content 2",
            mode=Question.ModeChoices.PENGAWASAN,
            user=self.user,
        )
        tag1 = Tag.objects.create(name="Tag1")
        tag2 = Tag.objects.create(name="Tag2")
        question1.tags.add(tag1)
        question2.tags.add(tag2)

        result = self.service.get_field_values(self.user)

        # Assert (for admin user)
        self.assertEqual([], result.pengguna)  
        self.assertIn("Question 1", result.judul)
        self.assertIn("Question 2", result.judul)
        self.assertIn("Tag1", result.topik)
        self.assertIn("Tag2", result.topik)
    
    def test_get_field_values_admin(self):
        with patch.object(self.service, 'get_field_values') as mock_get_field_values:
            from collections import namedtuple
            FieldValues = namedtuple('FieldValues', ['pengguna', 'judul', 'topik'])

            mock_result = FieldValues(
                pengguna=['admin_user', 'testuser68'],
                judul=["Question 1", "Question 2", "Question 3"],
                topik=["Tag1", "Tag2", "Tag3"]
            )
            mock_get_field_values.return_value = mock_result
            
            result = self.service.get_field_values(self.user_admin)
            
            mock_get_field_values.assert_called_once_with(self.user_admin)
            
            self.assertEqual(set(['admin_user', 'testuser68']), set(result.pengguna))        
            self.assertIn("Question 1", result.judul) 
            self.assertIn("Question 2", result.judul) 
            self.assertIn("Question 3", result.judul)       
            self.assertIn("Tag1", result.topik)
            self.assertIn("Tag2", result.topik)
            self.assertIn("Tag3", result.topik)
        
    def test_get_field_values_no_questions(self):
        self.question.delete()
        admin_user = CustomUser.objects.create(
            username="adminuser",
            email="admin@example.com",
            password="password123",
            is_superuser=True,
            is_staff=True
        )

        # Act
        result = self.service.get_field_values(user=admin_user)

        # Assert
        self.assertEqual(result.pengguna, [])
        self.assertEqual(result.judul, [])
        self.assertEqual(result.topik, [])

    def test_get_field_values_unauthorized_access(self):
        self.client.logout() 
        response = self.client.get('/question/history/field-values/') ## Attempt to access without authentication
        self.assertEqual(response.status_code, 401)  # Expect 401 (Unauthorized)
    
    def test_get_field_values_sql_injection(self):
        input = "'; DROP TABLE question_question; --"

        with self.assertRaises(Exception):  # Expect an exception if input is sanitized
            self.service.get_field_values(user=input)

    # More test to refactor is_admin
    def test_get_field_values_sets_pengguna_for_admin(self):
        admin = CustomUser.objects.create_user(username="adminuser", email='adminuser@gmail.com', role="admin", password="pass")
        question = Question.objects.create(
            title="Judul Admin",
            question="Isi",
            mode=Question.ModeChoices.PENGAWASAN,
            user=admin
        )

        result = self.service.get_field_values(admin)

        self.assertIn("adminuser", result.pengguna)

    def test_get_privileged_defaults_to_semua_and_empty_keyword(self):
        admin = CustomUser.objects.create_user(username="adminuser", email='adminuser@gmail.com', role="admin", password="pass")
        with patch.object(self.service, '_resolve_filter_type') as mock_resolve:
            mock_resolve.return_value = Q()
            result = self.service.get_privileged('', admin, '')
            mock_resolve.assert_called_once_with('semua', '', True)
            self.assertIsInstance(result, QuerySet)

    def test_get_privileged_filters_pengawasan_questions(self):
        admin = CustomUser.objects.create_user(username="adminuser", email='adminuser@gmail.com', role="admin", password="pass")
        pengawasan_q = Question.objects.create(
            title="Pengawasan Only",
            question="Isi",
            mode=Question.ModeChoices.PENGAWASAN,
            user=admin
        )
        with patch.object(self.service, '_resolve_filter_type') as mock_resolve:
            mock_resolve.return_value = Q(id=pengawasan_q.id)
            result = self.service.get_privileged('judul', admin, 'Pengawasan')
            self.assertIn(pengawasan_q, result)

    def test_get_field_values_as_admin_includes_pengguna(self):
        self.user_admin.role = "admin"
        self.user_admin.save()
        
        response = self.service.get_field_values(self.user_admin)

        self.assertIn(self.user.username, response.pengguna)
        self.assertIn("Test Title", response.judul)
        self.assertIn("test_tag", response.topik)
    
    def test_get_privileged_with_empty_filter_and_keyword(self):
        self.question.mode = Question.ModeChoices.PENGAWASAN
        self.question.save()

        self.user_admin.role = "admin"
        self.user_admin.save()

        result = self.service.get_privileged(q_filter="", keyword="", user=self.user_admin)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.question)


class TestUpdateQuestion(TestCase):
    def setUp(self):
        self.service = QuestionService()
        self.question_id = uuid.uuid4()
        self.user = CustomUser.objects.create(username="test_user", email="user@test.com")
        self.user.set_password("password")
        self.user.save()

        self.other_user = CustomUser.objects.create(username="other_user", email="other@test.com")
        self.other_user.set_password("password")
        self.other_user.save()

        self.question = Question.objects.create(
            id=self.question_id,
            title="Old Title",
            question="Old Question",
            mode="OLD",
            user=self.user,
        )
        self.tag1 = Tag.objects.create(name="tag1")
        self.question.tags.add(self.tag1)

    def test_update_question_success(self):
        # Arrange
        new_title = "New Title"
        new_mode = "NEW"
        new_tags = ["tag2", "tag3"]
        tag2 = Tag.objects.create(name="tag2")
        tag3 = Tag.objects.create(name="tag3")

        with patch.object(self.service, '_validate_tags') as mock_validate_tags:
            mock_validate_tags.return_value = [tag2, tag3]

            # Act
            result = self.service.update_question(
                user=self.user,
                pk=self.question_id,
                title=new_title,
                mode=new_mode,
                tags=new_tags
            )

            # Assert
            self.assertEqual(result.title, new_title)
            self.assertEqual(result.mode, new_mode)
            self.assertSetEqual(set(result.tags.all()), {tag2, tag3})

    def test_update_question_not_found(self):
        # Arrange
        random_id = uuid.uuid4()

        # Act + Assert
        with self.assertRaises(NotFoundRequestException) as ctx:
            self.service.update_question(user=self.user, pk=random_id, title="New Title")

        self.assertEqual(str(ctx.exception), ErrorMsg.NOT_FOUND)

    def test_update_question_forbidden_user(self):
        # Act + Assert
        with self.assertRaises(ForbiddenRequestException) as ctx:
            self.service.update_question(
                user=self.other_user,
                pk=self.question_id,
                title="Another Title"
            )

        self.assertEqual(str(ctx.exception), ErrorMsg.FORBIDDEN_UPDATE)

    def test_update_question_no_changes(self):
        # Act + Assert
        with self.assertRaises(ValueNotUpdatedException) as ctx:
            self.service.update_question(
                user=self.user,
                pk=self.question_id,
                title="Old Title",
                question="Old Question",
                mode="OLD",
                tags=["tag1"]  # same as existing
            )

        self.assertEqual(str(ctx.exception), ErrorMsg.VALUE_NOT_UPDATED)