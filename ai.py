import json
import re
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
    except Exception as e:
        raise Exception(f"AI Analysis Failed: {str(e)}")

    # Extract text from response (supports both GenerateResponse object and dict)
    if hasattr(response, 'response'):
        raw_text = response.response
    elif isinstance(response, dict):
        raw_text = response.get('response', '')
    else:
        raw_text = str(response)

    raw_text = raw_text.strip()

    # Remove markdown code blocks if the model wrapped output in ```json ... ```
    if raw_text.startswith('```'):
        raw_text = re.sub(r'^```(?:json)?\s*', '', raw_text)
        raw_text = re.sub(r'\s*```$', '', raw_text)

    # Attempt to parse JSON
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        # Fallback: search for JSON object within text
        match = re.search(r'\{[\s\S]*\}', raw_text)
        if match:
            try:
                data = json.loads(match.group(0))
            except json.JSONDecodeError:
                data = {
                    "vulnerability": "Security Analysis Note",
                    "severity": "Info",
                    "remediation": raw_text
                }
        else:
            data = {
                "vulnerability": "Security Analysis Note",
                "severity": "Info",
                "remediation": raw_text
            }

    # Ensure required fields exist
    if isinstance(data, dict):
        if "vulnerability" not in data:
            data["vulnerability"] = "Unspecified Vulnerability"
        if "severity" not in data:
            data["severity"] = "Medium"
        if "remediation" not in data:
            data["remediation"] = "Review code and architecture for potential flaws."
    elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        data = data[0]
    else:
        data = {
            "vulnerability": "Analysis Completed",
            "severity": "Info",
            "remediation": str(data)
        }

    return data
