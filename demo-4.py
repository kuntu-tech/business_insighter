from datetime import datetime
import json
import sys
import os
import asyncio
import copy
from agents import Agent, Runner, function_tool, ModelSettings, HostedMCPTool, SQLiteSession, WebSearchTool
from pathlib import Path
from dotenv import load_dotenv
sys.path.append(str(Path(__file__).resolve().parent.parent))


load_dotenv()
SUPABASE_PROJECT_ID = os.getenv("SUPABASE_PROJECT_ID")
SUPABASE_ACCESS_TOKEN = os.getenv("SUPABASE_ACCESS_TOKEN")
SUPABASE_MCP_URL = f"https://mcp.supabase.com/mcp?project_ref={SUPABASE_PROJECT_ID}"
USER_NAME = "huimin"


### 1. 设置路径
BUSINESS_EXPERT_PROMPT = (Path(__file__).resolve().parent / "business_expert_sys_prompt.md").read_text(encoding="utf-8")
MARKET_ANALYSIS_PROMPT = (Path(__file__).resolve().parent / "market_analysis_prompt.md").read_text(encoding="utf-8")
CUSTOMER_ANALYSIS_PROMPT = (Path(__file__).resolve().parent / "customer_analysis_prompt.md").read_text(encoding="utf-8")
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
output_dir = Path(__file__).resolve().parent / f"outputs_{timestamp}"
output_dir.mkdir(exist_ok=True)


### 2. 工具函数
@function_tool
def get_current_time() -> str:
    return datetime.now().astimezone().isoformat()



### 3. 主函数
async def main():
    agent = Agent(
        name='business_expert',
        instructions=BUSINESS_EXPERT_PROMPT,
        model='gpt-4.1-mini',
        model_settings=ModelSettings(
            temperature=0.7,
            top_p=0.9
        ),
        tools=[
            HostedMCPTool(
                tool_config={
                    'type': "mcp",
                    "server_label": "supabase",
                    "server_url": SUPABASE_MCP_URL,
                    "authorization": SUPABASE_ACCESS_TOKEN,
                    "require_approval": "never"
                }
            ),
            get_current_time,
            WebSearchTool(),
        ],
    )
    session = SQLiteSession(USER_NAME, f"{USER_NAME}_conversations.db")
    
    # ========== Step 1: Schema Description ==========
    print("=" * 60)
    print("STEP 1: Schema Description")
    print("=" * 60)
    
    schema_analysis = await Runner.run(
        agent,
        input="Use supabase mcp tools, give me a description in Supabase public schema.",
        session=session
    )
    schema_analysis_output = schema_analysis.final_output
    
    schema_path = output_dir / f"schema_description_{timestamp}.md"
    schema_path.write_text(schema_analysis_output, encoding="utf-8")
    print(f"✓ Schema description saved to: {schema_path.name}\n")

    # ========== Step 2: Market Analysis ==========
    print("=" * 60)
    print("STEP 2: Market Analysis")
    print("=" * 60)
    
    market_analysis = await Runner.run(
        agent,
        input=MARKET_ANALYSIS_PROMPT,
        session=session
    )
    market_analysis_output = market_analysis.final_output
    
    market_path = output_dir / f"market_analysis_{timestamp}.md"
    market_path.write_text(market_analysis_output, encoding="utf-8")
    print(f"✓ Market analysis saved to: {market_path.name}")
    
    # 解析市场分析 JSON
    market_analysis_json = json.loads(market_analysis_output)
    # 在受众分析之前测试
    test_run = await Runner.run(
        agent,
        input=f"What was the TAM (Total Addressable Market) for {market_analysis_json['market_segments'][0]['market_name']} that we just analyzed?",
        session=session
    )
    print(f"Session test: {test_run.final_output[:100]}...")
    # 创建一个深拷贝用于合并受众分析（保持原始市场分析不变）
    integrated_analysis = copy.deepcopy(market_analysis_json)

    print(f"\n📊 Found {len(market_analysis_json['market_segments'])} market(s) to analyze:")

    # ========== Step 3: Customer Analysis for Each Market ==========
    print("=" * 60)
    print("STEP 3: Customer Analysis (循环处理每个市场)")
    print("=" * 60)
    
    
    for idx, market in enumerate(market_analysis_json["market_segments"], 1):
        market_name = market.get("market_name", f"market_{idx}")
        print(f"\n[{idx}/{len(market_analysis_json['market_segments'])}] Processing Market: {market_name}")

        # 3.1 执行受众分析 - 利用 session 上下文，无需传递完整市场数据
        customer_prompt = f"""
Based on our previous market analysis conversation, please focus on the market: **{market_name}**

{CUSTOMER_ANALYSIS_PROMPT}

"""
        try:
            customer_analysis = await Runner.run(
                agent,
                input=customer_prompt,
                session=session
            )
            customer_analysis_output = customer_analysis.final_output
            
            # 保存单个市场的受众分析
            safe_market_name = market_name.replace(" ", "_").replace("/", "_")
            customer_path = output_dir / f"customer_analysis_{safe_market_name}_{timestamp}.md"
            customer_path.write_text(customer_analysis_output, encoding="utf-8")
            print(f"   ✓ Customer analysis saved: {customer_path.name}")
            
            # 3.2 将受众分析合并到 integrated_analysis 中（不修改原始 market_analysis_json）
            customer_json = json.loads(customer_analysis_output)
            target_market_entry = None
            for entry in integrated_analysis.get("market_segments", []):
                if entry.get("market_name") == market_name:
                    target_market_entry = entry
                    break

            if target_market_entry is None:
                target_market_entry = {"market_name": market_name}
                integrated_analysis.setdefault("market_segments", []).append(target_market_entry)

            target_market_entry["customer_analysis"] = customer_json
            print("   ✓ Customer analysis merged into integrated analysis")

        except Exception as e:
            print(f"   ✗ Error processing market {market_name}: {e}\n")
            integrated_analysis[market_name]["customer_analysis"] = {
                "error": str(e),
                "status": "failed"
            }

    # ========== Step 4: 保存完整的分析结果 ==========
    print("=" * 60)
    print("STEP 4: Saving Complete Analysis Results")
    print("=" * 60)
    
    # 4.1 保存纯市场分析（不含受众分析）
    pure_market_analysis = {
        "metadata": {
            "analysis_type": "market_analysis_only",
            "analysis_timestamp": timestamp,
            "analysis_date": datetime.now().isoformat(),
        },
        "markets": market_analysis_json
    }
    
    pure_market_path = output_dir / f"market_analysis_pure_{timestamp}.json"
    pure_market_path.write_text(
        json.dumps(pure_market_analysis, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    print(f"✓ Pure market analysis saved: {pure_market_path.name}")
    
    # 4.2 保存集成分析（市场分析 + 受众分析）
    integrated_analysis_output = {
        "metadata": {
            "analysis_type": "integrated_market_and_customer",
            "analysis_timestamp": timestamp,
            "analysis_date": datetime.now().isoformat(),
        },
        "markets": integrated_analysis
    }
    
    integrated_path = output_dir / f"integrated_analysis_{timestamp}.json"
    integrated_path.write_text(
        json.dumps(integrated_analysis_output, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    print(f"✓ Integrated analysis saved: {integrated_path.name}")
    
    # 4.3 保存所有验证报告汇总
    
    
    # # 返回关键数据供后续使用
    # return {
    #     "market_analysis": market_analysis_json,
    #     "integrated_analysis": integrated_analysis,
    #     "validation_reports": all_validation_reports,
    #     "timestamp": timestamp
    # }


if __name__ == "__main__":
    asyncio.run(main())
