"""running FileController by default - example"""
from pathlib import Path

from kjmarotools.basics import logtools

from kfilecontroller import FileController


if __name__ == "__main__":
    this_file_path = Path(__file__).parent.resolve()
    logger = logtools.get_fast_logger("FileController", this_file_path)
    folder_patterns = ("1.*", "2.*", "3.*", "4.*", "5.*", )
    FileController(this_file_path, Path.cwd().joinpath("databasetest"),
                   logger, folder_patterns).run()
