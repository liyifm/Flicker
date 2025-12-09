from flicker.utils.settings import ModelRef
from openai import OpenAI
from loguru import logger
from pydantic import BaseModel
from itertools import batched
from time import time
from typing import Optional


class EmbeddingOptions(BaseModel):
    batch_size: int
    dimension: int

    @classmethod
    def default(cls) -> 'EmbeddingOptions':
        return EmbeddingOptions(
            batch_size=64,
            dimension=256
        )


class EmbeddingService:
    @classmethod
    def startEmbedding(cls, model_ref: ModelRef, texts: list[str], options: Optional[EmbeddingOptions] = None) -> None:
        logger.info(f'start embedding for {len(texts)} text chunks')
        if options is None:
            options = EmbeddingOptions.default()

        client = OpenAI(api_key=model_ref.api_key, base_url=model_ref.base_url)
        N = len(texts) // options.batch_size + (1 if len(texts) % options.batch_size != 0 else 0)
        start_time = time()
        total_tokens = 0

        for i, payload in enumerate(batched(texts, options.batch_size)):
            resp = client.embeddings.create(
                model=model_ref.model_name,
                input=payload,
                dimensions=options.dimension
            )
            total_tokens += resp.usage.total_tokens
            total_tps = total_tokens / (time() - start_time)
            logger.info(f"processed batch {i + 1} / {N} embeddings, total tokens {total_tokens}, tps {total_tps:.2f}")
