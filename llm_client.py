#!/usr/bin/env python3
"""LLM client with FriendliAI and OpenAI fallback."""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def get_llm_client():
    """Get LLM client with OpenAI as primary."""
    openai_key = os.getenv("OPENAI_API_KEY")
    friendli_key = os.getenv("FRIENDLI_API_KEY")
    
    # Try OpenAI first (more reliable)
    if openai_key:
        try:
            client = OpenAI(api_key=openai_key)
            print("✅ Using OpenAI")
            return client, "gpt-4o-mini"
        except Exception as e:
            print(f"⚠️  OpenAI failed: {e}")
    
    # Fallback to FriendliAI
    if friendli_key:
        try:
            client = OpenAI(
                api_key=friendli_key,
                base_url="https://inference.friendli.ai/v1"
            )
            # Test the connection with a simple call
            test_response = client.chat.completions.create(
                model="meta-llama/Meta-Llama-3.1-8B-Instruct",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            print("✅ Using FriendliAI")
            return client, "meta-llama/Meta-Llama-3.1-8B-Instruct"
        except Exception as e:
            print(f"⚠️  FriendliAI failed: {e}")
    
    raise ValueError("No working LLM API key found. Please set OPENAI_API_KEY or FRIENDLI_API_KEY")

def generate_memo(name: str, stage: str, check_size: str, horizon: str, context: str):
    """Generate VC memo using available LLM."""
    import json
    from prompts import SYSTEM_PROMPT, format_user_prompt
    
    client, model = get_llm_client()
    user_prompt = format_user_prompt(name, stage, check_size, horizon, context)
    
    # Try with JSON mode first
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
        
        content = response.choices[0].message.content
        
        # Validate JSON before returning
        json.loads(content)  # This will raise an exception if invalid
        return content
        
    except Exception as e:
        print(f"⚠️  JSON mode failed: {e}")
        
        # Fallback: try without JSON mode and clean up response
        try:
            response = client.chat.completions.create(
                model=model,
                temperature=0.2,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT + " Return ONLY valid JSON, no other text."},
                    {"role": "user", "content": user_prompt},
                ],
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to extract JSON from response
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            # Validate JSON
            json.loads(content)
            return content
            
        except Exception as e2:
            print(f"❌ Fallback also failed: {e2}")
            
            # Return a default JSON structure
            return json.dumps({
                "verdict": "Pass",
                "scores": {
                    "team": 0,
                    "problem": 0,
                    "market": 0,
                    "moat": 0,
                    "traction": 0,
                    "gtm": 0,
                    "unit_economics": 0,
                    "risks": 5
                },
                "pros": ["Analysis unavailable due to LLM error"],
                "cons": ["Unable to generate proper analysis"],
                "key_metrics": ["Analysis failed"],
                "biggest_risks": ["LLM response parsing failed"],
                "fit_for_profile": "Unable to assess fit due to technical issues",
                "disclaimer": "This analysis failed due to technical issues and should not be used for investment decisions"
            })