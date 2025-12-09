from PySide6.QtCore import QThread, QObject, Signal
from pydantic import BaseModel, Field
from typing import Optional, Callable
from os import walk
from os.path import splitext
from time import time
from loguru import logger
from pathlib import Path
from datetime import datetime
from uuid import UUID, uuid4


class FileScanningOptions(BaseModel):
    root_directory: str
    extension_names: set[str]
    excluded_directories: list[str]
    after: Optional[datetime] = None


class FileScanningResult(BaseModel):
    paths: list[Path] = Field(default_factory=list)


class FileScannerInstance(QObject):
    scanningFinished = Signal()

    def __init__(self, options: FileScanningOptions) -> None:
        super().__init__()
        self.instance_id = uuid4()
        self.options = options
        self.working_thread = QThread()
        self.result = FileScanningResult()

    def start(self) -> None:
        logger.info(f'start file scanning: {self.options.root_directory}')
        start = time()
        total_files = 0

        for current_directory, sub_directories, filenames in walk(self.options.root_directory):
            excluded = False
            for exclude in self.options.excluded_directories:
                if current_directory.startswith(exclude):
                    excluded = True
                    break

            if excluded:
                # if the current directory is excluded, all subdirectories are excluded either
                sub_directories.clear()
                continue

            for filename in filenames:
                _, extension_name = splitext(filename)
                extension_name = extension_name.lower()
                if extension_name not in self.options.extension_names:
                    continue

                file_path = Path(current_directory) / filename
                file_stat = file_path.stat()
                total_files += 1
                self.result.paths.append(file_path)

        cost = time() - start
        logger.info(f'file scanning task takes {cost:.2f} seconds with {total_files} files')

        # todo: should be decoupled later
        # from flicker.services.llm.embedding import EmbeddingService
        # from flicker.utils.settings import Settings
        # EmbeddingService.startEmbedding(
        #     Settings.loadDefault().default_embed_model,
        #     [p.name for p in self.result.paths]
        # )

        self.scanningFinished.emit()


class FileScanner:
    scanning_tasks: dict[UUID, FileScannerInstance] = dict()

    @classmethod
    def startScanning(cls, options: FileScanningOptions) -> None:
        inst = FileScannerInstance(options)
        cls.scanning_tasks[inst.instance_id] = inst
        inst.working_thread.started.connect(inst.start)
        inst.working_thread.finished.connect(lambda: cls.finalizeScanning(inst))
        inst.scanningFinished.connect(inst.working_thread.quit)
        inst.moveToThread(inst.working_thread)
        inst.working_thread.start()

    @classmethod
    def finalizeScanning(cls, inst: FileScannerInstance) -> None:
        logger.info(f'finalizing scanning task {inst.instance_id}')
        del cls.scanning_tasks[inst.instance_id]
