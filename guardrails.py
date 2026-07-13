import re

class GuardrailManager:
    def __init__(self):
        # A list of basic heuristics representing malicious prompt manipulation attempts
        self.injection_keywords = [
            "ignore previous instructions",
            "system prompt",
            "ignore the rules",
            "you must now act as",
            "override instructions"
        ]
        # Regex pattern to match PII/API keys (e.g., secret_api_key_xxx or generic password formats)
        self.sensitive_patterns = [
            r"(?i)password\s*=\s*\S+",
            r"(?i)api_key\s*=\s*\S+",
            r"secret_api_key_[a-zA-Z0-9]+"
        ]

    def validate_input(self, user_prompt: str) -> bool:
        """
        Input Guardrail: Screens for potential Prompt Injection or Jailbreak keywords.
        Returns True if input is safe, False if a security threat is detected.
        """
        normalized_prompt = user_prompt.lower()
        for pattern in self.injection_keywords:
            if pattern in normalized_prompt:
                print(f"[!] SECURITY WARNING: Input blocked. Detected Prompt Injection pattern: '{pattern}'")
                return False
        return True

    def validate_output(self, llm_response: str) -> str:
        """
        Output Guardrail: Screens LLM output for potential data leakage before it reaches the user.
        Replaces sensitive leaks with redaction strings.
        """
        sanitized_response = llm_response
        for pattern in self.sensitive_patterns:
            if re.search(pattern, sanitized_response):
                print("[!] SECURITY WARNING: Output Guardrail triggered. Redacting sensitive data from LLM response.")
                sanitized_response = re.sub(pattern, "[REDACTED_SENSITIVE_DATA]", sanitized_response)
        return sanitized_response
