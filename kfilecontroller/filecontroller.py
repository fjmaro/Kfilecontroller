"""filecontroller"""
from logging import Logger
from pathlib import Path

from tqdm import tqdm
from kjmarotools.basics import filetools, ostools

from .database import Kdatabase, KdtbTools


class FileController:
    """
    --------------------------------------------------------------------------
    Kjmaro FileController
    --------------------------------------------------------------------------
    --------------------------------------------------------------------------
    """
    # pylint: disable=too-many-instance-attributes
    def __init__(self, base_path2scan: Path, database_file: Path,
                 logger: Logger, fold_patterns: tuple[str, ...] = ()) -> None:

        self.base_path2scan = base_path2scan
        self.database_file = database_file
        self.fld_patterns = fold_patterns
        self.log = logger

        # Class database loaded and updated
        self.current_database: Kdatabase
        self.loaded_database: Kdatabase
        self.files_added: Kdatabase
        self.files_lost: Kdatabase
        self.files_found: Kdatabase
        self.__phs = "[FLC] <NewModulePhase> "
        self.__res = "[FLC] <NewResultsBlock> "

    def load_and_create_current_database(self) -> None:
        """
        ----------------------------------------------------------------------
        Load the database file and analyse the path to create the current one
        ----------------------------------------------------------------------
        """
        self.log.info(f"{self.__phs}Generating current files dabase...")
        if self.database_file.exists():
            self.loaded_database = KdtbTools.load_database(self.database_file)
        else:
            self.loaded_database = Kdatabase((), (), ())

        folders2scan = filetools.get_folders_tree(self.base_path2scan,
                                                  self.fld_patterns)
        files_in_path = filetools.get_files_tree(folders2scan)

        md5s: list[str] = []
        names: list[str] = []
        paths: list[Path] = []

        for file in tqdm(files_in_path):
            paths.append(file)
            names.append(file.name)
            md5s.append(ostools.md5checksum(file, 2**26))

        self.current_database = Kdatabase(tuple(
            paths), tuple(names), tuple(md5s))

    def find_new_and_lost_files_since_last_execution(self) -> None:
        """
        ----------------------------------------------------------------------
        Get the files lost and added since last execution
        ----------------------------------------------------------------------
        """
        self.log.info(f"{self.__phs}Finding files added and removed...")

        new_md5s: list[str] = []
        new_names: list[str] = []
        new_paths: list[Path] = []
        for idx, this_path in enumerate(self.current_database.paths):
            if this_path not in self.loaded_database.paths:
                new_paths.append(this_path)
                new_names.append(self.current_database.names[idx])
                new_md5s.append(self.current_database.md5s[idx])

        del_md5s: list[str] = []
        del_names: list[str] = []
        del_paths: list[Path] = []
        for idx, this_path in enumerate(self.loaded_database.paths):
            if this_path not in self.current_database.paths:
                del_paths.append(this_path)
                del_names.append(self.current_database.names[idx])
                del_md5s.append(self.current_database.md5s[idx])
                self.log.warning("[FLC] [FileDeleted]: %s | %s | %s",
                                 del_md5s[-1],
                                 del_names[-1], str(del_paths[-1].relative_to(
                                     self.base_path2scan)))

        self.log.info(f"{self.__res}New files found = %s",
                      str(len(new_names)))
        self.log.info(f"{self.__res}Files deleted found = %s",
                      str(len(del_names)))

        self.files_added = Kdatabase(
            tuple(new_paths), tuple(new_names), tuple(new_md5s))
        self.files_lost = Kdatabase(
            tuple(del_paths), tuple(del_names), tuple(del_md5s))

    def try_to_find_deleted_files(self):
        """
        ----------------------------------------------------------------------
        Try to find the deleted files
        ----------------------------------------------------------------------
        """
        self.log.info(f"{self.__phs}Finding deleted files in given path...")
        for idx, md5val in enumerate(self.files_lost.md5s):
            if md5val in self.files_added.md5s:
                match_paths: list[str] = []

                for jdx, jmd5val in self.files_added.md5s:
                    if jmd5val == md5val:
                        match_paths.append(str(self.files_added.paths[jdx]))

                fmsg = "[FLC] [ProbablyFound]: %s %s | LOST | %s | FOUND | %s"
                self.log.info(fmsg, md5val, self.files_lost.names[idx],
                              self.files_lost.paths[idx],
                              str(match_paths))

    def update_the_database_file(self):
        """
        ----------------------------------------------------------------------
        Update the database file with the current information
        ----------------------------------------------------------------------
        """
        KdtbTools.save_database(self.current_database, self.database_file)

    def run(self, embedded=False, skip_dtb_updates=False) -> bool:
        """
        ----------------------------------------------------------------------
        Execute FileController with the defined configuration
        - embedded: It won't stop after the execution
        - skip_dtb_updates: If this is enabled the database is not updated
                            after the execution of run().
        ----------------------------------------------------------------------
        return:
            - True: Files deleted found
            - False: No deleted files are found
        ----------------------------------------------------------------------
        """
        self.log.info("[FLC] <INIT> FileController initialized ...")
        self.log.info(f"[FLC] <CNFG> base_path2scan = {self.base_path2scan}")
        self.log.info(f"[FLC] <CNFG> fld_patterns = {self.fld_patterns}")
        self.log.info("[FLC] <TAGS> [FileDeleted] [ProbablyFound]")

        self.load_and_create_current_database()
        self.find_new_and_lost_files_since_last_execution()
        self.try_to_find_deleted_files()
        if not skip_dtb_updates:
            self.update_the_database_file()

        if not embedded:
            if len(self.files_lost.md5s) > 0:
                print("+------------------------+")
                print("|        WARNING         |")
                print("+------------------------+")
                print("|  Deleted files found.  |")
                print("| see log for more info. |")
                print("+------------------------+")
            input("\nPROCESS FINALIZED\n\n\t\tPRESS ENTER TO RESUME")
        return len(self.files_lost.md5s) > 0
