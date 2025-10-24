## 1. Purpose

This workflow defines the structured reasoning process for analyzing target cutomers after market assessment.  
It identifies **who the target customers are**, **what problems they care about**, and **which questions are worth solving and commercializing**.  
The output returns JSON object , ensuring that every customer group has its own set of valued business questions.
The length of output is not limited by the example, and your output should be a legal JSON.

---

## Analysis Steps

### Step 1 — customer Identification

**Objective:**

Define and classify customer segments that share similar roles, goals, or contexts.

**Reasoning Flow:**

1. Identify segmentation basis (industry, company size, region, behavior, role).  
2. Group customers into clear segment archetypes.  
3. Create a concise profile for each segment.  

**Example Schema:**

```json
{
  "customer_name": "Data Innovators",
  "profile": {
    "industry": "Tech",
    "company_size": "mid-market",
    "region": "Global",
    "roles": ["Head of Data", "Product Analytics Lead"]
  }
}
```

---

### Step 2 — Valued Questions (Pain Points)

**Objective:**

Identify and reframe pain points into specific, data-answerable questions that hold measurable business or monetization value.
Questions must focus on facts that can be derived directly from datasets (e.g., rankings, trends, correlations, or forecasts).

**Reasoning Flow:**

1. Gather 5–10 recurring data-related questions from each customer or segment.

2. Transform vague pain points into quantitative, fact-based questions that data can answer.

3. For each question, specify its business meaning, type of analytical problem, monetization potential, and decision value.

**Example Schema:**

```json
{
  "valued_questions": [
    {
      "question": "Which U.S. cities have the highest median home prices in 2024?",
      "mapped_pain_point": "Investors need to identify premium real-estate zones.",
      "problem_type": "Market Comparison / Pricing Insight",
      "monetization_path": ["data_api", "market_report"],
      "decision_value": "High"
    }
  ]
}
```

---

## Step 3 — Willingness to Pay

**Objective:**

Assess financial capacity and pricing sensitivity for each segment.

**Reasoning Flow:**

1. Estimate budget range and procurement model.
2. Evaluate frequency of purchase or renewal.
3. Classify payment potential by tier.

**Example Schema:**

```json
{
  "willingness_to_pay": {
    "tier": "high",
    "budget_range_usd": "30000-50000"
  }
}
```

---

## 3. Final Output Structure

Integrate all results, return JSON.

**Example Output:**

```json
{
  "target_customers": [
    {
      "customer_name": "Retail Buyers",
      "profile": { ... },
      "valued_questions": [
        { ... },
        { ... }
      ],
      "willingness_to_pay": { ... },
    },
    {
      "customer_name": "policy_analyst",
      ...
    }
  ]
}

```

---
