from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional, Dict, Any
from dataclasses import dataclass

import httpx
import ollama
import json
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings
from app.utils.logger import logger


@dataclass
class LLMResponse:
    content: str
    model: str
    done: bool
    total_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    eval_count: Optional[int] = None


class BaseLLM(ABC):
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        pass

    @abstractmethod
    async def stream_generate(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        pass


class OllamaLLM(BaseLLM):
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.temperature = settings.ollama_temperature
        self.top_p = settings.ollama_top_p
        self.max_tokens = settings.ollama_max_tokens
        self.num_ctx = settings.ollama_num_ctx
        
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(120.0)
            )
        return self._client

    async def generate(self, prompt: str, **kwargs) -> str:
        temperature = kwargs.get("temperature", self.temperature)
        top_p = kwargs.get("top_p", self.top_p)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        
        try:
            client = ollama.AsyncClient(host=self.base_url, timeout=120.0)
            response = await client.generate(
                model=self.model,
                prompt=prompt,
                options={
                    "temperature": temperature,
                    "top_p": top_p,
                    "num_predict": max_tokens,
                    "num_ctx": self.num_ctx
                }
            )
            logger.info(f"Ollama generate completed, model: {self.model}")
            return response["response"]
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            raise

    async def stream_generate(
        self,
        prompt: str,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        temperature = kwargs.get("temperature", self.temperature)
        top_p = kwargs.get("top_p", self.top_p)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        
        try:
            client = ollama.AsyncClient(host=self.base_url, timeout=120.0)
            async for chunk in await client.generate(
                model=self.model,
                prompt=prompt,
                stream=True,
                options={
                    "temperature": temperature,
                    "top_p": top_p,
                    "num_predict": max_tokens,
                    "num_ctx": self.num_ctx
                }
            ):
                if chunk.get("response"):
                    yield chunk["response"]
        except Exception as e:
            logger.error(f"Ollama stream error: {e}")
            raise


class HuggingFaceLLM(BaseLLM):
    def __init__(self):
        self.model_name = settings.hf_model_name
        self.device = settings.hf_device_map
        self.temperature = settings.ollama_temperature
        self.max_tokens = settings.ollama_max_tokens
        self._pipeline = None

    @property
    def pipeline(self):
        if self._pipeline is None:
            from transformers import pipeline
            logger.info(f"Loading HuggingFace model: {self.model_name}")
            self._pipeline = pipeline(
                "text-generation",
                model=self.model_name,
                device=self.device,
                torch_dtype="auto"
            )
            logger.info("HuggingFace model loaded")
        return self._pipeline

    async def generate(self, prompt: str, **kwargs) -> str:
        import torch
        temperature = kwargs.get("temperature", self.temperature)
        max_new_tokens = kwargs.get("max_tokens", self.max_tokens)
        
        with torch.no_grad():
            outputs = self.pipeline(
                prompt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=temperature > 0,
                pad_token_id=0
            )
        
        return outputs[0]["generated_text"].replace(prompt, "")

    async def stream_generate(
        self,
        prompt: str,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        import torch
        temperature = kwargs.get("temperature", self.temperature)
        max_new_tokens = kwargs.get("max_tokens", self.max_tokens)
        
        inputs = self.pipeline.preprocess([prompt])
        
        generation_kwargs = dict(
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=temperature > 0,
            pad_token_id=0
        )
        
        with torch.no_grad():
            streamer = self.pipeline._get_streamer(
                inputs,
                **generation_kwargs
            )
            
            generation_kwargs["streamer"] = streamer
            
            import asyncio
            task = self.pipeline.generate(
                inputs,
                **generation_kwargs
            )
            
            async for text in asyncio.to_thread(streamer.__iter__):
                yield text
        
        await task


class OpenRouterLLM(BaseLLM):
    def __init__(self):
        self.api_key = settings.openrouter_api_key
        self.model = settings.openrouter_model
        self.base_url = settings.openrouter_base_url
        self.temperature = settings.ollama_temperature
        self.max_tokens = settings.ollama_max_tokens

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException)),
        reraise=True,
        before_sleep=lambda retry_state: logger.info(f"Retrying OpenRouter call... (attempt {retry_state.attempt_number})")
    )
    async def generate(self, prompt: str, **kwargs) -> str:
        if not self.api_key or "your_openrouter_api_key_here" in self.api_key:
            raise ValueError("OpenRouter API key is missing. Please set OPENROUTER_API_KEY in .env")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/google-deepmind/antigravity",
            "X-Title": "AI Tutor Backend",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens)
        }

        async with httpx.AsyncClient(timeout=300.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                
                if not isinstance(data, dict):
                    raise Exception(f"OpenRouter returned unexpected data type: {type(data)}. Response: {data}")

                if "choices" in data and len(data["choices"]) > 0:
                    choice = data["choices"][0]
                    if "message" in choice and "content" in choice["message"]:
                        return choice["message"]["content"]
                    else:
                        raise Exception(f"OpenRouter choice missing message content: {choice}")
                elif "error" in data:
                    error_msg = data["error"].get("message", str(data["error"]))
                    raise Exception(f"OpenRouter API error: {error_msg}")
                else:
                    raise Exception(f"OpenRouter unexpected response format (missing 'choices'): {data}")
            except Exception as e:
                logger.error(f"OpenRouter generation error: {str(e)}")
                raise

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException)),
        reraise=True,
        before_sleep=lambda retry_state: logger.info(f"Retrying OpenRouter stream... (attempt {retry_state.attempt_number})")
    )
    async def stream_generate(
        self,
        prompt: str,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        if not self.api_key or "your_openrouter_api_key_here" in self.api_key:
            raise ValueError("OpenRouter API key is missing. Please set OPENROUTER_API_KEY in .env")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/google-deepmind/antigravity",
            "X-Title": "AI Tutor Backend",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "stream": True
        }

        async with httpx.AsyncClient(timeout=300.0) as client:
            try:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            if line.strip() == "data: [DONE]":
                                break
                            try:
                                data = json.loads(line[6:])
                                if isinstance(data, dict) and "choices" in data and len(data["choices"]) > 0:
                                    delta = data["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        yield content
                            except Exception as e:
                                logger.debug(f"OpenRouter stream chunk parse error: {e}")
                                continue
            except Exception as e:
                logger.error(f"OpenRouter stream error: {str(e)}")
                raise


class LLMService:
    def __init__(self):
        self.provider = settings.llm_provider
        self._llm: Optional[BaseLLM] = None

    @property
    def llm(self) -> BaseLLM:
        if self._llm is None:
            if self.provider == "ollama":
                self._llm = OllamaLLM()
                logger.info("Using Ollama LLM")
            elif self.provider == "openrouter":
                self._llm = OpenRouterLLM()
                logger.info(f"Using OpenRouter LLM ({settings.openrouter_model})")
            else:
                self._llm = HuggingFaceLLM()
                logger.info("Using HuggingFace LLM")
        return self._llm

    async def generate(self, prompt: str, **kwargs) -> str:
        return await self.llm.generate(prompt, **kwargs)

    async def stream_generate(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        async for token in self.llm.stream_generate(prompt, **kwargs):
            yield token


llm_service = LLMService()
