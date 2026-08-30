# Portfolio Bug Reports

These are structured demonstration reports based on common defects found while testing web workflows. In a live project, I would attach the real screenshot, URL/build, browser/device, and execution date before marking a defect as observed.

## BUG-001 — Checkout accepts an incomplete address

| Field | Details |
| --- | --- |
| Severity | High |
| Priority | High |
| Area | Checkout / order creation |
| Type | Functional and validation |
| Status | Example portfolio defect |

### Steps to reproduce

1. Add an available item to the cart.
2. Proceed to checkout.
3. Leave the required address field blank.
4. Enter the other required information.
5. Select **Submit order**.

### Expected result

The order is blocked and the user receives a clear message identifying the missing address.

### Actual result

The order is allowed to continue without a complete address.

### Risk

Orders may be created without the information needed for fulfillment, creating customer-service, payment, and delivery problems.

## BUG-002 — Invalid email format is accepted during registration

| Field | Details |
| --- | --- |
| Severity | Medium |
| Priority | High |
| Area | Registration / client-side validation |
| Type | Validation |
| Status | Example portfolio defect |

### Steps to reproduce

1. Open the registration form.
2. Enter a value such as `customer@` in the email field.
3. Complete the remaining required fields.
4. Submit the form.

### Expected result

The form rejects the value and explains the required email format.

### Actual result

The invalid value is accepted or the error is not associated with the email field.

### Risk

Users may be unable to receive account messages, order notices, or password-reset instructions.

## BUG-003 — Mobile checkout control is clipped in portrait view

| Field | Details |
| --- | --- |
| Severity | Medium |
| Priority | Medium |
| Area | Responsive checkout UI |
| Type | Responsive/usability |
| Status | Example portfolio defect |

### Steps to reproduce

1. Open the checkout page on a narrow portrait viewport.
2. Scroll through the form.
3. Inspect the payment and submit controls.

### Expected result

All controls are visible, reachable, and usable without horizontal scrolling.

### Actual result

One or more controls are clipped, overlap nearby content, or require an unintended rotation to use.

### Risk

Mobile users may abandon checkout or be unable to complete an order.

## Defect-reporting standard

Every report should answer: What happened? Where did it happen? How can someone reproduce it? What should have happened? How serious is the risk? What evidence supports the report?

