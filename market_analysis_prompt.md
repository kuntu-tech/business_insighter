## 1. Purpose

Build a reasoning workflow that transforms **raw data or product attributes** into **strategic market insight**.
The system must **quantify market potential**, **analyze structural dynamics**, and **derive actionable investment or entry decisions**.
All outputs must integrate both **quantitative metrics** and **strategic interpretation** (cause → effect → implication).
The system identifies relevant markets from schema, performs full-dimensional analysis

---

## 2. Analysis Steps

### Step 0 — Market Identification

**Objective:**  
Infer which markets are represented in the dataset through schema inspection and content pattern analysis, without predefining which fields are market-related.

**Reasoning Flow:**

1. Use 'supabase mcp' to inspect the database structure to understand available tables, field types, and naming patterns.  
2. Retrieve a small random sample (≤50 rows) from each table for exploratory analysis.  
3. Examine the **value distributions** of each field — identify frequent tokens, numeric ranges, regional codes, or product categories.  
4. Detect potential **industries, commodities, or geographic clusters** by combining schema semantics and data regularities (e.g., recurring medical terms → healthcare market; repeated HS-like codes → trade commodities).  
5. Cluster correlated variables (e.g., product name + region + value) into **candidate market groups**.  
6. Compute a **relevance_score** for each inferred market using:  
   - coverage of related fields  
   - frequency and diversity of occurrences  
   - dominance in total transaction or value  
   - regional and temporal stability  
7. For the top markets (≤5), summarize detection evidence and propose segmentation logic (by product, region, or channel).

**Output Example:**

```json
{
  "market_name": "Cosmetics Export ASEAN",
  "market_overview": [
    {
      "relevance_score": 0.87,
      "evidence_fields": ["table:trade_data", "columns:['product_name','region','export_value']"],
      "pattern_summary": {
        "keywords_detected": ["skincare", "makeup"],
        "dominant_regions": ["TH", "VN", "MY"],
        "valsue_share": 0.68
      },
      "suggested_segments": ["Beauty care", "OEM brands", "Retail distribution"],
    }
  ]
}
```

---

### Step 1 — Market Size & Growth

**Objective:**

Quantify and interpret the commercial growth logic, not just static market numbers.

**Reasoning Flow:**

1. Define **market boundary** precisely (industry × use-case × geography).
2. Calculate **TAM/SAM/SOM** and CAGR (3–7 yr horizon).
3. Evaluate **revenue concentration** (top 10 share) and **growth sustainability** (driver dependency index).
4. Distinguish **data monetization** (data→insight) vs **service monetization** (insight→solution).
5. Identify top 3 **sub-segments by ROI and barrier asymmetry**.
6. State **key assumptions** and **sensitivity factors** (pricing elasticity, regulation, adoption speed).

Output Example:

```json
{
  "market_size_and_growth": {
    "period": "2022–2028",
    "tam_usd": 2300000000,
    "sam_usd": 870000000,
    "som_usd": 160000000,
    "cagr": "18%",
    "growth_sustainability": "High (driver-linked >70%)",
    "data_monetization_value": "$60M",
    "service_monetization_value": "$100M",
    "top_segments": [
      {"segment": "AI analytics SaaS", "roi_rank": 1, "barrier": "medium"},
      {"segment": "Predictive API services", "roi_rank": 2, "barrier": "low"}
    ],
    "key_assumptions": ["Regulatory climate remains stable", "Data acquisition cost growth <5%"]
  }
}
```

---

### Step 2 — Market Structure & Competition**

Objective: Reveal who controls access to customers, capital, and data — and how rivalry shapes profitability.

Reasoning Flow:

1. Map **value layers** (upstream→downstream).
2. Compute **HHI/CR5** and interpret vs industry benchmarks.
3. Identify **control nodes** (who owns distribution, network effects, data).
4. Assess **entry barriers**, **switching costs**, and **platform dependency**.
5. Evaluate **strategic options**: enter via partnership, acquisition, or niche specialization.

Output Example:

```json
{
  "market_structure_and_competition": {
    "hhi": 0.42,
    "control_nodes": ["Booking platforms", "API aggregators"],
    "major_players": [
      {"name": "Company A", "share": 35, "model": "Data marketplace"},
      {"name": "Company B", "share": 22, "model": "Vertical SaaS"}
    ],
    "entry_barriers": ["Regulatory license", "Data network effects"],
    "competitive_pressure": "High rivalry; buyer power medium; supplier power low",
    "recommended_entry_mode": "Strategic partnership with midstream platform"
  }
}
```

---

### 5. Step 3 — Demand & Drivers**

Objective: Quantify what sustains demand, when, and with what magnitude; clarify elasticity and risk of reversal.

Reasoning Flow:

1. Identify 3–5 key growth drivers and quantify effect (+/– %).
2. Add **time horizon** and **probability of persistence**.
3. Quantify inhibitors with measurable drag factors.
4. Rank **net demand strength = Σ(impact×probability) – inhibitors**.
5. Define **dominant driver** and its dependency risks.

Output Example:

```json
{
  "demand_and_drivers": {
    "drivers": [
      {"driver": "AI adoption", "impact": 0.9, "probability": 0.8, "net_effect": "+25%", "horizon": "short"},
      {"driver": "ESG compliance", "impact": 0.6, "probability": 0.7, "net_effect": "+12%", "horizon": "mid"}
    ],
    "inhibitors": [
      {"factor": "High acquisition cost", "impact": -0.4},
      {"factor": "Policy uncertainty", "impact": -0.3}
    ],
    "dominant_driver": "AI-driven automation (high persistence)"
  }
}
```

---

### Step 4 — Value Chain & Ecosystem**

Objective: Locate the highest-margin nodes and integration leverage across the chain.

Reasoning Flow:

1. Map **profit distribution** (EBITDA basis).
2. Evaluate **margin drivers** (scale, data, IP, switching costs).
3. Highlight **synergy opportunities** via vertical/horizontal integration.
4. Score each opportunity = (ROI × barrier asymmetry × strategic fit).

Output Example:

```json
{
  "value_chain_and_ecosystem": {
    "profit_distribution": {"upstream": "20%", "midstream": "50%", "downstream": "30%"},
    "margin_drivers": ["Data ownership", "API lock-in"],
    "integration_opportunities": [
      {"target": "Midstream API aggregators", "roi_score": 8.7, "priority": "high"},
      {"target": "Downstream SaaS resellers", "roi_score": 6.3, "priority": "medium"}
    ]
  }
}
```

---

### Step 5 — Trends, Risks & Scenarios

**Objective:** Convert uncertainty into strategic readiness.

**Reasoning Flow:**

1. Identify top trends and assign **quantified impact index**.
2. Develop **risk matrix** (Probability × Impact).
3. Simulate **best/base/worst-case scenarios** for 3-year horizon.
4. Output **response priorities** (Prevent / Adapt / Exploit).

**Output Example:**

```json
{
  "trends_and_risks": {
    "emerging_trends": [
      {"trend": "AI regulation tightening", "impact_index": 0.8},
      {"trend": "Open-data economy", "impact_index": 0.6}
    ],
    "risk_matrix": [
      {"event": "Regulatory delay", "prob": 0.7, "impact": 0.8, "type": "external"},
      {"event": "Price compression", "prob": 0.5, "impact": 0.6, "type": "market"}
    ],
    "scenarios": {
      "best_case": "Rapid AI adoption → +30% market expansion",
      "base_case": "Steady 12% CAGR, moderate risk",
      "worst_case": "Regulatory freeze → –10% growth"
    },
    "response_plan": ["Invest in compliance tech", "Diversify into B2B API services"]
  }
}
```

---

### Step 8 — Overall Summary

**Objective**: Provide a one-screen executive summary integrating quantitative scale, structural logic, and strategic recommendation.

**Output Example:**

```json
{
  "summary": {
    "headline": "A $2.3B high-growth data service market with dominant midstream profit pools and rising AI-driven monetization potential.",
    "core_insight": "Value capture is shifting from ownership to integration — firms controlling midstream APIs and compliance automation will dominate ROI.",
    "risk_outlook": "Regulatory uncertainty is the single largest downside risk; diversification into B2B and compliance tech mitigates exposure.",
    "strategic_call": "Prioritize entry via partnership and data integration; short-term focus on compliance connectors, long-term on predictive analytics ecosystems."
  }
}
```

## 3. Final Output Structure

**Objective:**

For each dimension :

1. Summarize the **key data patterns** — what the data shows: highlight major findings, numerical patterns, relationships, or metrics.  
2. Write a **concise summary (1–2 sentences)** — what it means for business or strategy.

**Reasoning Flow:**

1. Combine analysis and summary in the same text field.  
2. Write 1–2 sentences (≤60 words total).  
3. Style: consulting report tone (McKinsey / BCG).  
4. Do not list raw data; interpret it.  
5. Focus on **fact → implication** logic, Output one field `insight` per dimension.

Sort out all the JSON，integrate them and return JSON object, the JSON MUST cover the JSON output examples mentioned in analysis steps.

```json
{
  "market_segments": [
    {
      "market_name": "Short-Term Vacation Rentals",
      "market_overview": { 
        ... 
        "insight": "The market grows at 15% CAGR, driven by digital expansion and tourism recovery. This indicates strong near-term potential but cyclical exposure to seasonality."
      },
      "market_size_and_growth": { ... },
      "market_structure_and_competition": { ... },
      "demand_and_drivers": { ... },
      "value_chain_and_ecosystem": { ... },
      "trends_and_risks": { ... },
      "market_summary": {...}
    },
    {
      "market_name": "another market",
      "market_overview": { ... },
      ...
    }
  ]
}

```
