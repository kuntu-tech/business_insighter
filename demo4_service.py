#!/usr/bin/env python3
"""
FastAPI wrapper around the demo-4 market & customer analysis pipeline.
"""
from __future__ import annotations

import asyncio
import copy
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from agents import (
    Agent,
    Runner,
    function_tool,
    ModelSettings,
    HostedMCPTool,
    WebSearchTool,
)


from fastapi.middleware.cors import CORSMiddleware


# Ensure .env values (SUPABASE_PROJECT_ID, SUPABASE_ACCESS_TOKEN, etc.) are visible.
load_dotenv()

# ---------------------------------------------------------------------------
# Configuration models
# ---------------------------------------------------------------------------

class Demo4Request(BaseModel):
    """Incoming payload describing how the pipeline should run."""
    supabase_project_id: str = Field(
        default_factory=lambda: os.getenv("SUPABASE_PROJECT_ID", ""),
        description="Supabase project ref (project_ref=...)",
    )
    supabase_access_token: str = Field(
        default_factory=lambda: os.getenv("SUPABASE_ACCESS_TOKEN", ""),
        description="Supabase Personal Access Token",
    )
    user_name: str = Field(
        default="huimin",
        description="Session owner; becomes the SQLite session ID and DB prefix",
    )
    business_prompt_path: Optional[str] = Field(
        default=None,
        description="Override path to business expert prompt markdown",
    )
    market_prompt_path: Optional[str] = Field(
        default=None,
        description="Override path to market analysis prompt markdown",
    )
    customer_prompt_path: Optional[str] = Field(
        default=None,
        description="Override path to customer analysis prompt markdown",
    )
    output_dir: Optional[str] = Field(
        default=None,
        description="Optional override for the output directory; defaults to ./outputs_<timestamp>",
    )
    save_files: bool = Field(
        default=True,
        description="When false, analysis artifacts are returned but not persisted to disk",
    )
    user_feedback:Optional[str] = Field(default=None, description="user's feedback")
    

class Demo4Result(BaseModel):
    """Result returned to the API caller."""
    integrated_analysis: Dict[str, Any]


# ---------------------------------------------------------------------------
# Utilities from the original script
# ---------------------------------------------------------------------------


def _load_prompt(path: Optional[str], fallback: Path) -> str:
    target = Path(path) if path else fallback
    if not target.exists():
        raise FileNotFoundError(f"Prompt file not found: {target}")
    return target.read_text(encoding="utf-8")


def _build_agent(project_id: str, access_token: str, instructions: str) -> Agent:
    @function_tool
    def get_current_time() -> str:
        return datetime.now().astimezone().isoformat()

    return Agent(
        name="business_expert",
        instructions=instructions,
        model="gpt-4.1-mini",
        model_settings=ModelSettings(temperature=0.7, top_p=0.9),
        tools=[
            HostedMCPTool(
                tool_config={
                    "type": "mcp",
                    "server_label": "supabase",
                    "server_url": f"https://mcp.supabase.com/mcp?project_ref={project_id}",
                    "authorization": access_token,
                    "require_approval": "never",
                }
            ),
            get_current_time,
            WebSearchTool(),
        ],
    )


async def run_pipeline(payload: Demo4Request) -> Demo4Result:
    base_dir = Path(__file__).resolve().parent
    business_prompt = _load_prompt(
        payload.business_prompt_path,
        base_dir / "business_expert_sys_prompt.md",
    )
    # print(business_prompt)
    market_prompt = _load_prompt(
        payload.market_prompt_path,
        base_dir / "market_analysis_prompt.md",
    )
    # print(market_prompt)
    customer_prompt_template = _load_prompt(
        payload.customer_prompt_path,
        base_dir / "customer_analysis_prompt.md",
    )
    # print(customer_prompt_template)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_dir = Path(payload.output_dir) if payload.output_dir else (base_dir / f"outputs_{timestamp}")
    if payload.save_files:
        output_dir.mkdir(parents=True, exist_ok=True)

    agent = _build_agent(payload.supabase_project_id, payload.supabase_access_token, business_prompt)
    # session_path = base_dir / f"{payload.user_name}_conversations.db"
    # session = SQLiteSession(payload.user_name, str(session_path))

    # Step 1: schema description
    schema_run = await Runner.run(
        agent,
        input=f"""
        <user's feedback>
        {payload.user_feedback}
        <user's feedback>
        
        Use supabase mcp tools, give me a description in Supabase public schema.
        
        """,
        # session=session,
    )
    schema_output = schema_run.final_output
    schema_path: Optional[Path] = None
    if payload.save_files:
        schema_path = output_dir / f"schema_description_{timestamp}.md"
        schema_path.write_text(schema_output, encoding="utf-8")

    # Step 2: market analysis
    market_run = await Runner.run(agent, input=
    f"""
    <user's feedback>
    {payload.user_feedback}
    <user's feedback>
    YOU CAN NOT CHANGE THE OUTPUT SCHEMA.
    {market_prompt}
    """
    )
    market_output = market_run.final_output
    market_json = json.loads(market_output)

    market_path: Optional[Path] = None
    if payload.save_files:
        market_path = output_dir / f"market_analysis_{timestamp}.md"
        market_path.write_text(market_output, encoding="utf-8")

    integrated_analysis = copy.deepcopy(market_json)


    # Step 3: customer analysis per market
    for entry in market_json.get("market_segments", []):
        market_name = entry.get("market_name", "unknown_market")
        prompt = (
            f"<user's feedback>{payload.user_feedback}<user's feedback>"
            f"YOU CAN NOT CHANGE THE OUTPUT SCHEMA."
            f"Based on our previous market analysis conversation, please focus on the market: **{market_name}**\n\n"
            f"{customer_prompt_template}\n"
        )
        customer_run = await Runner.run(agent, input=prompt)
        customer_output = customer_run.final_output
        customer_json = json.loads(customer_output)

        if payload.save_files:
            safe_name = market_name.replace(" ", "_").replace("/", "_")
            customer_path = output_dir / f"customer_analysis_{safe_name}_{timestamp}.md"
            customer_path.write_text(customer_output, encoding="utf-8")

        # Merge into integrated analysis
        target = next(
            (segment for segment in integrated_analysis.get("market_segments", []) if segment.get("market_name") == market_name),
            None,
        )
        if target is None:
            target = {"market_name": market_name}
            integrated_analysis.setdefault("market_segments", []).append(target)
        target["customer_analysis"] = customer_json

    # Step 4: persist combined outputs
    integrated_path: Optional[Path] = None
    if payload.save_files:
        integrated_payload = {
            "metadata": {
                "analysis_type": "integrated_market_and_customer",
                "analysis_timestamp": timestamp,
                "analysis_date": datetime.now().isoformat(),
            },
            "markets": integrated_analysis,
        }
        integrated_path = output_dir / f"integrated_analysis_{timestamp}.json"
        integrated_path.write_text(json.dumps(integrated_payload, indent=2, ensure_ascii=False), encoding="utf-8")


    return Demo4Result(
        integrated_analysis= integrated_payload if integrated_payload else None,
    )


# ---------------------------------------------------------------------------
# FastAPI wiring
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Demo-4 Analysis Service",
    description="Wraps the demo-4 market/customer analysis pipeline behind a REST API.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": "business-insighter", "version": "1.0.0"}


@app.post("/api/v1/run-analysis", response_model=Demo4Result)
async def run_analysis_endpoint(payload: Demo4Request) -> Demo4Result:
    try:
        if not payload.supabase_project_id or not payload.supabase_access_token:
            raise HTTPException(status_code=400, detail="Supabase credentials are required.")
        return await run_pipeline(payload)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "demo4_service:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
    )
