import unittest
from unittest.mock import patch, MagicMock
import os, jwt
import xml.etree.ElementTree as ET

from django.test import TestCase

from sso_ui.config import SSOJWTConfig
from sso_ui.ticket import validate_ticket, ValidateTicketError
from sso_ui.token import create_token, decode_token

class TestValidateTicket(TestCase):
    def setUp(self):
        self.config = MagicMock()
        self.config.cas_url = 'https://sso.ui.ac.id/cas2'
        self.config.service_url = 'http://localhost:3000/auth/callback'
        
        # Success XML
        self.success_xml = '''
        <cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'>
            <cas:authenticationSuccess>
                <cas:user>username</cas:user>
                <cas:attributes>
                    <cas:ldap_cn>User Name</cas:ldap_cn>
                    <cas:kd_org>Faculty</cas:kd_org>
                    <cas:peran_user>Student</cas:peran_user>
                    <cas:nama>User Name</cas:nama>
                    <cas:npm>2206081534</cas:npm>
                </cas:attributes>
            </cas:authenticationSuccess>
        </cas:serviceResponse>
        '''
        
        # Failure XML
        self.failure_xml = '''
        <cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'>
            <cas:authenticationFailure code="INVALID_TICKET">
                Ticket not recognized
            </cas:authenticationFailure>
        </cas:serviceResponse>
        '''
        
    @patch('sso_ui.ticket.requests.get')
    def test_validate_ticket_success(self, mock_get):
        """Test successful ticket validation"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.text = self.success_xml
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Call validate_ticket
        result = validate_ticket(self.config, 'valid_ticket')
        
        # Verify the result
        self.assertIn('authentication_success', result)
        auth_success = result['authentication_success']
        self.assertEqual(auth_success['user'], 'username')
        self.assertEqual(auth_success['attributes']['npm'], '2206081534')
        self.assertEqual(auth_success['attributes']['nama'], 'User Name')
        
        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            f"{self.config.cas_url}/serviceValidate?ticket=valid_ticket&service={self.config.service_url}",
            headers={"User-Agent": "Python-Requests"}
        )
        
    @patch('sso_ui.ticket.requests.get')
    def test_validate_ticket_xml_parse_error(self, mock_get):
        """Test ticket validation with XML parsing error"""
        # Mock the response with invalid XML
        mock_response = MagicMock()
        mock_response.text = 'Not an XML'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Call validate_ticket
        with self.assertRaises(ValidateTicketError) as context:
            validate_ticket(self.config, 'invalid_ticket')
            
        # Verify error message
        self.assertEqual(str(context.exception), 'XMLParsingError')
        
    @patch('sso_ui.ticket.requests.get')
    def test_validate_ticket_authentication_failed(self, mock_get):
        """Test ticket validation with authentication failure"""
        # Mock the response with failure XML
        mock_response = MagicMock()
        mock_response.text = self.failure_xml
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Call validate_ticket
        with self.assertRaises(ValidateTicketError) as context:
            validate_ticket(self.config, 'invalid_ticket')
            
        # Verify error message
        self.assertEqual(str(context.exception), 'AuthenticationFailed')
        
    @patch('sso_ui.ticket.requests.get')
    def test_validate_ticket_missing_fields(self, mock_get):
        """Test ticket validation with missing fields in the XML"""
        # Create XML with missing attributes
        xml = '''
        <cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'>
            <cas:authenticationSuccess>
                <cas:user>username</cas:user>
                <!-- Missing attributes element -->
            </cas:authenticationSuccess>
        </cas:serviceResponse>
        '''
        
        # Mock the response
        mock_response = MagicMock()
        mock_response.text = xml
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Call validate_ticket
        with self.assertRaises(ValidateTicketError) as context:
            validate_ticket(self.config, 'invalid_ticket')
            
        # Verify error message
        self.assertEqual(str(context.exception), 'XMLParsingError')


class TestSSOToken(TestCase):
    def setUp(self):
        self.config = MagicMock()
        # Use fixed values instead of env variables to avoid None type errors
        self.config.access_token_exp_time = 3600
        self.config.refresh_token_exp_time = 86400
        self.config.access_token_secret_key = "test_access_secret"
        self.config.refresh_token_secret_key = "test_refresh_secret"

        # Sample service response
        self.service_response = {
            "authentication_success": {
                "user": "username",
                "attributes": {
                    "npm": "2206081534",
                    "nama": "User Name"
                }
            }
        }
        
    @patch('sso_ui.token.jwt')
    def test_create_token_access(self, mock_jwt):
        """Test creating an access token"""
        # Mock jwt.encode
        mock_jwt.encode.return_value = 'encoded_access_token'
        
        # Call create_token
        token = create_token(self.config, 'access_token', self.service_response)
        
        # Verify the result
        self.assertEqual(token, 'encoded_access_token')
        
        # Verify jwt.encode was called with correct parameters
        mock_jwt.encode.assert_called_once()
        args, kwargs = mock_jwt.encode.call_args
        
        # Check payload
        payload = args[0]
        self.assertEqual(payload['username'], 'username')
        self.assertEqual(payload['attributes'], self.service_response['authentication_success']['attributes'])
        
        # Check secret key and algorithm
        self.assertEqual(args[1], self.config.access_token_secret_key)
        self.assertEqual(kwargs['algorithm'], 'HS256')
        
    @patch('sso_ui.token.jwt')
    def test_create_token_refresh(self, mock_jwt):
        """Test creating a refresh token"""
        # Mock jwt.encode
        mock_jwt.encode.return_value = 'encoded_refresh_token'
        
        # Call create_token
        token = create_token(self.config, 'refresh_token', self.service_response)
        
        # Verify the result
        self.assertEqual(token, 'encoded_refresh_token')
        
        # Verify jwt.encode was called with correct parameters
        mock_jwt.encode.assert_called_once()
        args, _ = mock_jwt.encode.call_args
        
        # Check secret key
        self.assertEqual(args[1], self.config.refresh_token_secret_key)
        
    def test_create_token_invalid_service_response(self):
        """Test creating a token with invalid service response"""
        # Call create_token with empty response
        with self.assertRaises(ValueError):
            create_token(self.config, 'access_token', {})
            
    @patch('sso_ui.token.jwt')
    def test_decode_token_access(self, mock_jwt):
        """Test decoding an access token"""
        # Mock jwt.decode
        expected_payload = {
            'username': 'username',
            'attributes': {'npm': '2206081534'},
            'exp': 9999999999  # Far future timestamp
        }
        mock_jwt.decode.return_value = expected_payload
        
        # Call decode_token
        payload = decode_token(self.config, 'access_token', 'encoded_token')
        
        # Verify the result
        self.assertEqual(payload, expected_payload)
        
        # Verify jwt.decode was called with correct parameters
        mock_jwt.decode.assert_called_once_with(
            'encoded_token', 
            self.config.access_token_secret_key, 
            algorithms=['HS256']
        )
        
    @patch('sso_ui.token.jwt')
    def test_decode_token_refresh(self, mock_jwt):
        """Test decoding a refresh token"""
        # Mock jwt.decode
        expected_payload = {
            'username': 'username',
            'attributes': {'npm': '2206081534'},
            'exp': 9999999999
        }
        mock_jwt.decode.return_value = expected_payload
        
        # Call decode_token
        payload = decode_token(self.config, 'refresh_token', 'encoded_token')
        
        # Verify the result
        self.assertEqual(payload, expected_payload)
        
        # Verify jwt.decode was called with correct parameters
        mock_jwt.decode.assert_called_once_with(
            'encoded_token', 
            self.config.refresh_token_secret_key, 
            algorithms=['HS256']
        )
        
    @patch('sso_ui.token.jwt')
    def test_decode_token_expired(self, mock_jwt):
        """Test decoding an expired token"""
        # Mock jwt.decode
        expired_payload = {
            'username': 'username',
            'attributes': {'npm': '2206081534'},
            'exp': 1  # Expired timestamp
        }
        mock_jwt.decode.return_value = expired_payload
        
        # Call decode_token
        payload = decode_token(self.config, 'access_token', 'encoded_token')
        
        # Verify the result is None (expired)
        self.assertIsNone(payload)
        
        # Verify jwt.decode was called
        mock_jwt.decode.assert_called_once()
        
    @patch('sso_ui.token.jwt.decode')
    def test_decode_token_expired_exception(self, mock_decode):
        """Test decoding a token that throws ExpiredSignatureError"""
        # Mock jwt.decode to raise ExpiredSignatureError
        mock_decode.side_effect = jwt.exceptions.ExpiredSignatureError('Token expired')
        
        # Call decode_token
        payload = decode_token(self.config, 'access_token', 'expired_token')
        
        # Verify the result
        self.assertIsNone(payload)
        
    @patch('sso_ui.token.jwt.decode')
    def test_decode_token_invalid(self, mock_decode):
        """Test decoding an invalid token"""
        # Mock jwt.decode to raise InvalidTokenError
        mock_decode.side_effect = jwt.exceptions.InvalidTokenError('Invalid token')
        
        # Call decode_token
        payload = decode_token(self.config, 'access_token', 'invalid_token')
        
        # Verify the result
        self.assertIsNone(payload)