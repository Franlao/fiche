"""Couche LLM, servie par Pydantic AI. Reprise de celle d'ingest, avec le coût par appel.

Une seule opération : `structured(system, user, schema, check=None)` renvoie une instance
validée du schéma pydantic. Tout passe par le cache disque. Quand le modèle renvoie une sortie
mal formée, ou qu'un `check` métier la refuse, Pydantic AI la lui renvoie avec le reproche et
redemande (jusqu'à `RETRIES` fois).

Le coût est estimé d'après la table des prix embarquée dans Pydantic AI (genai-prices) ; un
modèle absent de la table compte `unknown_cost_usd`, pour que le budget ne file pas.
"""

from __future__ import annotations

import asyncio
import logging
import os
import threading
import time
from collections.abc import Callable, Coroutine
from datetime import timedelta
from typing import Any, TypeVar

from pydantic import BaseModel
from pydantic_ai import (
    Agent,
    ModelHTTPError,
    ModelRetry,
    NativeOutput,
    RunContext,
    UnexpectedModelBehavior,
    capture_run_messages,
)
from pydantic_ai.messages import ModelResponse
from pydantic_ai.models import Model
from pydantic_ai.settings import ModelSettings

from fiche.cache import DiskCache
from fiche.config import Provider, Settings
from fiche.errors import ProviderError

log = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)
R = TypeVar("R")
Check = Callable[[Any], str | None]
"""Validateur métier : None si la sortie convient, sinon le reproche à faire au modèle."""

DEFAULT_MODEL = {
    "mistral": "mistral-large-latest",
    "openai": "gpt-6.1-sol",
    "anthropic": "claude-opus-5-5",
}
MISTRAL_OPENAI_URL = "https://api.mistral.ai/v1"
RETRIES = 2
RETRY_STATUS = {408, 409, 429, 500, 502, 503, 504}
HTTP_ATTEMPTS = 4


class _SharedLoop:
    """Une boucle asyncio dans un fil dédié, pour tous les appels au modèle (les clients HTTP de
    Pydantic AI restent attachés à la boucle qui les a créés)."""

    def __init__(self) -> None:
        self.loop = asyncio.new_event_loop()
        thread = threading.Thread(target=self.loop.run_forever, name="fiche-llm", daemon=True)
        thread.start()

    def run(self, coro: Coroutine[Any, Any, R]) -> R:
        return asyncio.run_coroutine_threadsafe(coro, self.loop).result()


_shared: _SharedLoop | None = None
_shared_lock = threading.Lock()


def shared_loop() -> _SharedLoop:
    global _shared
    with _shared_lock:
        if _shared is None:
            _shared = _SharedLoop()
        return _shared


class LLMUsage(BaseModel):
    calls: int = 0
    cached_calls: int = 0
    retries: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    failed_calls: int = 0
    """Appels abandonnés après les reprises (sortie toujours refusée) : leur coût est compté."""
    cost_usd: float = 0.0
    """Coût estimé des appels non servis par le cache, appels abandonnés compris."""


class LLMProvider:
    """Appels structurés au modèle, avec cache disque, compteurs d'usage et coût."""

    def __init__(
        self,
        cache: DiskCache,
        model: Model | None,
        name: str,
        model_name: str,
        max_tokens: int,
        unknown_cost_usd: float = 0.02,
    ) -> None:
        self.cache = cache
        self.name = name
        self.model = model_name
        self.unknown_cost_usd = unknown_cost_usd
        self._model = model
        self._settings = ModelSettings(max_tokens=max_tokens)
        if name == "mistral":
            self._settings["temperature"] = 0.0
        self.usage = LLMUsage()
        self._lock = threading.Lock()
        self._agents: dict[type[BaseModel], Agent[Any, Any]] = {}

    def structured(
        self, system: str, user: str, schema: type[T], check: Check | None = None
    ) -> tuple[T, float]:
        """La sortie validée et le coût de l'appel (0 quand le cache a répondu)."""
        key = DiskCache.key(
            "llm",
            {
                "provider": self.name,
                "model": self.model,
                "system": system,
                "user": user,
                "schema": schema.model_json_schema(),
            },
        )
        cached = self.cache.get(key)
        if cached is not None:
            with self._lock:
                self.usage.cached_calls += 1
            return schema.model_validate(cached), 0.0
        result, in_tok, out_tok, retries, cost = self._call(system, user, schema, check)
        with self._lock:
            self.usage.calls += 1
            self.usage.retries += retries
            self.usage.input_tokens += in_tok
            self.usage.output_tokens += out_tok
            self.usage.cost_usd += cost
        self.cache.set(key, result.model_dump(mode="json"))
        return result, cost

    # --- Pydantic AI -------------------------------------------------------------------------

    def _model_for(self, schema: type[BaseModel]) -> Model:
        assert self._model is not None
        return self._model

    def _output_for(self, model: Model, schema: type[T]) -> Any:
        if model.profile.get("supports_json_schema_output"):
            return NativeOutput(schema, strict=True)
        return schema

    def _agent(self, schema: type[T]) -> Agent[Any, T]:
        with self._lock:
            agent = self._agents.get(schema)
            if agent is None:
                model = self._model_for(schema)
                agent = Agent(
                    model,
                    output_type=self._output_for(model, schema),
                    deps_type=object,
                    retries=RETRIES,
                    model_settings=self._settings,
                )

                @agent.output_validator
                async def _checked(ctx: RunContext[object], output: T) -> T:
                    check = ctx.deps
                    if callable(check):
                        problem = check(output)
                        if problem:
                            log.info(
                                "%s : sortie %s refusée : %s", self.name, schema.__name__, problem
                            )
                            raise ModelRetry(problem)
                    return output

                self._agents[schema] = agent
        return agent

    def _cost(self, messages: list[Any]) -> float:
        responses = [m for m in messages if isinstance(m, ModelResponse)]
        total = 0.0
        for response in responses:
            try:
                total += float(response.cost().total_price)
            except Exception:  # modèle hors table des prix
                total += self.unknown_cost_usd
        return total

    async def _run_captured(
        self, agent: Agent[Any, T], system: str, user: str, check: Check | None
    ) -> Any:
        # capture_run_messages dans la coroutine : le contexte ne traverse pas les fils
        with capture_run_messages() as messages:
            try:
                return await agent.run(user, instructions=system, deps=check)
            except UnexpectedModelBehavior as exc:
                raise _Abandoned(exc, list(messages)) from exc

    def _charge_failure(self, messages: list[Any]) -> None:
        responses = [m for m in messages if isinstance(m, ModelResponse)]
        in_tok = sum(r.usage.input_tokens or 0 for r in responses)
        out_tok = sum(r.usage.output_tokens or 0 for r in responses)
        cost = self._cost(messages)
        with self._lock:
            self.usage.failed_calls += 1
            self.usage.retries += max(0, len(responses) - 1)
            self.usage.input_tokens += in_tok
            self.usage.output_tokens += out_tok
            self.usage.cost_usd += cost

    def _call(
        self, system: str, user: str, schema: type[T], check: Check | None
    ) -> tuple[T, int, int, int, float]:
        agent = self._agent(schema)
        delay = 2.0
        for attempt in range(HTTP_ATTEMPTS):
            try:
                result = shared_loop().run(self._run_captured(agent, system, user, check))
            except ModelHTTPError as exc:
                retryable = exc.status_code in RETRY_STATUS
                if retryable and attempt < HTTP_ATTEMPTS - 1:
                    wait = _retry_after(exc) or delay
                    log.warning(
                        "%s : HTTP %s, nouvel essai dans %.0f s", self.name, exc.status_code, wait
                    )
                    time.sleep(wait)
                    delay *= 2
                    continue
                raise ProviderError(self.name, str(exc), retryable=retryable) from exc
            except _Abandoned as abandoned:
                # sortie toujours mal formée ou refusée par `check` : les requêtes sont payées
                self._charge_failure(abandoned.messages)
                raise ProviderError(self.name, str(abandoned.cause)) from abandoned.cause
            usage = result.usage  # attribut dans la version de Pydantic AI utilisée par ingest
            retries = max(0, (usage.requests or 1) - 1)
            cost = self._cost(result.new_messages())
            return (
                result.output,
                usage.input_tokens or 0,
                usage.output_tokens or 0,
                retries,
                cost,
            )
        raise ProviderError(self.name, "échec après plusieurs essais", retryable=True)


class _Abandoned(Exception):
    def __init__(self, cause: UnexpectedModelBehavior, messages: list[Any]) -> None:
        super().__init__(str(cause))
        self.cause, self.messages = cause, messages


def _retry_after(exc: ModelHTTPError) -> float | None:
    value = getattr(exc, "retry_after", None)
    if isinstance(value, timedelta):
        return max(value.total_seconds(), 0.5)
    if isinstance(value, int | float):
        return max(float(value), 0.5)
    return None


def _require(*names: str) -> str:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    raise ProviderError(names[0].split("_")[0].lower(), f"{' ou '.join(names)} manquant")


def build_model(provider: Provider, model_name: str | None) -> tuple[Model, str]:
    """Le modèle Pydantic AI pour un fournisseur, et son nom."""
    name = model_name or DEFAULT_MODEL.get(provider, "")
    if provider == "mistral":
        # Point d'entrée compatible OpenAI : sortie json_schema stricte, comme dans ingest
        # (MistralModel passe par un appel d'outil, moins fidèle sur le banc d'ingest).
        from pydantic_ai.models.openai import OpenAIChatModel
        from pydantic_ai.profiles.openai import OpenAIJsonSchemaTransformer, OpenAIModelProfile
        from pydantic_ai.providers.openai import OpenAIProvider

        model = OpenAIChatModel(
            name,
            provider=OpenAIProvider(
                base_url=MISTRAL_OPENAI_URL, api_key=_require("MISTRAL_API_KEY")
            ),
            profile=OpenAIModelProfile(
                supports_json_schema_output=True,
                json_schema_transformer=OpenAIJsonSchemaTransformer,
                openai_supports_strict_tool_definition=True,
            ),
        )
        return model, name
    if provider == "openai":
        from pydantic_ai.models.openai import OpenAIChatModel
        from pydantic_ai.providers.openai import OpenAIProvider

        return OpenAIChatModel(
            name, provider=OpenAIProvider(api_key=_require("OPENAI_API_KEY"))
        ), name
    if provider == "anthropic":
        from pydantic_ai.models.anthropic import AnthropicModel
        from pydantic_ai.providers.anthropic import AnthropicProvider

        key = _require("ANTHROPIC_API_KEY", "Claude_API_KEY")
        return AnthropicModel(name, provider=AnthropicProvider(api_key=key)), name
    if provider == "azure":
        from pydantic_ai.models.openai import OpenAIChatModel
        from pydantic_ai.providers.azure import AzureProvider

        name = name or _require("AZURE_OPENAI_DEPLOYMENT")
        model = OpenAIChatModel(
            name,
            provider=AzureProvider(
                azure_endpoint=_require("AZURE_OPENAI_ENDPOINT"),
                api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-10-21"),
                api_key=_require("AZURE_OPENAI_API_KEY"),
            ),
        )
        return model, name
    raise ValueError(f"Fournisseur LLM inconnu : {provider}")


def build_writer(settings: Settings, cache: DiskCache) -> LLMProvider:
    """Le modèle qui rédige (plan et blocs)."""
    if settings.llm_provider == "fake":
        raise ValueError("Le fournisseur 'fake' se construit explicitement avec un handler")
    model, name = build_model(settings.llm_provider, settings.llm_model)
    return LLMProvider(
        cache,
        model,
        settings.llm_provider,
        name,
        settings.llm_max_tokens,
        settings.unknown_cost_usd,
    )


def build_judge(settings: Settings, cache: DiskCache) -> LLMProvider:
    """Le modèle qui vérifie la fidélité des blocs."""
    if settings.judge_provider == "fake":
        raise ValueError("Le fournisseur 'fake' se construit explicitement avec un handler")
    model, name = build_model(settings.judge_provider, settings.judge_model)
    return LLMProvider(cache, model, settings.judge_provider, name, 4000, settings.unknown_cost_usd)


class FakeLLMProvider(LLMProvider):
    """Modèle local pour les tests : `handler(system, user, schema)` renvoie une instance du
    schéma. La réponse passe par Pydantic AI comme une vraie (schéma, validateurs, relances).
    Chaque appel coûte `cost` pour tester le budget."""

    def __init__(
        self,
        cache: DiskCache,
        handler: Callable[[str, str, type[Any]], Any],
        cost: float = 0.0,
    ) -> None:
        super().__init__(cache, None, "fake", "fake", 4000)
        self.handler = handler
        self.fake_cost = cost

    def _output_for(self, model: Model, schema: type[T]) -> Any:
        return schema

    def _cost(self, messages: list[Any]) -> float:
        return self.fake_cost * max(1, sum(isinstance(m, ModelResponse) for m in messages))

    def _model_for(self, schema: type[BaseModel]) -> Model:
        from pydantic_ai.messages import (
            InstructionPart,
            ModelMessage,
            SystemPromptPart,
            ToolCallPart,
            UserPromptPart,
        )
        from pydantic_ai.models.function import AgentInfo, FunctionModel

        def reply(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
            system = info.instructions or ""
            user = ""
            for message in messages:
                for part in getattr(message, "parts", []):
                    if isinstance(part, UserPromptPart) and isinstance(part.content, str):
                        user = part.content
                    elif not system and isinstance(part, SystemPromptPart | InstructionPart):
                        system = part.content
            output = self.handler(system, user, schema)
            tool = info.output_tools[0].name
            return ModelResponse(parts=[ToolCallPart(tool, output.model_dump(mode="json"))])

        return FunctionModel(reply)
