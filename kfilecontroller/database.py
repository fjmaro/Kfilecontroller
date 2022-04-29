"""database dataclass"""
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class Kdatabase:
    """database containing path-files info"""
    paths: tuple[Path, ...] = ()
    names: tuple[str, ...] = ()
    md5s: tuple[str, ...] = ()


class KdtbTools:
    """basic tools to work with Kdatabase"""
    @staticmethod
    def save_database(database: Kdatabase, output_file: Path) -> None:
        """save the database info"""
        data2save = np.array(([str(x) for x in database.paths],
                              database.names, database.md5s), dtype=str)
        np.save(output_file, data2save)

    @staticmethod
    def load_database(file: Path) -> Kdatabase:
        """load the database saved"""
        data_loaded = np.load(file)
        return Kdatabase([Path(x) for x in data_loaded[0, :]],
                         data_loaded[1, :], data_loaded[2, :])
