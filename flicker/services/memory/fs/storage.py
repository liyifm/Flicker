from pathlib import Path
from typing import Optional
from loguru import logger
from threading import current_thread

import sqlite3


CREATE_FILE_INFO = """
CREATE TABLE IF NOT EXISTS fileinfo (
    file_path TEXT PRIMARY KEY,
    file_name TEXT,
    created_time TIMESTAMP,
    modified_time TIMESTAMP,
    accessed_time TIMESTAMP
);
"""

INSERT_FILE_INFO = """
INSERT INTO fileinfo (
    file_path, file_name,
    created_time, modified_time, accessed_time
) VALUES (
    :file_path, :file_name,
    :created_time, :modified_time, :accessed_time
) ON CONFLICT(file_path) DO UPDATE SET
    file_name = :file_name,
    created_time = :created_time,
    modified_time = :modified_time,
    accessed_time = :accessed_time
;
"""


class FSStorage:

    _instances: dict[int, 'FSStorage'] = dict()

    @classmethod
    def getInstance(cls) -> 'FSStorage':
        thread_id = current_thread().ident
        if thread_id is None:
            raise RuntimeError("the thread is not started yet")

        if thread_id in cls._instances:
            return cls._instances[thread_id]

        from flicker.utils.settings import Settings
        db_path = Settings.getSettingsDirectory() / "fsmemory.db"
        instance = FSStorage(db_path)
        if instance.db_list_tables() == []:
            instance.db_initialize()

        cls._instances[thread_id] = instance
        return instance

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.__connection = sqlite3.connect(self.db_path)

    def getFileInfo(self, path: Path) -> dict:
        stat = path.stat()
        return {
            "file_path": str(path),
            "file_name": path.name,
            "created_time": int(stat.st_birthtime),
            "modified_time": int(stat.st_mtime),
            "accessed_time": int(stat.st_atime)
        }

    def addFiles(self, paths: list[Path]) -> None:
        logger.info(f'generating stat for {len(paths)} files')
        infos = [self.getFileInfo(path) for path in paths]

        try:
            logger.info('start batch inserting')
            self.__connection.execute("BEGIN TRANSACTION")
            cursor = self.__connection.cursor()
            cursor.executemany(INSERT_FILE_INFO, infos)
            self.__connection.commit()
            logger.info(f'finish batch insert {len(paths)} file info rows')
        except Exception as ex:
            logger.error(f'failed to batch insert: {ex}')
            self.__connection.rollback()

    def db_initialize(self) -> None:
        logger.info(f'initialize database @ {self.db_path}')
        cursor = self.__connection.cursor()
        cursor.execute(CREATE_FILE_INFO)
        self.__connection.commit()

    def db_list_tables(self) -> list[str]:
        cursor = self.__connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        return [table[0] for table in tables]
