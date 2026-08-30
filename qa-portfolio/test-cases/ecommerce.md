# E-commerce Test Cases

## Scope

Core customer workflows: account access, product discovery, cart behavior, checkout validation, and order submission.

## Test cases

| ID | Priority | Scenario | Steps | Expected result | Type |
| --- | --- | --- | --- | --- | --- |
| ECOM-001 | High | Login with valid credentials | Open login; enter a valid email and password; select **Log in** | User reaches the authenticated area and sees the correct account state | Functional |
| ECOM-002 | High | Login with invalid password | Enter a valid email and incorrect password; select **Log in** | A clear error appears and the user remains signed out | Negative |
| ECOM-003 | Medium | Search for an existing product | Enter a known product name in search and submit | Matching products appear with correct names and prices | Functional |
| ECOM-004 | Medium | Search with no matching results | Search for a value that does not exist | Empty-state message appears and the page does not crash | Negative |
| ECOM-005 | High | Add an item to the cart | Open a product; select required options; choose **Add to cart** | Correct item, option, quantity, and price appear in the cart | Functional |
| ECOM-006 | Medium | Update cart quantity | Change quantity from one to two | Quantity, subtotal, and total update correctly | Functional |
| ECOM-007 | High | Checkout with missing required address | Add an item; proceed to checkout; leave address blank; submit | The order is blocked and the user is told which field is required | Validation |
| ECOM-008 | High | Checkout with invalid payment data | Enter invalid or incomplete payment data; submit | Payment is rejected safely and no order is created | Negative |
| ECOM-009 | High | Successful checkout | Complete all required fields with valid data; submit | Confirmation page shows the order reference and correct total | Functional |
| ECOM-010 | Medium | Refresh after cart update | Add an item; refresh the page | Cart state is preserved or the user receives an intentional, documented result | State/persistence |
| ECOM-011 | Medium | Mobile checkout layout | Test checkout in a narrow portrait viewport | Fields and buttons remain visible, usable, and not clipped | Responsive |
| ECOM-012 | Low | Back navigation after checkout error | Trigger a validation error; use browser back and forward | Form and cart state behave consistently without duplicate submission | Regression |

## Execution notes

For a real run, I would add environment, build number, browser/device, tester, execution date, actual result, evidence link, and Pass/Fail status to each row.

