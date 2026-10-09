# Initial automated test coverage

| Test | Type | Scenario | Expected result |
|---|---|---|---|
| Room capacity starts available | Unit | New room with capacity 1 | One bed available |
| Allocation updates availability | Integration/model | Active student allocated to room | Available bed count becomes 0 |
| Duplicate bed is blocked | Integration/model | Two active allocations use same bed | Database rejects duplicate active bed |
| Invalid leave date range | Unit | End date before start date | Validation error |
| Dashboard responds | Integration/view | GET `/` | HTTP 200 and dashboard rendered |
| Health endpoint responds | Integration/view | GET `/health/` | HTTP 200 and status `ok` |

These are starter tests only. Add test cases for each SRS requirement as its feature is implemented.
