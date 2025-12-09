from flicker.services.memory.base import AbstractDataSource
from flicker.services.memory.fs.scanner import FileScanner, FileScanningOptions
from pydantic import BaseModel, Field
from typing import Literal, Callable


DEFAULT_SUPPORTED_EXTENSIONS = [
    ".png", ".jpg", ".jpeg", ".webp",
    ".ppt", ".pptx",
    ".doc", ".docx",
    ".pdf",
    ".txt"
]


class FileSystemDataSource(BaseModel, AbstractDataSource):
    type: Literal['file_system'] = 'file_system'
    root_directory: str
    extension_names: list[str] = Field(default_factory=lambda: list(DEFAULT_SUPPORTED_EXTENSIONS))
    excluded_directories: list[str] = Field(default_factory=list)
    database_file: str = ""

    def startUpdate(self, on_finished: Callable[[], None] | None = None):
        FileScanner.startScanning(FileScanningOptions(
            root_directory=self.root_directory,
            extension_names=set(self.extension_names),
            excluded_directories=self.excluded_directories
        ))

    def save(self) -> None:
        pass
