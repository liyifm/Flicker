from flicker.services.memory.fs.datasource import FileSystemDataSource
from typing import Union, Annotated
from pydantic import Field


DataSourceUnion = Annotated[
    Union[FileSystemDataSource],
    Field(discriminator='type')
]
