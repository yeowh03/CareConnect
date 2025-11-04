# RequestController Test Design Documentation

## Testing Strategy Overview

This document outlines the comprehensive test design for the `RequestController` class using **Equivalence Class Partitioning** and **Boundary Value Analysis** testing techniques.

## Testing Techniques Applied

### 1. Equivalence Class Partitioning

Equivalence Class Partitioning divides input data into equivalence classes where all members of a class are expected to be processed similarly by the system.

#### Input Fields and Their Equivalence Classes

| Field | Valid Equivalence Classes | Invalid Equivalence Classes |
|-------|---------------------------|----------------------------|
| `request_category` | ["Food", "Drinks", "Furnitures", "Electronics", "Essentials"] | ["", "   ", "InvalidCategory", None] |
| `request_quantity` | [1, 2, 5, 100, 999] | [0, -1, -100, "abc", None, 1.5] |
| `request_item` | ["Rice", "Water Bottle", "Chair", "Laptop", "Soap"] | ["", "   ", None] |
| `location` | ["CC1", "Community Club A", "North CC"] | ["", "   ", None] |
| `status` | ["Pending"] (for updates) | ["Matched", "Completed", "Expired"] |
| `user_role` | ["C"] (Client) | ["M"] (Manager for client operations) |
| `authorization` | [Valid User Object] | [None, Unauthorized] |

### 2. Boundary Value Analysis

Boundary Value Analysis focuses on testing values at the boundaries of equivalence classes, as errors often occur at these boundaries.

#### Boundary Values Identified

| Field | Boundary Values | Expected Results |
|-------|-----------------|------------------|
| `request_quantity` | 0, 1, 2, 999, 1000, -1 | 0,-1: Invalid (400), Others: Valid (201) |
| `request_id` | 0, 1, -1, 999999 | 0,-1,999999: Not Found (404), 1: Valid (200) |
| `allocation` | 0, 1, 5 | 0: Update Allowed, >0: Update Blocked |
| `string_length` | "", "   ", "a", "valid_string" | Empty/Whitespace: Invalid (400) |

## Test Case Categories

### 1. Create Request Tests (`create_request`)

#### Equivalence Class Tests
- **Valid Input Classes**: Test all valid combinations of categories, quantities, items, and locations
- **Invalid Input Classes**: Test each invalid input type separately
- **Authorization Classes**: Test authorized vs unauthorized users

#### Boundary Value Tests
- **Quantity Boundaries**: Test values 0, 1, 2, 999, 1000, -1
- **String Length Boundaries**: Test empty strings, whitespace-only strings
- **JSON Parsing Boundaries**: Test None and empty JSON objects

### 2. Update Request Tests (`update_pending_request`)

#### Equivalence Class Tests
- **Status Classes**: Only "Pending" requests can be updated
- **Ownership Classes**: Users can only update their own requests
- **Allocation Classes**: Requests with allocations cannot be updated

#### Boundary Value Tests
- **Allocation Boundaries**: Test allocation values 0, 1, 5
- **ID Boundaries**: Test request IDs 0, 1, -1, 999999

### 3. Authorization Tests (All Methods)

#### Equivalence Class Tests
- **User Authentication**: Authorized vs Unauthorized users
- **Role-Based Access**: Manager vs Client role restrictions
- **Ownership Validation**: Own vs other users' requests

### 4. Manager-Specific Tests

#### Equivalence Class Tests
- **Role Validation**: Manager role required for manager operations
- **Community Club Validation**: Managers can only access their CC's requests
- **Status Validation**: Only "Matched" requests can be completed

### 5. Error Handling Tests

#### Edge Cases
- **Database Errors**: Test rollback behavior on database failures
- **Missing Data**: Test behavior with missing or malformed input
- **Concurrent Access**: Test allocation conflicts and race conditions

## Test Implementation Structure

```python
class TestRequestControllerEquivalenceClasses:
    """Tests using Equivalence Class Partitioning"""
    
    def test_create_request_valid_equivalence_classes()
    def test_create_request_invalid_equivalence_classes()
    def test_update_request_status_equivalence_classes()
    def test_authorization_equivalence_classes()

class TestRequestControllerBoundaryValues:
    """Tests using Boundary Value Analysis"""
    
    def test_request_quantity_boundary_values()
    def test_string_length_boundary_values()
    def test_request_id_boundary_values()
    def test_allocation_boundary_values()

class TestRequestControllerEdgeCases:
    """Tests for edge cases and error conditions"""
    
    def test_database_error_handling()
    def test_ownership_validation()
    def test_manager_community_validation()
    def test_json_parsing_edge_cases()
```

## Coverage Analysis

### Methods Tested
- ✅ `create_request()`
- ✅ `update_pending_request(req_id)`
- ✅ `delete_pending_request(req_id)`
- ✅ `get_my_request(req_id)`
- ✅ `my_requests()`
- ✅ `manager_matched_requests()`
- ✅ `manager_complete_request(req_id)`
- ✅ `reject_matched_request()`

### Input Validation Coverage
- ✅ Required field validation
- ✅ Data type validation
- ✅ Range validation
- ✅ Format validation
- ✅ Authorization validation
- ✅ Business rule validation

### Error Condition Coverage
- ✅ Authentication errors (401)
- ✅ Authorization errors (403)
- ✅ Not found errors (404)
- ✅ Validation errors (400)
- ✅ Server errors (500)

## Test Data Strategy

### Valid Test Data Sets
```python
valid_categories = ["Food", "Drinks", "Furnitures", "Electronics", "Essentials"]
valid_quantities = [1, 5, 100, 999]
valid_items = ["Rice", "Water Bottle", "Chair", "Laptop", "Soap"]
valid_locations = ["CC1", "Community Club A", "North CC"]
```

### Invalid Test Data Sets
```python
invalid_categories = ["", "   ", "InvalidCategory", None]
invalid_quantities = [0, -1, -100, "abc", None, 1.5]
invalid_strings = ["", "   ", None]
```

### Boundary Test Data Sets
```python
quantity_boundaries = [0, 1, 2, 999, 1000, -1]
id_boundaries = [0, 1, -1, 999999]
allocation_boundaries = [0, 1, 5]
```

## Expected Benefits

1. **Comprehensive Coverage**: Tests cover all major input combinations and edge cases
2. **Systematic Approach**: Equivalence classes ensure no input category is missed
3. **Boundary Focus**: Boundary value analysis catches common off-by-one errors
4. **Maintainability**: Well-structured tests are easy to maintain and extend
5. **Documentation**: Tests serve as living documentation of expected behavior

## Running the Tests

```bash
# Run all tests
pytest backend/test_request_controller.py -v

# Run specific test class
pytest backend/test_request_controller.py::TestRequestControllerEquivalenceClasses -v

# Run with coverage
pytest backend/test_request_controller.py --cov=backend.controllers.requests_controller
```

## Test Metrics

- **Total Test Cases**: 50+ individual test scenarios
- **Equivalence Classes Covered**: 15+ distinct input classes
- **Boundary Values Tested**: 20+ boundary conditions
- **Error Conditions**: 10+ error scenarios
- **Methods Covered**: 8/8 controller methods (100%)