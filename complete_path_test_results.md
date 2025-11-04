# Complete Path Test Results - Input/Expected/Actual Output

## create_request() Method - All 7 Paths

| Path | Node Sequence | Test Input | Expected Output | Actual Output | Status |
|------|---------------|------------|-----------------|---------------|---------|
| **Path 1** | N1→N2→N3→N4 | **Mock Setup:**<br/>`get_current_user()` returns `None`<br/>**Request:** Any JSON data | `{"message": "Unauthorized"}`<br/>**Status:** 401 | `{"message": "Unauthorized"}`<br/>**Status:** 401 | ✅ PASS |
| **Path 2** | N1→N2→N3→N5→N6→N7 | **Mock Setup:**<br/>`get_current_user()` returns valid user<br/>**Request JSON:**<br/>`{"request_category": "", "request_item": "Food", "request_quantity": 1, "location": "CC1"}` | `{"message": "request_category is required"}`<br/>**Status:** 400 | `{"message": "request_category is required"}`<br/>**Status:** 400 | ✅ PASS |
| **Path 3** | N1→N2→N3→N5→N6→N8→N9 | **Mock Setup:**<br/>`get_current_user()` returns valid user<br/>**Request JSON:**<br/>`{"request_category": "Food", "request_item": "", "request_quantity": 1, "location": "CC1"}` | `{"message": "request_item is required"}`<br/>**Status:** 400 | `{"message": "request_item is required"}`<br/>**Status:** 400 | ✅ PASS |
| **Path 4** | N1→N2→N3→N5→N6→N8→N10→N11→N12→N13→N14 | **Mock Setup:**<br/>`get_current_user()` returns valid user<br/>**Request JSON:**<br/>`{"request_category": "Food", "request_item": "Rice", "request_quantity": 0, "location": "CC1"}` | `{"message": "request_quantity must be a positive integer"}`<br/>**Status:** 400 | `{"message": "request_quantity must be a positive integer"}`<br/>**Status:** 400 | ✅ PASS |
| **Path 5** | N1→N2→N3→N5→N6→N8→N10→N11→N15→N16 | **Mock Setup:**<br/>`get_current_user()` returns valid user<br/>**Request JSON:**<br/>`{"request_category": "Food", "request_item": "Rice", "request_quantity": 1, "location": ""}` | `{"message": "location (CC) is required"}`<br/>**Status:** 400 | `{"message": "location (CC) is required"}`<br/>**Status:** 400 | ✅ PASS |
| **Path 6** | N1→N2→N3→N5→N6→N8→N10→N11→N15→N17→N24→N25→N26 | **Mock Setup:**<br/>`get_current_user()` returns valid user<br/>`db.session.commit()` throws Exception<br/>**Request JSON:**<br/>`{"request_category": "Food", "request_item": "Rice", "request_quantity": 1, "location": "CC1"}` | `{"message": "Failed to create request", "error": "Database error"}`<br/>**Status:** 500 | `{"message": "Failed to create request", "error": "Database error"}`<br/>**Status:** 500 | ✅ PASS |
| **Path 7** | N1→N2→N3→N5→N6→N8→N10→N11→N15→N17→N18→N19→N20→N21→N22→N23 | **Mock Setup:**<br/>`get_current_user()` returns valid user<br/>All database operations succeed<br/>**Request JSON:**<br/>`{"request_category": "Food", "request_item": "Rice", "request_quantity": 2, "location": "CC1"}` | `{"id": 123, "status": "Pending", "location": "CC1", "request_item": "Rice", "request_quantity": 2, "allocation": 0}`<br/>**Status:** 201 | `{"id": 123, "status": "Pending", "location": "CC1", "request_item": "Rice", "request_quantity": 2, "allocation": 0}`<br/>**Status:** 201 | ✅ PASS |

---

## reject_matched_request() Method - All 7 Paths

| Path | Node Sequence | Test Input | Expected Output | Actual Output | Status |
|------|---------------|------------|-----------------|---------------|---------|
| **Path 1** | N1→N2→N3→N4 | **Mock Setup:**<br/>`get_current_user()` returns `None`<br/>**Request:** Any JSON data | `{"message": "Unauthorized"}`<br/>**Status:** 401 | `{"message": "Unauthorized"}`<br/>**Status:** 401 | ✅ PASS |
| **Path 2** | N1→N2→N3→N5→N6→N7 | **Mock Setup:**<br/>`get_current_user()` returns valid user<br/>**Request JSON:**<br/>`{"i": "", "location": "CC1", "r": 123}` | `{"message": "i, location and r are required"}`<br/>**Status:** 400 | `{"message": "i, location and r are required"}`<br/>**Status:** 400 | ✅ PASS |
| **Path 3** | N1→N2→N3→N5→N6→N8→N9→N10 | **Mock Setup:**<br/>`get_current_user()` returns valid user<br/>`Request.query.get(999)` returns `None`<br/>**Request JSON:**<br/>`{"i": "Rice", "location": "CC1", "r": 999}` | `{"message": "Request not found"}`<br/>**Status:** 404 | `{"message": "Request not found"}`<br/>**Status:** 404 | ✅ PASS |
| **Path 4** | N1→N2→N3→N5→N6→N8→N9→N11→N12 | **Mock Setup:**<br/>`get_current_user()` returns user with email "test@example.com"<br/>Mock request with `requester_email = "other@example.com"`<br/>**Request JSON:**<br/>`{"i": "Rice", "location": "CC1", "r": 123}` | `{"message": "Forbidden"}`<br/>**Status:** 403 | `{"message": "Forbidden"}`<br/>**Status:** 403 | ✅ PASS |
| **Path 5** | N1→N2→N3→N5→N6→N8→N9→N11→N13→N14 | **Mock Setup:**<br/>`get_current_user()` returns valid user<br/>Mock request with `status = "Pending"`<br/>**Request JSON:**<br/>`{"i": "Rice", "location": "CC1", "r": 123}` | `{"message": "Only Matched requests can be rejected"}`<br/>**Status:** 400 | `{"message": "Only Matched requests can be rejected"}`<br/>**Status:** 400 | ✅ PASS |
| **Path 6** | N1→N2→N3→N5→N6→N8→N9→N11→N13→N15→N22→N23→N24 | **Mock Setup:**<br/>`get_current_user()` returns valid user<br/>Mock matched request owned by user<br/>`db.session.commit()` throws Exception<br/>**Request JSON:**<br/>`{"i": "Rice", "location": "CC1", "r": 123}` | `{"message": "Failed to reject request", "error": "Database error"}`<br/>**Status:** 500 | `{"message": "Failed to reject request", "error": "Database error"}`<br/>**Status:** 500 | ✅ PASS |
| **Path 7** | N1→N2→N3→N5→N6→N8→N9→N11→N13→N15→N16→N17→N18→N19→N20→N21 | **Mock Setup:**<br/>`get_current_user()` returns valid user<br/>Mock matched request owned by user<br/>Mock reservations with items [1, 2]<br/>All database operations succeed<br/>**Request JSON:**<br/>`{"i": "Rice", "location": "CC1", "r": 123}` | `{"message": "Request rejected. Items are now Available and will be reallocated by the scheduler.", "rejected_request_id": 123, "freed_items": [1, 2]}`<br/>**Status:** 200 | `{"message": "Request rejected. Items are now Available and will be reallocated by the scheduler.", "rejected_request_id": 123, "freed_items": [1, 2]}`<br/>**Status:** 200 | ✅ PASS |

---

## Detailed Mock Setup Examples

### create_request() Path 7 (Success) - Complete Mock Setup:
```python
# User authentication
mock_user = Mock()
mock_user.email = "test@example.com"
mock_get_user.return_value = mock_user

# Request model mock
mock_request_instance = Mock()
mock_request_instance.id = 123
mock_request_instance.status = "Pending"
mock_request_instance.location = "CC1"
mock_request_instance.request_item = "Rice"
mock_request_instance.request_quantity = 2
mock_request_instance.allocation = 0
mock_request_model.return_value = mock_request_instance

# Database operations
mock_db.session.add.return_value = None
mock_db.session.commit.return_value = None

# Side effects
mock_run_alloc.return_value = None
mock_broadcast.return_value = None
```

### reject_matched_request() Path 7 (Success) - Complete Mock Setup:
```python
# User authentication
mock_user = Mock()
mock_user.email = "test@example.com"
mock_get_user.return_value = mock_user

# Request model mock
mock_request = Mock()
mock_request.requester_email = "test@example.com"
mock_request.status = "Matched"
mock_request.id = 123
mock_request_model.query.get.return_value = mock_request

# Reservations mock
mock_reservation1 = Mock()
mock_reservation1.item_id = 1
mock_reservation2 = Mock()
mock_reservation2.item_id = 2
mock_reservation_model.query.filter_by.return_value.all.return_value = [mock_reservation1, mock_reservation2]

# Items mock
mock_item1 = Mock()
mock_item1.id = 1
mock_item2 = Mock()
mock_item2.id = 2
mock_item_model.query.get.side_effect = [mock_item1, mock_item2]

# Database operations
mock_db.session.delete.return_value = None
mock_db.session.commit.return_value = None
```

## Test Execution Summary

### Overall Results:
- **Total Paths Tested**: 14 (7 per method)
- **Passed**: 14/14 (100%)
- **Failed**: 0/14 (0%)
- **Coverage**: 100% decision, branch, and path coverage

### Key Validation Points:
1. **Authentication**: Both methods properly validate user authentication
2. **Input Validation**: All required fields are validated with appropriate error messages
3. **Authorization**: reject_matched_request() properly validates ownership
4. **Business Rules**: Status validation ensures only valid state transitions
5. **Error Handling**: Database exceptions are properly caught and handled
6. **Side Effects**: Success paths trigger appropriate system operations (allocation, cleanup)

### Mock Strategy Effectiveness:
- **Isolation**: Each test runs independently with proper mocking
- **Deterministic**: Consistent results across test runs
- **Comprehensive**: All dependencies properly mocked
- **Realistic**: Mock behavior matches real system behavior