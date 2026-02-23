core/llm_manager.py
"""
LLM Manager - Handles OpenAI, Claude, and Grok integration
"""
import os
from typing import Optional, Dict, Any, List
from openai import AsyncOpenAI
import anthropic
import httpx
from core.logger import get_logger

logger = get_logger(__name__)


class LLMManager:
    """
    Manages multiple LLM providers with fallback support
    Primary: OpenAI GPT-4o
    Fallback: Anthropic Claude
    Alternative: Grok
    """
    
    def __init__(
        self,
        openai_key: str = "",
        anthropic_key: str = "",
        grok_key: str = "",
        default_model: str = "gpt-4o"
    ):
        self.openai_key = openai_key or os.getenv("OPENAI_API_KEY")
        self.anthropic_key = anthropic_key or os.getenv("ANTHROPIC_API_KEY")
        self.grok_key = grok_key or os.getenv("GROK_API_KEY")
        self.default_model = default_model
        
        # Initialize clients
        self.openai_client = None
        self.anthropic_client = None
        
        if self.openai_key:
            self.openai_client = AsyncOpenAI(api_key=self.openai_key)
            logger.info("✓ OpenAI client initialized")
        
        if self.anthropic_key:
            self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_key)
            logger.info("✓ Anthropic Claude client initialized")
        
        if not self.openai_client and not self.anthropic_client:
            logger.warning("⚠ No LLM clients initialized - check API keys")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> str:
        """
        Generate response from LLM with fallback support
        
        Args:
            prompt: User prompt
            system_prompt: System instructions
            model: Model to use (default: default_model)
            temperature: Creativity level (0-1)
            max_tokens: Maximum tokens in response
        
        Returns:
            LLM response text
        """
        model = model or self.default_model
        
        # Try OpenAI first
        if self.openai_client and "gpt" in model.lower():
            try:
                response = await self.openai_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt or "You are an expert programmer AI assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                logger.debug(f"✓ OpenAI response received ({model})")
                return response.choices[0].message.content
            except Exception as e:
                logger.warning(f"OpenAI error: {e}, trying fallback...")
        
        # Try Anthropic Claude
        if self.anthropic_client and "claude" in model.lower():
            try:
                response = self.anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt or "You are an expert programmer AI assistant.",
                    messages=[{"role": "user", "content": prompt}]
                )
                logger.info("✓ Anthropic Claude response received")
                return response.content[0].text
            except Exception as e:
                logger.warning(f"Claude error: {e}")
        
        # Try Grok as last resort
        if self.grok_key:
            try:
                return await self._call_grok(prompt, system_prompt, temperature)
            except Exception as e:
                logger.warning(f"Grok error: {e}")
        
        # No providers available
        logger.error("❌ No LLM providers available")
        return "Error: No LLM providers configured"
    
    async def _call_grok(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float
    ) -> str:
        """Call Grok API"""
        # Note: Grok integration requires xAI API setup
        # This is a placeholder implementation
        headers = {
            "Authorization": f"Bearer {self.grok_key}",
            "Content-Type": "application/json"
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.x.ai/v1/chat/completions",
                headers=headers,
                json={
                    "model": "grok-beta",
                    "messages": [
                        {"role": "system", "content": system_prompt or "You are an expert programmer."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": temperature
                },
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
    
    async def analyze_code(
        self,
        code: str,
        issue_description: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze code to understand the issue and generate solution
        
        Args:
            code: The code to analyze
            issue_description: Description of the issue
            context: Additional context about the repository
        
        Returns:
            Dictionary with analysis and solution
        """
        prompt = f"""
You are an expert software engineer analyzing a code issue.

## Issue Description
{issue_description}

## Code to Analyze
```{get_code_language(code)}
{code}
