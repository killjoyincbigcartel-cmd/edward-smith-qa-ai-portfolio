# Playwright Automation

The manual test cases are the source of truth. Automation should make stable, high-value checks repeatable rather than replace exploratory testing.

## Automation priorities

- Registration validation
- Login success and failure
- Critical checkout smoke flow
- API-backed UI states
- Responsive layout checks for important mobile workflows

The included TypeScript example shows the structure I use for a negative registration test. The route and labels should be mapped to the target application before execution.

