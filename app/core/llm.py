from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseLanguageModel
from langchain_core.outputs import LLMResult, Generation
from langchain_core.prompt_values import PromptValue
from typing import List, Any, Optional, Iterator, AsyncIterator

# --- vLLM Configuration ---
VLLM_MODEL_NAME = "Qwen/Qwen3-14B"
VLLM_API_BASE = "http://localhost:7052/v1"
REQUEST_TIMEOUT = 300


# --- Mock LLM Fallback ---
class MockLLM(BaseLanguageModel):
    def invoke(self, prompt: str, **kwargs: Any) -> str:
        return f"[MOCK] {prompt[:100]}..."

    def _generate(self, prompts: List[str], **kwargs: Any) -> LLMResult:
        generations = [[Generation(text=self.invoke(p))] for p in prompts]
        return LLMResult(generations=generations)

    def generate_prompt(self, prompts: List[PromptValue], **kwargs: Any) -> LLMResult:
        return self._generate([p.to_string() for p in prompts])

    async def agenerate_prompt(self, prompts: List[PromptValue], **kwargs: Any) -> LLMResult:
        return self.generate_prompt(prompts)

    @property
    def _llm_type(self) -> str:
        return "mock"

    def _stream(self, prompt: str, **kwargs: Any) -> Iterator[Generation]:
        yield Generation(text=self.invoke(prompt))

    async def _astream(self, prompt: str, **kwargs: Any) -> AsyncIterator[Generation]:
        yield Generation(text=self.invoke(prompt))


# --- LLM Client ---
try:
    llm: BaseLanguageModel = ChatOpenAI(
        model=VLLM_MODEL_NAME,
        openai_api_base=VLLM_API_BASE,
        openai_api_key="EMPTY",
        temperature=0.1,
        max_tokens=2048,
        request_timeout=REQUEST_TIMEOUT,
    )
    print(f"✅ Connected to vLLM @ {VLLM_API_BASE}")

except Exception as e:
    print(f"⚠️ vLLM unavailable, using MockLLM: {e}")
    llm = MockLLM()
