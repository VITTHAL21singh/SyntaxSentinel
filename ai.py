import json
import ollama

def analyze_image(filepath, user_query=""):
    system_instruction = f"""
    You are a strict application security auditor. Analyze this uploaded image for vulnerabilities.
    
    User Context/Question: {user_query if user_query else "Analyze the image generally for security flaws."}
    
    Respond ONLY with a raw JSON object. Do not use markdown formatting.
    Required JSON schema:
    {{
        "vulnerability": "Brief title of the flaw",
        "severity": "Critical, High, Medium, or Low",
        "remediation": "Concise, actionable step to fix the issue"
    }}
    """
    try:
        response = ollama.generate(
            model='gemma4:31b-cloud',
            prompt=system_instruction,
            images=[filepath],
            format='json'
        )
    except json.JSONDecodeError:
        raise Exception(f"Failed to parse JSON. Check terminal for raw output.")
    except Exception as e:
        raise Exception(f"AI Analysis Failed: {str(e)}")
