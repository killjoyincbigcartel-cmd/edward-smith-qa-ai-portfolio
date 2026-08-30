# QA Testing Portfolio

This section demonstrates how I approach quality assurance from requirements and user flows through test execution, defect reporting, retesting, and regression coverage.

## Testing workflow

1. Understand the requirement and identify the primary user flow.
2. Break the flow into clear, repeatable test cases.
3. Add negative, boundary, permission, responsive, and error-state coverage.
4. Record expected and actual results.
5. Document defects with steps to reproduce, environment, severity, and priority.
6. Retest fixes and run focused regression checks around the change.
7. Summarize risk, coverage, and remaining issues for the team.

## Portfolio artifacts

| Artifact | Purpose |
| --- | --- |
| [E-commerce test cases](test-cases/ecommerce.md) | Covers login, cart, checkout, validation, and order flow |
| [Registration test cases](test-cases/registration.md) | Covers required fields, email validation, password rules, and duplicate accounts |
| [Bug reports](bug-reports/bug-reports.md) | Shows clear reproduction steps and defect communication |
| [Movies API test plan](api-testing/movies-api-test-plan.md) | Shows API, database, validation, and HTTP-status testing |
| [Playwright example](automation/registration.spec.ts) | Shows how manual coverage can become repeatable automation |

## Testing areas represented

- Functional and regression testing
- Smoke and exploratory testing
- Negative and edge-case testing
- Responsive and mobile-layout validation
- API and JSON response validation
- SQL and persistence checks
- Authentication and session-state checks
- Defect triage and retesting

The examples in this folder are portfolio demonstration artifacts. When connecting them to a live project, I would record the exact build number, browser/device, environment, evidence, and execution date.

