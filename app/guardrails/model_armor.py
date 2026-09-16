"""Google Cloud Model Armor Inline Guardrail Simulation & Sanitization."""
import re
import time
from typing import Dict, Any, Tuple

class ModelArmorScanner:
    def __init__(self):
        self.injection_patterns = [
            r"ignore\s+(all\s+)?(previous|prior)\s+(instructions|rules|constraints|prompts)",
            r"disable\s+safety\s+filters",
            r"(print\s+out|reveal|show|display|leak)\s+(the\s+|your\s+)?(bearer\s+token|secret|system\s+prompt|api\s+token|api\s+key|tokens)",
            r"override\s+system\s+prompt",
            r"reveal\s+developer\s+mode",
            r"jailbreak",
            r"bypass\s+safety"
        ]
        self.spii_patterns = {
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "credit_card": r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14})\b",
            "email_domain": r"[a-zA-Z0-9_.+-]+@(?:gmail|yahoo|hotmail)\.com"
        }
        self.out_of_domain_keywords = [
            "pytorch", "tensorflow", "cnn", "convolutional", "write a python script to",
            "stock trading", "crypto investment", "horoscope", "quantum mechanics"
        ]

    def scan_input(self, user_prompt: str) -> Tuple[bool, str, Dict[str, Any]]:
        start_time = time.time()
        prompt_lower = user_prompt.lower()
        
        # 1. Adversarial / Prompt Injection Check
        for pattern in self.injection_patterns:
            if re.search(pattern, prompt_lower):
                elapsed_ms = int((time.time() - start_time) * 1000)
                return False, "I cannot fulfill this request as it violates security policies.", {
                    "verdict": "DENIED",
                    "violation": "PROMPT_INJECTION",
                    "latency_ms": elapsed_ms
                }
                
        # 2. Domain Boundary Containment Check
        for keyword in self.out_of_domain_keywords:
            if keyword in prompt_lower:
                elapsed_ms = int((time.time() - start_time) * 1000)
                return False, "I am specialized strictly for corporate HR policies, WorkWeek, and ServiceImmediately support.", {
                    "verdict": "DENIED",
                    "violation": "OUT_OF_DOMAIN",
                    "latency_ms": elapsed_ms
                }
                
        elapsed_ms = int((time.time() - start_time) * 1000)
        return True, user_prompt, {"verdict": "ALLOWED", "latency_ms": elapsed_ms}

    def sanitize_output(self, text: str) -> Tuple[str, Dict[str, Any]]:
        start_time = time.time()
        sanitized = text
        redacted = False
        for p_name, regex in self.spii_patterns.items():
            if re.search(regex, sanitized):
                sanitized = re.sub(regex, f"[REDACTED_{p_name.upper()}]", sanitized)
                redacted = True
                
        elapsed_ms = int((time.time() - start_time) * 1000)
        return sanitized, {
            "verdict": "SPII_REDACTED" if redacted else "ALLOWED",
            "latency_ms": elapsed_ms
        }

model_armor = ModelArmorScanner()
