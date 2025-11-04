"""Test Cases for RequestController using Equivalence Class and Boundary Value Testing.

This module contains comprehensive test cases for the RequestController class,
designed using equivalence class partitioning and boundary value analysis techniques.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
from backend.controllers.requests_controller import RequestController
from backend.models import Request, User, Client, Manager, Item, Donation, Reservation


class TestRequestControllerEquivalenceClasses:
    """Test cases using Equivalence Class Partitioning technique."""
    
    # ========== CREATE REQUEST TESTS ==========
    
    def test_create_request_valid_equivalence_classes(self):
        """Test create_request with valid input equivalence classes."""
        
        # Valid Category Equivalence Classes
        valid_categories = ["Food", "Drinks", "Furnitures", "Electronics", "Essentials"]
        
        # Valid Quantity Equivalence Classes  
        valid_quantities = [1, 5, 100, 999]
        
        # Valid String Equivalence Classes
        valid_items = ["Rice", "Water Bottle", "Chair", "Laptop", "Soap"]
        valid_locations = ["CC1", "Community Club A", "North CC"]
        
        for category in valid_categories:
            for quantity in valid_quantities:
                for item in valid_items:
                    for location in valid_locations:
                        with patch('backend.controllers.requests_controller.get_current_user') as mock_user, \
                             patch('backend.controllers.requests_controller.request') as mock_request, \
                             patch('backend.controllers.requests_controller.db') as mock_db, \
                             patch('backend.controllers.requests_controller.run_allocation'), \
                             patch('backend.controllers.requests_controller.check_and_broadcast_for_cc'):
                            
                            mock_user.return_value = Mock(email="test@example.com")
                            mock_request.get_json.return_value = {
                                "request_category": category,
                                "request_item": item,
                                "request_quantity": quantity,
                                "location": location
                            }
                            
                            response, status = RequestController.create_request()
                            assert status == 201
    
    def test_create_request_invalid_equivalence_classes(self):
        """Test create_request with invalid input equivalence classes."""
        
        # Invalid Category Equivalence Class
        invalid_categories = ["", "   ", "InvalidCategory", None]
        
        # Invalid Quantity Equivalence Classes
        invalid_quantities = [0, -1, -100, "abc", None, 1.5]
        
        # Invalid String Equivalence Classes  
        invalid_strings = ["", "   ", None]
        
        test_cases = [
            # Invalid categories
            *[{"request_category": cat, "request_item": "Rice", "request_quantity": 1, "location": "CC1"} 
              for cat in invalid_categories],
            
            # Invalid quantities
            *[{"request_category": "Food", "request_item": "Rice", "request_quantity": qty, "location": "CC1"} 
              for qty in invalid_quantities],
            
            # Invalid items
            *[{"request_category": "Food", "request_item": item, "request_quantity": 1, "location": "CC1"} 
              for item in invalid_strings],
            
            # Invalid locations
            *[{"request_category": "Food", "request_item": "Rice", "request_quantity": 1, "location": loc} 
              for loc in invalid_strings]
        ]
        
        for test_data in test_cases:
            with patch('backend.controllers.requests_controller.get_current_user') as mock_user, \
                 patch('backend.controllers.requests_controller.request') as mock_request:
                
                mock_user.return_value = Mock(email="test@example.com")
                mock_request.get_json.return_value = test_data
                
                response, status = RequestController.create_request()
                assert status == 400
    
    # ========== UPDATE REQUEST TESTS ==========
    
    def test_update_request_status_equivalence_classes(self):
        """Test update_pending_request with different status equivalence classes."""
        
        # Valid Status Equivalence Class: Only "Pending" allows updates
        with patch('backend.controllers.requests_controller.get_current_user') as mock_user, \
             patch('backend.controllers.requests_controller.Request') as mock_request_model, \
             patch('backend.controllers.requests_controller.Reservation') as mock_reservation, \
             patch('backend.controllers.requests_controller.request') as mock_request:
            
            mock_user.return_value = Mock(email="test@example.com")
            mock_req = Mock(
                id=1, 
                requester_email="test@example.com", 
                status="Pending",
                allocation=0,
                request_category="Food",
                request_item="Rice", 
                request_quantity=1,
                location="CC1"
            )
            mock_request_model.query.get.return_value = mock_req
            mock_reservation.query.filter_by.return_value.count.return_value = 0
            mock_request.get_json.return_value = {"request_quantity": 2}
            
            response, status = RequestController.update_pending_request(1)
            assert status == 200
        
        # Invalid Status Equivalence Classes: Non-pending statuses should fail
        invalid_statuses = ["Matched", "Completed", "Expired"]
        
        for invalid_status in invalid_statuses:
            with patch('backend.controllers.requests_controller.get_current_user') as mock_user, \
                 patch('backend.controllers.requests_controller.Request') as mock_request_model:
                
                mock_user.return_value = Mock(email="test@example.com")
                mock_req = Mock(
                    id=1, 
                    requester_email="test@example.com", 
                    status=invalid_status
                )
                mock_request_model.query.get.return_value = mock_req
                
                response, status = RequestController.update_pending_request(1)
                assert status == 400
    
    # ========== AUTHORIZATION TESTS ==========
    
    def test_authorization_equivalence_classes(self):
        """Test authorization equivalence classes across all methods."""
        
        # Unauthorized User Equivalence Class
        with patch('backend.controllers.requests_controller.get_current_user') as mock_user:
            mock_user.return_value = None
            
            methods_to_test = [
                (RequestController.create_request, []),
                (RequestController.my_requests, []),
                (RequestController.get_my_request, [1]),
                (RequestController.update_pending_request, [1]),
                (RequestController.delete_pending_request, [1]),
                (RequestController.manager_matched_requests, []),
                (RequestController.manager_complete_request, [1]),
                (RequestController.reject_matched_request, [])
            ]
            
            for method, args in methods_to_test:
                response, status = method(*args)
                assert status == 401
        
        # Manager Role Equivalence Class for manager-only methods
        with patch('backend.controllers.requests_controller.get_current_user') as mock_user:
            mock_user.return_value = Mock(email="manager@example.com", role="C")  # Client role
            
            manager_methods = [
                (RequestController.manager_matched_requests, []),
                (RequestController.manager_complete_request, [1])
            ]
            
            for method, args in manager_methods:
                response, status = method(*args)
                assert status == 403


class TestRequestControllerBoundaryValues:
    """Test cases using Boundary Value Analysis technique."""
    
    def test_request_quantity_boundary_values(self):
        """Test request_quantity boundary values."""
        
        # Boundary values for request_quantity
        boundary_values = [
            (0, 400),    # Just below minimum valid (invalid)
            (1, 201),    # Minimum valid value
            (2, 201),    # Just above minimum valid
            (999, 201),  # Large valid value
            (1000, 201), # Very large valid value
            (-1, 400),   # Negative boundary (invalid)
        ]
        
        for quantity, expected_status in boundary_values:
            with patch('backend.controllers.requests_controller.get_current_user') as mock_user, \
                 patch('backend.controllers.requests_controller.request') as mock_request, \
                 patch('backend.controllers.requests_controller.db') as mock_db, \
                 patch('backend.controllers.requests_controller.run_allocation'), \
                 patch('backend.controllers.requests_controller.check_and_broadcast_for_cc'):
                
                mock_user.return_value = Mock(email="test@example.com")
                mock_request.get_json.return_value = {
                    "request_category": "Food",
                    "request_item": "Rice",
                    "request_quantity": quantity,
                    "location": "CC1"
                }
                
                response, status = RequestController.create_request()
                assert status == expected_status
    
    def test_string_length_boundary_values(self):
        """Test string field length boundary values."""
        
        # Test empty strings (boundary case)
        empty_string_cases = [
            {"request_category": "", "request_item": "Rice", "location": "CC1"},
            {"request_category": "Food", "request_item": "", "location": "CC1"},
            {"request_category": "Food", "request_item": "Rice", "location": ""}
        ]
        
        for test_case in empty_string_cases:
            test_case["request_quantity"] = 1
            
            with patch('backend.controllers.requests_controller.get_current_user') as mock_user, \
                 patch('backend.controllers.requests_controller.request') as mock_request:
                
                mock_user.return_value = Mock(email="test@example.com")
                mock_request.get_json.return_value = test_case
                
                response, status = RequestController.create_request()
                assert status == 400
        
        # Test whitespace-only strings (boundary case)
        whitespace_cases = [
            {"request_category": "   ", "request_item": "Rice", "location": "CC1"},
            {"request_category": "Food", "request_item": "   ", "location": "CC1"},
            {"request_category": "Food", "request_item": "Rice", "location": "   "}
        ]
        
        for test_case in whitespace_cases:
            test_case["request_quantity"] = 1
            
            with patch('backend.controllers.requests_controller.get_current_user') as mock_user, \
                 patch('backend.controllers.requests_controller.request') as mock_request:
                
                mock_user.return_value = Mock(email="test@example.com")
                mock_request.get_json.return_value = test_case
                
                response, status = RequestController.create_request()
                assert status == 400
    
    def test_request_id_boundary_values(self):
        """Test request ID boundary values."""
        
        # Test with various ID boundary values
        id_boundary_cases = [
            (0, 404),      # Zero ID
            (1, 200),      # Minimum positive ID
            (-1, 404),     # Negative ID
            (999999, 404), # Very large ID (not found)
        ]
        
        for req_id, expected_status in id_boundary_cases:
            with patch('backend.controllers.requests_controller.get_current_user') as mock_user, \
                 patch('backend.controllers.requests_controller.Request') as mock_request_model:
                
                mock_user.return_value = Mock(email="test@example.com")
                
                if req_id == 1:
                    # Valid case - request exists and belongs to user
                    mock_req = Mock(
                        id=1,
                        requester_email="test@example.com",
                        request_category="Food",
                        request_item="Rice",
                        request_quantity=1,
                        allocation=0,
                        location="CC1",
                        status="Pending",
                        created_at=datetime.now(timezone.utc)
                    )
                    mock_request_model.query.get.return_value = mock_req
                else:
                    # Invalid cases - request not found
                    mock_request_model.query.get.return_value = None
                
                response, status = RequestController.get_my_request(req_id)
                assert status == expected_status
    
    def test_allocation_boundary_values(self):
        """Test allocation field boundary values for update operations."""
        
        # Test cases where allocation affects update permission
        allocation_cases = [
            (0, True),   # No allocation - update allowed
            (1, False),  # Has allocation - update blocked
            (5, False),  # Multiple allocations - update blocked
        ]
        
        for allocation_value, should_allow_update in allocation_cases:
            with patch('backend.controllers.requests_controller.get_current_user') as mock_user, \
                 patch('backend.controllers.requests_controller.Request') as mock_request_model, \
                 patch('backend.controllers.requests_controller.Reservation') as mock_reservation, \
                 patch('backend.controllers.requests_controller.request') as mock_request, \
                 patch('backend.controllers.requests_controller.db'):
                
                mock_user.return_value = Mock(email="test@example.com")
                mock_req = Mock(
                    id=1,
                    requester_email="test@example.com",
                    status="Pending",
                    allocation=allocation_value,
                    request_category="Food",
                    request_item="Rice",
                    request_quantity=1,
                    location="CC1"
                )
                mock_request_model.query.get.return_value = mock_req
                mock_reservation.query.filter_by.return_value.count.return_value = 0
                mock_request.get_json.return_value = {"request_quantity": 2}
                
                response, status = RequestController.update_pending_request(1)
                
                if should_allow_update:
                    assert status == 200
                else:
                    assert status == 400


class TestRequestControllerEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_database_error_handling(self):
        """Test database error handling across methods."""
        
        with patch('backend.controllers.requests_controller.get_current_user') as mock_user, \
             patch('backend.controllers.requests_controller.request') as mock_request, \
             patch('backend.controllers.requests_controller.db') as mock_db:
            
            mock_user.return_value = Mock(email="test@example.com")
            mock_request.get_json.return_value = {
                "request_category": "Food",
                "request_item": "Rice", 
                "request_quantity": 1,
                "location": "CC1"
            }
            
            # Simulate database error
            mock_db.session.commit.side_effect = Exception("Database error")
            
            response, status = RequestController.create_request()
            assert status == 500
            mock_db.session.rollback.assert_called_once()
    
    def test_ownership_validation(self):
        """Test request ownership validation."""
        
        with patch('backend.controllers.requests_controller.get_current_user') as mock_user, \
             patch('backend.controllers.requests_controller.Request') as mock_request_model:
            
            mock_user.return_value = Mock(email="user1@example.com")
            
            # Request belongs to different user
            mock_req = Mock(
                id=1,
                requester_email="user2@example.com",  # Different owner
                status="Pending"
            )
            mock_request_model.query.get.return_value = mock_req
            
            response, status = RequestController.get_my_request(1)
            assert status == 404  # Should return not found for security
    
    def test_manager_community_validation(self):
        """Test manager community club validation."""
        
        with patch('backend.controllers.requests_controller.get_current_user') as mock_user, \
             patch('backend.controllers.requests_controller.Manager') as mock_manager_model, \
             patch('backend.controllers.requests_controller.Request') as mock_request_model:
            
            mock_user.return_value = Mock(email="manager@example.com", role="M")
            
            # Manager belongs to different CC
            mock_mgr = Mock(cc="CC1")
            mock_manager_model.query.get.return_value = mock_mgr
            
            mock_req = Mock(
                id=1,
                location="CC2",  # Different CC
                status="Matched"
            )
            mock_request_model.query.get.return_value = mock_req
            
            response, status = RequestController.manager_complete_request(1)
            assert status == 403
    
    def test_json_parsing_edge_cases(self):
        """Test JSON parsing edge cases."""
        
        with patch('backend.controllers.requests_controller.get_current_user') as mock_user, \
             patch('backend.controllers.requests_controller.request') as mock_request:
            
            mock_user.return_value = Mock(email="test@example.com")
            
            # Test with None JSON
            mock_request.get_json.return_value = None
            
            response, status = RequestController.create_request()
            assert status == 400
            
            # Test with empty JSON
            mock_request.get_json.return_value = {}
            
            response, status = RequestController.create_request()
            assert status == 400


if __name__ == "__main__":
    pytest.main([__file__])