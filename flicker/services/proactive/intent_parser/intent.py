from pydantic import BaseModel, Field
from typing import Type, List, ClassVar, Optional, Iterable
from pathlib import Path
from loguru import logger


class Intent(BaseModel):
    name: str
    description: str
    parameterSchema: Type[BaseModel]


class IntentRegistry(BaseModel):
    intents: List[Intent] = Field(default_factory=list)
    _instance: ClassVar[Optional['IntentRegistry']] = None

    @classmethod
    def getInstance(cls) -> 'IntentRegistry':
        """ Return a global instance of intent registry """
        if cls._instance is not None:
            return cls._instance

        instance = IntentRegistry()
        cls._instance = instance
        instance.loadPredefinedIntents()
        return instance

    def registerIntent(self, intent: Intent) -> None:
        self.intents.append(intent)

    def getIntents(self) -> Iterable[Intent]:
        return self.intents

    def loadPredefinedIntents(self) -> None:
        """ Load predefined intents into the registry """
        import importlib.util

        intents_dir = Path(__file__).parent / "intents"
        if intents_dir.exists():
            for file_path in intents_dir.glob("*.py"):
                if file_path.name == "__init__.py":
                    continue

                spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
                if spec is None or spec.loader is None:
                    continue

                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, Intent):
                        logger.info("register predefined intent: " + attr.name)
                        self.registerIntent(attr)
