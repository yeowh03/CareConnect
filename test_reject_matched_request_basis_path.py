"""
Basis Path Testing for reject_matched_request() method in RequestController
Using White Box Testing methodology with 7 independent paths identified.
"""

import unittest
from unittest.mock import Mock, patch
from flask import Flask
from backend.controllers.requests_controller import RequestController

class TestRejectMatchedRequestBasisPath(unittest.TestCase):
    
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        
    @patch('backend.controllers.requests_controller.get_current_user')
    def test_path_1_unauthorized_user(self, mock_get_user):
        """Path 1: User not authenticated (get_current_user returns None)"""
        mock_get_user.return_value = None
        
        with self.app.test_request_context('/reject', method='POST', json={}):
            result, status = RequestController.reject_matched_request()
            
        self.assertEqual(status, 401)
        self.assertEqual(result.json['message'], "Unauthorized")
    
    @patch('backend.controllers.requests_controller.get_current_user')
    def test_path_2_missing_required_fields(self, mock_get_user):
        """Path 2: Missing required fields (i, location, r)"""
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_get_user.return_value = mock_user
        
        test_data = {
            "i": "",  # Missing item name
            "location": "CC1",
            "r": 123
        }
        
        with self.app.test_request_context('/reject', method='POST', json=test_data):
            result, status = RequestController.reject_matched_request()
            
        self.assertEqual(status, 400)
        self.assertEqual(result.json['message'], "i, location and r are required")
    
    @patch('backend.controllers.requests_controller.Request')
    @patch('backend.controllers.requests_controller.get_current_user')
    def test_path_3_request_not_found(self, mock_get_user, mock_request_model):
        """Path 3: Request not found in database"""
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_get_user.return_value = mock_user
        
        mock_request_model.query.get.return_value = None  # Request not found
        
        test_data = {
            "i": "Rice",
            "location": "CC1",
            "r": 999  # Non-existent request ID
        }
        
        with self.app.test_request_context('/reject', method='POST', json=test_data):
            result, status = RequestController.reject_matched_request()
            
        self.assertEqual(status, 404)
        self.assertEqual(result.json['message'], "Request not found")
    
    @patch('backend.controllers.requests_controller.Request')
    @patch('backend.controllers.requests_controller.get_current_user')
    def test_path_4_forbidden_access(self, mock_get_user, mock_request_model):
        """Path 4: User trying to reject someone else's request"""
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_get_user.return_value = mock_user
        
        mock_request = Mock()
        mock_request.requester_email = "other@example.com"  # Different user
        mock_request_model.query.get.return_value = mock_request
        
        test_data = {
            "i": "Rice",
            "location": "CC1",
            "r": 123
        }
        
        with self.app.test_request_context('/reject', method='POST', json=test_data):
            result, status = RequestController.reject_matched_request()
            
        self.assertEqual(status, 403)
        self.assertEqual(result.json['message'], "Forbidden")
    
    @patch('backend.controllers.requests_controller.Request')
    @patch('backend.controllers.requests_controller.get_current_user')
    def test_path_5_invalid_status(self, mock_get_user, mock_request_model):
        """Path 5: Request status is not 'Matched'"""
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_get_user.return_value = mock_user
        
        mock_request = Mock()
        mock_request.requester_email = "test@example.com"
        mock_request.status = "Pending"  # Not Matched
        mock_request_model.query.get.return_value = mock_request
        
        test_data = {
            "i": "Rice",
            "location": "CC1",
            "r": 123
        }
        
        with self.app.test_request_context('/reject', method='POST', json=test_data):
            result, status = RequestController.reject_matched_request()
            
        self.assertEqual(status, 400)
        self.assertEqual(result.json['message'], "Only Matched requests can be rejected")
    
    @patch('backend.controllers.requests_controller.run_allocation')
    @patch('backend.controllers.requests_controller.db')
    @patch('backend.controllers.requests_controller.Item')
    @patch('backend.controllers.requests_controller.Reservation')
    @patch('backend.controllers.requests_controller.Request')
    @patch('backend.controllers.requests_controller.get_current_user')
    def test_path_6_database_exception(self, mock_get_user, mock_request_model, mock_reservation_model, 
                                     mock_item_model, mock_db, mock_run_alloc):
        """Path 6: Database exception during rejection process"""
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_get_user.return_value = mock_user
        
        mock_request = Mock()
        mock_request.requester_email = "test@example.com"
        mock_request.status = "Matched"
        mock_request.id = 123
        mock_request_model.query.get.return_value = mock_request
        
        # Mock database exception
        mock_db.session.commit.side_effect = Exception("Database error")
        
        test_data = {
            "i": "Rice",
            "location": "CC1",
            "r": 123
        }
        
        with self.app.test_request_context('/reject', method='POST', json=test_data):
            result, status = RequestController.reject_matched_request()
            
        self.assertEqual(status, 500)
        self.assertEqual(result.json['message'], "Failed to reject request")
        mock_db.session.rollback.assert_called_once()
    
    @patch('backend.controllers.requests_controller.run_allocation')
    @patch('backend.controllers.requests_controller.db')
    @patch('backend.controllers.requests_controller.Item')
    @patch('backend.controllers.requests_controller.Reservation')
    @patch('backend.controllers.requests_controller.Request')
    @patch('backend.controllers.requests_controller.get_current_user')
    def test_path_7_successful_rejection(self, mock_get_user, mock_request_model, mock_reservation_model,
                                       mock_item_model, mock_db, mock_run_alloc):
        """Path 7: Successful request rejection (happy path)"""
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_get_user.return_value = mock_user
        
        mock_request = Mock()
        mock_request.requester_email = "test@example.com"
        mock_request.status = "Matched"
        mock_request.id = 123
        mock_request_model.query.get.return_value = mock_request
        
        # Mock reservations
        mock_reservation1 = Mock()
        mock_reservation1.item_id = 1
        mock_reservation2 = Mock()
        mock_reservation2.item_id = 2
        mock_reservation_model.query.filter_by.return_value.all.return_value = [mock_reservation1, mock_reservation2]
        
        # Mock items
        mock_item1 = Mock()
        mock_item1.id = 1
        mock_item2 = Mock()
        mock_item2.id = 2
        mock_item_model.query.get.side_effect = [mock_item1, mock_item2]
        
        test_data = {
            "i": "Rice",
            "location": "CC1",
            "r": 123
        }
        
        with self.app.test_request_context('/reject', method='POST', json=test_data):
            result, status = RequestController.reject_matched_request()
            
        self.assertEqual(status, 200)
        self.assertIn("Request rejected", result.json['message'])
        self.assertEqual(result.json['rejected_request_id'], 123)
        self.assertEqual(result.json['freed_items'], [1, 2])
        
        # Verify items were set to Available
        self.assertEqual(mock_item1.status, "Available")
        self.assertEqual(mock_item2.status, "Available")
        
        # Verify database operations
        mock_db.session.delete.assert_called()  # Should delete reservations and request
        mock_db.session.commit.assert_called_once()
        mock_run_alloc.assert_called_once()

if __name__ == '__main__':
    unittest.main()