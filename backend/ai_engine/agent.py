# agent.py
import os
from openai import OpenAI

# Initialize client (Make sure your OPENAI_API_KEY is exported in your environment variables)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "your-fallback-key-if-applicable"))

SYSTEM_PROMPT = """You are the PHOENIX AI Forensic Assistant, an expert administrative AI specializing in multi-modal video container forensics, deepfake localization, and blockchain chain-of-custody verification.

Your task is to analyze the provided JSON forensic payload and answer investigator questions accurately, professionally, and objectively. 
- Use strict technical terminology when relevant (e.g., GOP frames, compression targets, smart contract mapping slots, SHA-256 fingerprint matching).
- Cite specific metrics from the payload (like confidence scores, resolution, frame rates, or blockchain hashes) to back up your claims.
- Do not fabricate data. If the forensic payload does not contain information requested by the investigator, state clearly that it is outside the current captured telemetry.
"""

def generate_forensic_response(user_prompt: str, forensic_payload: dict) -> str:
    """
    Ingests an investigator's query along with the complete JSON payload of the 
    video asset, then queries the LLM to get an explainable answer.
    """
    try:
        # Structure the payload data cleanly as context for the LLM
        context = f"FORENSIC PAYLOAD DATA:\n{forensic_payload}\n"
        
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Using an efficient, high-context model suitable for payloads
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"{context}\n\nInvestigator Query: {user_prompt}"}
            ],
            temperature=0.2, # Low temperature ensures focused, fact-based forensic data retrieval
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Forensic Agent Error: Failed to generate response from neural framework. Details: {str(e)}"