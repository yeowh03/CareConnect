"""
Basis Path Testing for create_request() method in RequestController
Using White Box Testing methodology with 7 independent paths identified.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from flask import Flask
from backend.controllers.requests_controller import RequestController

class TestCreateRequestBasisPath(unittest.TestCase):
    
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        
    @patch('backend.controllers.requests_controller.get_current_user')
    def test_path_1_unauthorized_user(self, mock_get_user):
        """Path 1: User not authenticated (get_current_user returns None)"""
        mock_get_user.return_value = None
        
        with self.app.test_request_context('/requests', method='POST', json={}):
            result, status = RequestController.create_request()
            
        self.assertEqual(status, 401)
        self.assertEqual(result.json['message'], "Unauthorized")
    
    @patch('backend.controllers.requests_controller.check_and_broadcast_for_cc')
    @patch('backend.controllers.requests_controller.run_allocation')
    @patch('backend.controllers.requests_controller.db')
    @patch('backend.controllers.requests_controller.Request')
    @patch('backend.controllers.requests_controller.get_current_user')
    def test_path_2_missing_category(self, mock_get_user, mock_request_model, mock_db, mock_run_alloc, mock_broadcast):
        """Path 2: Missing request_category field"""
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_get_user.return_value = mock_user
        
        test_data = {
            "request_category": "",  # Empty category
            "request_item": "Food",
            "request_quantity": 1,
            "location": "CC1"
        }
        
        with self.app.test_request_context('/requests', method='POST', json=test_data):
            result, status = RequestController.create_request()
            
        self.assertEqual(status, 400)
        self.assertEqual(result.json['message'], "request_category is required")
    
    @patch('backend.controllers.requests_controller.check_and_broadcast_for_cc')
    @patch('backend.controllers.requests_controller.run_allocation')
    @patch('backend.controllers.requests_controller.db')
    @patch('backend.controllers.requests_controller.Request')
    @patch('backend.controllers.requests_controller.get_current_user')
    def test_path_3_missing_item(self, mock_get_user, mock_request_model, mock_db, mock_run_alloc, mock_broadcast):
        """Path 3: Missing request_item field"""
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_get_user.return_value = mock_user
        
        test_data = {
            "request_category": "Food",
            "request_item": "",  # Empty item
            "request_quantity": 1,
            "location": "CC1"
        }
        
        with self.app.test_request_context('/requests', method='POST', json=test_data):
            result, status = RequestController.create_request()
            
        self.assertEqual(status, 400)
        self.assertEqual(result.json['message'], "request_item is required")
    
    @patch('backend.controllers.requests_controller.check_and_broadcast_for_cc')
    @patch('backend.controllers.requests_controller.run_allocation')
    @patch('backend.controllers.requests_controller.db')
    @patch('backend.controllers.requests_controller.Request')
    @patch('backend.controllers.requests_controller.get_current_user')
    def test_path_4_invalid_quantity(self, mock_get_user, mock_request_model, mock_db, mock_run_alloc, mock_broadcast):
        """Path 4: Invalid request_quantity (non-positive integer)"""
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_get_user.return_value = mock_user
        
        test_data = {
            "request_category": "Food",
            "request_item": "Rice",
            "request_quantity": 0,  # Invalid quantity
            "location": "CC1"
        }
        
        with self.app.test_request_context('/requests', method='POST', json=test_data):
            result, status = RequestController.create_request()
            
        self.assertEqual(status, 400)
        self.assertEqual(result.json['message'], "request_quantity must be a positive integer")
    
    @patch('backend.controllers.requests_controller.check_and_broadcast_for_cc')
    @patch('backend.controllers.requests_controller.run_allocation')
    @patch('backend.controllers.requests_controller.db')
    @patch('backend.controllers.requests_controller.Request')
    @patch('backend.controllers.requests_controller.get_current_user')
    def test_path_5_missing_location(self, mock_get_user, mock_request_model, mock_db, mock_run_alloc, mock_broadcast):
        """Path 5: Missing location field"""
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_get_user.return_value = mock_user
        
        test_data = {
            "request_category": "Food",
            "request_item": "Rice",
            "request_quantity": 1,
            "location": ""  # Empty location
        }
        
        with self.app.test_request_context('/requests', method='POST', json=test_data):
            result, status = RequestController.create_request()
            
        self.assertEqual(status, 400)
        self.assertEqual(result.json['message'], "location (CC) is required")
    
    @patch('backend.controllers.requests_controller.check_and_broadcast_for_cc')
    @patch('backend.controllers.requests_controller.run_allocation')
    @patch('backend.controllers.requests_controller.db')
    @patch('backend.controllers.requests_controller.Request')
    @patch('backend.controllers.requests_controller.get_current_user')
    def test_path_6_database_exception(self, mock_get_user, mock_request_model, mock_db, mock_run_alloc, mock_broadcast):
        """Path 6: Database exception during request creation"""
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_get_user.return_value = mock_user
        
        # Mock database exception
        mock_db.session.commit.side_effect = Exception("Database error")
        
        test_data = {
            "request_category": "Food",
            "request_item": "Rice",
            "request_quantity": 1,
            "location": "CC1"
        }
        
        with self.app.test_request_context('/requests', method='POST', json=test_data):
            result, status = RequestController.create_request()
            
        self.assertEqual(status, 500)
        self.assertEqual(result.json['message'], "Failed to create request")
        mock_db.session.rollback.assert_called_once()
    
    @patch('backend.controllers.requests_controller.check_and_broadcast_for_cc')
    @patch('backend.controllers.requests_controller.run_allocation')
    @patch('backend.controllers.requests_controller.db')
    @patch('backend.controllers.requests_controller.Request')
    @patch('backend.controllers.requests_controller.get_current_user')
    def test_path_7_successful_creation(self, mock_get_user, mock_request_model, mock_db, mock_run_alloc, mock_broadcast):
        """Path 7: Successful request creation (happy path)"""
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_get_user.return_value = mock_user
        
        # Mock successful request creation
        mock_request_instance = Mock()
        mock_request_instance.id = 123
        mock_request_instance.status = "Pending"
        mock_request_instance.location = "CC1"
        mock_request_instance.request_item = "Rice"
        mock_request_instance.request_quantity = 2
        mock_request_instance.allocation = 0
        mock_request_model.return_value = mock_request_instance
        
        test_data = {
            "request_category": "Food",
            "request_item": "Rice",
            "request_quantity": 2,
            "location": "CC1"
        }
        
        with self.app.test_request_context('/requests', method='POST', json=test_data):
            result, status = RequestController.create_request()
            
        self.assertEqual(status, 201)
        self.assertEqual(result.json['id'], 123)
        self.assertEqual(result.json['status'], "Pending")
        self.assertEqual(result.json['location'], "CC1")
        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_called_once()
        mock_run_alloc.assert_called_once()
        mock_broadcast.assert_called_once_with("CC1")

if __name__ == '__main__':
    unittest.main()