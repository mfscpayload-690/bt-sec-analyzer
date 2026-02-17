"""
Ollama client for local LLM integration.

Provides log summarization and analysis using locally-running Qwen Coder.
"""

import json
from typing import Any, Dict, List, Optional

try:
    import ollama
except ImportError:
    ollama = None

from bt_sectester.utils.logger import LoggerMixin


class OllamaClient(LoggerMixin):

    """Client for Ollama local LLM service."""

    def __init__(
        self,
        host: str = "http://localhost:11434",
        model: str = "qwen2.5-coder:7b",
        timeout: int = 60,
    ):
        """
        Initialize Ollama client.

        Args:
            host: Ollama server host
            model: Model name to use
            timeout: Request timeout in seconds

        Raises:
            RuntimeError: If Ollama library not available
        """
        if ollama is None:
            raise RuntimeError("Ollama library not installed. Run: pip install ollama")

        self.host = host
        self.model = model
        self.timeout = timeout

        # Test connection
        self._test_connection()

    def _test_connection(self) -> None:
        """Test connection to Ollama server."""
        try:
            # Try to list models to verify connection
            client = ollama.Client(host=self.host)
            models = client.list()
            self.logger.info(
                "Connected to Ollama",
                host=self.host,
                available_models=len(models.get("models", [])),
            )
        except Exception as e:
            self.logger.error("Failed to connect to Ollama", error=str(e), host=self.host)
            raise RuntimeError(f"Cannot connect to Ollama at {self.host}: {e}") from e

    def summarize_logs(
        self,
        logs: List[Dict[str, Any]],
        context: Optional[str] = None,
    ) -> str:
        """
        Summarize log entries using LLM.

        Args:
            logs: List of log entry dictionaries
            context: Optional context about the operation

        Returns:
            Summary text
        """
        self.logger.debug("Summarizing logs", log_count=len(logs))

        # Prepare log data for the model
        log_text = "\n".join(
            [f"[{log.get('timestamp', 'N/A')}] {log.get('event', log)}" for log in logs]
        )

        prompt = f"""You are a security analyst reviewing Bluetooth security testing logs.

Context: {context or 'Bluetooth security assessment'}

Logs:
{log_text}

Please provide a concise summary of these logs, highlighting:
1. Key events and actions performed
2. Any anomalies or errors
3. Important security findings
4. Overall assessment

Summary:"""

        try:
            response = self._generate(prompt)
            self.logger.info("Log summarization complete")
            return response
        except Exception as e:
            self.logger.error("Log summarization failed", error=str(e))
            raise

    def analyze_attack_results(
        self,
        attack_type: str,
        results: Dict[str, Any],
    ) -> str:
        """
        Analyze attack simulation results.

        Args:
            attack_type: Type of attack (dos, hijack, mitm, etc.)
            results: Attack results dictionary

        Returns:
            Analysis text
        """
        self.logger.debug("Analyzing attack results", attack_type=attack_type)

        results_json = json.dumps(results, indent=2)

        prompt = f"""You are a security analyst reviewing results from a Bluetooth security test.

Attack Type: {attack_type}

Results:
{results_json}

Please provide a professional analysis including:
1. What the test attempted to do
2. Whether the test was successful
3. Potential vulnerabilities or weaknesses identified
4. Recommendations for remediation
5. Risk assessment

Analysis:"""

        try:
            response = self._generate(prompt)
            self.logger.info("Attack analysis complete", attack_type=attack_type)
            return response
        except Exception as e:
            self.logger.error("Attack analysis failed", attack_type=attack_type, error=str(e))
            raise

    def extract_key_insights(
        self,
        text: str,
        max_insights: int = 5,
    ) -> List[str]:
        """
        Extract key insights from text.

        Args:
            text: Text to analyze
            max_insights: Maximum number of insights to extract

        Returns:
            List of insight strings
        """
        prompt = f"""Extract the {max_insights} most important insights from this text.
Provide them as a numbered list.

Text:
{text}

Key insights:"""

        try:
            response = self._generate(prompt)

            # Parse numbered list
            insights = []
            for line in response.split("\n"):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith("-") or line.startswith("•")):
                    # Remove numbering
                    insight = line.lstrip("0123456789.-•) ").strip()
                    if insight:
                        insights.append(insight)

            return insights[:max_insights]

        except Exception as e:
            self.logger.error("Insight extraction failed", error=str(e))
            return []

    def _generate(self, prompt: str, stream: bool = False) -> str:
        """
        Generate text using the LLM.

        Args:
            prompt: Input prompt
            stream: Whether to stream response

        Returns:
            Generated text
        """
        try:
            client = ollama.Client(host=self.host)

            response = client.generate(
                model=self.model,
                prompt=prompt,
                stream=stream,
            )

            if stream:
                # Handle streaming response
                full_response = ""
                for chunk in response:
                    full_response += chunk.get("response", "")
                return full_response
            else:
                return response.get("response", "")

        except Exception as e:
            self.logger.error("LLM generation failed", error=str(e))
            raise

    def chat(
        self,
        messages: List[Dict[str, str]],
    ) -> str:
        """
        Chat with the LLM using conversation history.

        Args:
            messages: List of message dicts with 'role' and 'content'

        Returns:
            Response text
        """
        try:
            client = ollama.Client(host=self.host)

            response = client.chat(
                model=self.model,
                messages=messages,
            )

            return response.get("message", {}).get("content", "")

        except Exception as e:
            self.logger.error("Chat failed", error=str(e))
            raise
