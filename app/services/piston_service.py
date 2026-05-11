import requests

# Piston API setup
PISTON_API_URL = "https://emkc.org/api/v2/piston/execute"

# frontend languages to Piston API requirements
LANGUAGE_MAP = {
    "python": {"language": "python", "version": "3.10.0"},
    "javascript": {"language": "javascript", "version": "18.15.0"}
}

def execute_code_against_tests(code, language, test_cases):
    # Takes user code and runs it against all test cases using Piston API Returns the evaluation summary.

    if language not in LANGUAGE_MAP:
        return {"status": "Compilation Error", "error": f"Unsupported language: {language}"}

    lang_config = LANGUAGE_MAP[language]
    passed_tests = 0
    total_tests = len(test_cases)
    final_stdout = ""
    final_stderr = ""
    final_status = "Accepted" 

    for index, test in enumerate(test_cases):
        # We append the input data to the user's code to simulate function execution
        # (In a real scenario, you'd wrap their code in a runner script, but this works for simple MVP)
        execution_payload = {
            "language": lang_config["language"],
            "version": lang_config["version"],
            "files": [{"content": code}],
            "stdin": test.input_data # Pass the test case input here
        }

        try:
            response = requests.post(PISTON_API_URL, json=execution_payload, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            run_data = result.get("run", {})
            stdout = run_data.get("stdout", "").strip()
            stderr = run_data.get("stderr", "").strip()
            signal = run_data.get("signal", None)

            # Keep track of outputs for the user to see (just save the last one, or combine)
            final_stdout = stdout
            final_stderr = stderr

            # Check for Errors
            if stderr or signal:
                final_status = "Runtime Error"
                break # Stop running tests if code crashes
            
            # Check Output against Expected Output
            if stdout == test.expected_output.strip():
                passed_tests += 1
            else:
                final_status = "Wrong Answer"
                break # Stop if a test fails (standard competitive programming logic)

        except requests.exceptions.Timeout:
            final_status = "Time Limit Exceeded"
            break
        except requests.exceptions.RequestException as e:
            return {"status": "System Error", "error": "Could not connect to execution engine."}

    return {
        "status": final_status,
        "passed_tests": passed_tests,
        "total_tests": total_tests,
        "stdout": final_stdout,
        "stderr": final_stderr
    }