# Proposed WE Recover AI Extension

## Feature

An AI-assisted inquiry triage and response-drafting workflow.

## User flow

1. A customer submits an inquiry.
2. The system validates and stores the request.
3. An AI service classifies the request by topic and urgency.
4. The AI creates a short summary and suggested response.
5. A business user reviews, edits, approves, or rejects the suggestion.
6. Only an approved message can be sent.
7. The system records the decision and the final message for auditability.

## Quality and safety checks

- Do not send messages automatically without approval.
- Do not expose one customer or business account's data to another.
- Test empty, ambiguous, abusive, and unusually long inquiries.
- Verify that the AI does not invent prices, promises, or policy details.
- Log model errors and provide a manual fallback.
- Apply rate limits and protect credentials.
- Measure classification accuracy and response usefulness with a reviewed test set.

## Portfolio value

This design shows how I think about AI as a complete software feature: user flow, data boundaries, human review, testing, observability, and failure handling.

