// Mirrors backend/app/schemas. Keep in sync by hand for now.

export type Category =
  | "changed_conditions"
  | "edge_cases"
  | "negation_counterexample"
  | "reverse_reasoning";

export interface Analysis {
  summary: string;
  principles: string[];
  assumptions: string[];
  constraints: string[];
  reasoning: string;
}

export interface Variation {
  id: string;
  category: Category;
  question: string;
  modified_conditions: string[];
  learning_objective: string;
}

export interface ExplainResponse {
  expected_answer: string;
  explanation: string;
}