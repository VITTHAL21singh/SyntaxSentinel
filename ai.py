import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

# This forces Python to read your .env file
load_dotenv()

# The client will now successfully find GEMINI_API_KEY
client = genai.Client()
def analyze_image(filepath):
    system_instruction = """
    You are a strict application security auditor and hardware architecture expert. 
    Analyze this uploaded image (which may be a network diagram, code snippet, or architecture layout) for vulnerabilities or critical design flaws.
    You must respond ONLY with a raw JSON object. Do not include markdown formatting, code blocks (```json), or any conversational text.
    
    Required JSON schema:
    {
        "vulnerability": "Brief title of the primary flaw",
        "severity": "Critical, High, Medium, or Low",
        "remediation": "Concise, actionable step to fix the issue"
    }
    """

    genai_file = None
    try:
        genai_file = client.files.upload(file=filepath)
        response = client.models.generate_content(
            model='gemma-4',
            contents=[system_instruction, genai_file],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )        
        audit_data = json.loads(response.text)
        return audit_data

    except json.JSONDecodeError:
        return {
            "vulnerability": "API Output Parsing Error",
            "severity": "Medium",
            "remediation": f"The model failed to return strict JSON. Raw output: {response.text}"
        }
    except Exception as e:
        raise Exception(f"AI Analysis Failed: {str(e)}")
        
    finally:
        if genai_file:
            client.files.delete(name=genai_file.name)