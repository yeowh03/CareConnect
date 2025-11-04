# Complete Path Analysis for Both Methods

## create_request() Method - All 7 Paths Explained

### Path 1: Unauthorized User
**Node Sequence**: N1 → N2 → N3 → N4
**Condition**: User not authenticated
**Explanation**: 
- System gets current user but finds none logged in
- Immediately returns 401 Unauthorized
- **Test Scenario**: No authentication token provided

### Path 2: Missing Category
**Node Sequence**: N1 → N2 → N3 → N5 → N6 → N7
**Condition**: Empty or missing request_category
**Explanation**:
- User authenticated successfully
- JSON data parsed but category field is empty/missing
- Returns 400 Bad Request with category error
- **Test Scenario**: `{"request_category": "", "request_item": "Food", ...}`

### Path 3: Missing Item
**Node Sequence**: N1 → N2 → N3 → N5 → N6 → N8 → N9
**Condition**: Empty or missing request_item
**Explanation**:
- User authenticated, category valid
- Item field is empty or missing
- Returns 400 Bad Request with item error
- **Test Scenario**: `{"request_category": "Food", "request_item": "", ...}`

### Path 4: Invalid Quantity
**Node Sequence**: N1 → N2 → N3 → N5 → N6 → N8 → N10 → N11 → N12 → N13 → N14
**Condition**: Quantity ≤ 0 or non-numeric
**Explanation**:
- User authenticated, category and item valid
- Quantity parsing fails or value is ≤ 0
- Exception caught and returns 400 with quantity error
- **Test Scenario**: `{"request_quantity": 0}` or `{"request_quantity": "abc"}`

### Path 5: Missing Location
**Node Sequence**: N1 → N2 → N3 → N5 → N6 → N8 → N10 → N11 → N15 → N16
**Condition**: Empty or missing location
**Explanation**:
- All previous validations pass
- Location field is empty or missing
- Returns 400 Bad Request with location error
- **Test Scenario**: `{"location": ""}`

### Path 6: Database Exception
**Node Sequence**: N1 → N2 → N3 → N5 → N6 → N8 → N10 → N11 → N15 → N17 → N24 → N25 → N26
**Condition**: Database operation fails
**Explanation**:
- All validations pass
- Database commit throws exception (connection lost, constraint violation, etc.)
- Transaction rolled back, returns 500 Internal Server Error
- **Test Scenario**: Database connection failure during commit

### Path 7: Successful Creation (Happy Path)
**Node Sequence**: N1 → N2 → N3 → N5 → N6 → N8 → N10 → N11 → N15 → N17 → N18 → N19 → N20 → N21 → N22 → N23
**Condition**: All validations pass, no exceptions
**Explanation**:
- User authenticated, all fields valid
- Request object created and saved successfully
- Allocation system triggered, broadcast sent
- Returns 201 Created with request details
- **Test Scenario**: Valid complete request data

---

## reject_matched_request() Method - All 7 Paths Explained

### Path 1: Unauthorized User
**Node Sequence**: N1 → N2 → N3 → N4
**Condition**: User not authenticated
**Explanation**:
- Same as create_request - no user logged in
- Returns 401 Unauthorized
- **Test Scenario**: No authentication token

### Path 2: Missing Required Fields
**Node Sequence**: N1 → N2 → N3 → N5 → N6 → N7
**Condition**: Missing i, location, or r fields
**Explanation**:
- User authenticated but required fields missing
- Compound validation: `if not item_name OR not location OR not req_id`
- Returns 400 Bad Request
- **Test Scenario**: `{"i": "", "location": "CC1", "r": 123}`

### Path 3: Request Not Found
**Node Sequence**: N1 → N2 → N3 → N5 → N6 → N8 → N9 → N10
**Condition**: Request ID doesn't exist in database
**Explanation**:
- All fields present, database query returns None
- Returns 404 Not Found
- **Test Scenario**: `{"r": 99999}` (non-existent ID)

### Path 4: Forbidden Access
**Node Sequence**: N1 → N2 → N3 → N5 → N6 → N8 → N9 → N11 → N12
**Condition**: User trying to reject someone else's request
**Explanation**:
- Request exists but belongs to different user
- Authorization check fails: `req.requester_email != u.email`
- Returns 403 Forbidden
- **Test Scenario**: User A trying to reject User B's request

### Path 5: Invalid Status
**Node Sequence**: N1 → N2 → N3 → N5 → N6 → N8 → N9 → N11 → N13 → N14
**Condition**: Request status is not "Matched"
**Explanation**:
- User owns the request but it's not in "Matched" status
- Business rule violation: only matched requests can be rejected
- Returns 400 Bad Request
- **Test Scenario**: Request with status "Pending" or "Completed"

### Path 6: Database Exception
**Node Sequence**: N1 → N2 → N3 → N5 → N6 → N8 → N9 → N11 → N13 → N15 → N22 → N23 → N24
**Condition**: Database operation fails during rejection
**Explanation**:
- All validations pass but database commit fails
- Transaction rolled back, returns 500 Internal Server Error
- **Test Scenario**: Database connection lost during commit

### Path 7: Successful Rejection (Happy Path)
**Node Sequence**: N1 → N2 → N3 → N5 → N6 → N8 → N9 → N11 → N13 → N15 → N16 → N17 → N18 → N19 → N20 → N21
**Condition**: All validations pass, successful rejection
**Explanation**:
- User authenticated and owns a matched request
- Reservations freed, items set to "Available"
- Request deleted, allocation system triggered
- Returns 200 Success with freed item IDs
- **Test Scenario**: Valid matched request rejection

---

## Path Comparison Analysis

| Path Type | create_request() | reject_matched_request() | Key Difference |
|-----------|------------------|--------------------------|----------------|
| **Auth Failure** | N1→N2→N3→N4 | N1→N2→N3→N4 | Identical |
| **Validation 1** | N1→N2→N3→N5→N6→N7 | N1→N2→N3→N5→N6→N7 | Category vs Fields |
| **Validation 2** | N1→N2→N3→N5→N6→N8→N9 | N1→N2→N3→N5→N6→N8→N9→N10 | Item vs Existence |
| **Validation 3** | N1→N2→N3→N5→N6→N8→N10→N11→N12→N13→N14 | N1→N2→N3→N5→N6→N8→N9→N11→N12 | Quantity vs Authorization |
| **Validation 4** | N1→N2→N3→N5→N6→N8→N10→N11→N15→N16 | N1→N2→N3→N5→N6→N8→N9→N11→N13→N14 | Location vs Status |
| **Exception** | ...→N17→N24→N25→N26 | ...→N15→N22→N23→N24 | Similar pattern |
| **Success** | ...→N17→N18→N19→N20→N21→N22→N23 | ...→N15→N16→N17→N18→N19→N20→N21 | Create vs Delete |

## Key Insights

### Validation Patterns:
- **create_request()**: Sequential field validation (category → item → quantity → location)
- **reject_matched_request()**: Authorization-heavy validation (fields → existence → ownership → status)

### Business Logic:
- **create_request()**: Input sanitization and resource creation
- **reject_matched_request()**: Access control and resource cleanup

### Error Distribution:
- Both methods have **5 error paths** and **1 success path**
- **create_request()** focuses on input validation errors
- **reject_matched_request()** focuses on authorization and business rule errors

### Complexity Drivers:
- **create_request()**: Data validation complexity
- **reject_matched_request()**: Authorization and state management complexity