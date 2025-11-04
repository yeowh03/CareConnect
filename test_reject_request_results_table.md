# Basis Path Testing Results for reject_matched_request() Method

## Test Cases Summary Table

| Test Case | Path | Test Input | Expected Output | Actual Output | Status |
|-----------|------|------------|-----------------|---------------|---------|
| **Path 1** | Unauthorized User | `get_current_user()` returns `None` | `{"message": "Unauthorized"}`, Status: 401 | `{"message": "Unauthorized"}`, Status: 401 | ✅ PASS |
| **Path 2** | Missing Required Fields | `{"i": "", "location": "CC1", "r": 123}` | `{"message": "i, location and r are required"}`, Status: 400 | `{"message": "i, location and r are required"}`, Status: 400 | ✅ PASS |
| **Path 3** | Request Not Found | `{"i": "Rice", "location": "CC1", "r": 999}` + Request.query.get returns None | `{"message": "Request not found"}`, Status: 404 | `{"message": "Request not found"}`, Status: 404 | ✅ PASS |
| **Path 4** | Forbidden Access | `{"i": "Rice", "location": "CC1", "r": 123}` + Different requester email | `{"message": "Forbidden"}`, Status: 403 | `{"message": "Forbidden"}`, Status: 403 | ✅ PASS |
| **Path 5** | Invalid Status | `{"i": "Rice", "location": "CC1", "r": 123}` + Request status = "Pending" | `{"message": "Only Matched requests can be rejected"}`, Status: 400 | `{"message": "Only Matched requests can be rejected"}`, Status: 400 | ✅ PASS |
| **Path 6** | Database Exception | Valid input + Database commit throws exception | `{"message": "Failed to reject request"}`, Status: 500 | `{"message": "Failed to reject request"}`, Status: 500 | ✅ PASS |
| **Path 7** | Successful Rejection | `{"i": "Rice", "location": "CC1", "r": 123}` + Valid matched request | `{"message": "Request rejected...", "rejected_request_id": 123, "freed_items": [1,2]}`, Status: 200 | `{"message": "Request rejected...", "rejected_request_id": 123, "freed_items": [1,2]}`, Status: 200 | ✅ PASS |

## Detailed Test Case Explanations

### Path 1: Unauthorized User Authentication
**Purpose**: Tests the authentication guard at method entry
- **Condition**: `get_current_user()` returns `None`
- **Expected Behavior**: Method immediately returns 401 Unauthorized
- **Coverage**: Tests the first decision point in the control flow

### Path 2: Missing Required Fields Validation
**Purpose**: Tests input validation for required fields (i, location, r)
- **Condition**: Any of the three required fields is missing or empty
- **Expected Behavior**: Returns 400 Bad Request with specific error message
- **Coverage**: Tests the compound validation condition after authentication

### Path 3: Request Not Found
**Purpose**: Tests database lookup failure
- **Condition**: Request ID does not exist in database
- **Expected Behavior**: Returns 404 Not Found
- **Coverage**: Tests request existence validation

### Path 4: Forbidden Access Control
**Purpose**: Tests ownership validation
- **Condition**: User tries to reject another user's request
- **Expected Behavior**: Returns 403 Forbidden
- **Coverage**: Tests authorization logic after authentication

### Path 5: Invalid Request Status
**Purpose**: Tests business rule validation
- **Condition**: Request status is not "Matched"
- **Expected Behavior**: Returns 400 Bad Request with status error
- **Coverage**: Tests status validation for rejection eligibility

### Path 6: Database Exception Handling
**Purpose**: Tests error handling during database operations
- **Condition**: Database commit operation throws exception
- **Expected Behavior**: Returns 500 Internal Server Error, triggers rollback
- **Coverage**: Tests exception handling in the main try-catch block

### Path 7: Successful Request Rejection (Happy Path)
**Purpose**: Tests complete successful execution flow
- **Condition**: All validations pass, database operations succeed
- **Expected Behavior**: Frees reserved items, deletes request, runs allocation, returns 200
- **Coverage**: Tests the complete success path including all side effects

## Control Flow Coverage Analysis

- **Decision Points Covered**: 7/7 (100%)
- **Branch Coverage**: All true/false branches tested
- **Exception Paths**: Database exception handling covered
- **Business Logic**: All validation rules and authorization checks tested
- **Side Effects Verified**: Item status updates, reservation deletions, allocation runs

## Key Business Logic Tested

1. **Authentication**: User must be logged in
2. **Input Validation**: All required fields must be provided
3. **Resource Existence**: Request must exist in database
4. **Authorization**: User can only reject their own requests
5. **Status Validation**: Only "Matched" requests can be rejected
6. **Resource Cleanup**: Reserved items are freed and made available
7. **System Integration**: Allocation system is triggered after rejection

## Comparison with create_request()

| Aspect | create_request() | reject_matched_request() |
|--------|------------------|--------------------------|
| Complexity | 7 paths | 7 paths |
| Input Format | JSON | JSON |
| Validation Types | Field validation | Field + business rule validation |
| Authorization | Authentication only | Authentication + ownership |
| Database Operations | Create + allocate | Delete + free resources |
| Side Effects | Allocation + broadcast | Allocation only |

## Test Methodology Notes

- **White Box Testing**: Based on internal code structure analysis
- **Basis Path Testing**: Covers all linearly independent execution paths
- **Cyclomatic Complexity**: V(G) = 7 paths identified and tested
- **Mock Strategy**: Comprehensive mocking of database models and services
- **Assertion Coverage**: Tests both return values and side effect verification
- **Error Scenarios**: All failure modes properly tested and handled