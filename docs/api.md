# API

| Endpoint | Purpose |
|---|---|
| `POST /api/v1/problems/analyze` | Analyze the original question |
| `POST /api/v1/problems/{problem_id}/variations` | Generate selected variation types |
| `POST /api/v1/variations/{variation_id}/explain` | Reveal solution and explanation |

## Analysis response
`summary`, `principles[]`, `assumptions[]`, `constraints[]`, `reasoning`

## Variation
`category`, `question`, `modified_conditions[]`, `learning_objective`, `expected_answer`/`explanation` (hidden until requested)
