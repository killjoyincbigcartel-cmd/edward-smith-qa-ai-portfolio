# Registration Test Cases

## Scope

New-account creation, validation rules, duplicate-account handling, password behavior, and session state.

## Test cases

| ID | Priority | Scenario | Steps | Expected result | Type |
| --- | --- | --- | --- | --- | --- |
| REG-001 | High | Register with valid information | Enter a unique name, valid email, compliant password, and confirmation; submit | Account is created and the user receives the expected next step | Functional |
| REG-002 | High | Submit with required fields empty | Open registration and submit without entering values | Required-field messages appear beside the correct fields | Validation |
| REG-003 | Medium | Enter invalid email format | Enter values such as `name@` or `name.example.com`; submit | Email field is rejected with a clear message | Negative |
| REG-004 | Medium | Enter weak password | Enter a password that violates one or more rules | Password is rejected and the rules are understandable | Validation |
| REG-005 | Medium | Password confirmation mismatch | Enter different password and confirmation values | Submission is blocked and mismatch is explained | Negative |
| REG-006 | High | Register with an existing email | Submit a valid form using an email already registered | Account is not duplicated and the response explains the issue safely | Business rule |
| REG-007 | Medium | Leading/trailing spaces | Enter spaces before or after name and email values | Values are normalized or rejected consistently according to requirements | Edge case |
| REG-008 | Medium | Maximum field length | Enter values at and above documented limits | Allowed length is accepted; excessive input is rejected safely | Boundary |
| REG-009 | High | Refresh after validation error | Submit invalid data, refresh, and return to the form | No duplicate account is created and the form state is intentional | State |
| REG-010 | High | Successful login after registration | Create an account; sign out if needed; log in with the new credentials | User reaches the correct authenticated state | Integration |
| REG-011 | Medium | Mobile registration layout | Test portrait and landscape viewports | Labels, inputs, messages, and submit controls remain usable | Responsive |
| REG-012 | Low | Password visibility control | Toggle password visibility on and off | The value is revealed/hidden without changing the value | Usability |

