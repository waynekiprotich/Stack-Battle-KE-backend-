import requests

# The URL for the code execution API
PISTON_URL = "https://emkc.org/api/v2/piston/execute"

# Map our language names to Piston's requirements
LANG_MAP = {
    "python": {
        "language": "python",
        "version": "3.10.0",
    },
    "javascript": {
        "language": "javascript",
        "version": "18.15.0",
    },
}

def run_code(language, code, stdin=""):
    # Check if the language is supported
    if language not in LANG_MAP:
        raise ValueError(f"Unsupported language: {language}. Use 'python' or 'javascript'.")

    lang_cfg = LANG_MAP[language]

    # Setup the data to send to the API
    payload = {
        "language": lang_cfg["language"],
        "version": lang_cfg["version"],
        "files": [{"content": code}],
        "stdin": stdin or "",
        "run_timeout": 5000,       
        "compile_timeout": 10000,  
        "run_memory_limit": 128,   
    }

    try:
        # Send the request to Piston
        resp = requests.post(PISTON_URL, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.Timeout:
        return {"stdout": "", "stderr": "Execution timed out.", "code": 1, "time": 0}
    except requests.exceptions.RequestException as e:
        return {"stdout": "", "stderr": f"Piston API error: {str(e)}", "code": 1, "time": 0}

    # Get the results from the response
    run = data.get("run", {})
    return {
        "stdout": run.get("stdout", ""),
        "stderr": run.get("stderr", ""),
        "code": run.get("code", 1),
        "time": run.get("time", 0),
    }