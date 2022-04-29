"""
------------------------------------------------------------------------------
Setup file for autoloading '_about.py' information in standard distributions.
Looks for the '_about.py' file under the second level of the project folder.
------------------------------------------------------------------------------
Copyright - Francisco José Mata Aroco (https://github.com/fjmaro)
See LICENSE.md file in this project for further details (setup.py v1.0.0)
------------------------------------------------------------------------------
"""
# pylint: disable=exec-used, line-too-long
import glob
import pathlib
from setuptools import setup, find_packages

here = pathlib.Path(__file__).parent.resolve()
aboutpath = [x for x in glob.glob(str(here) + "/*/*") if "_about.py" in x]

if len(aboutpath) == 0:
    FileNotFoundError(
        "SetupError: File '_about.py' not found in package level './*/*'")
elif len(aboutpath) > 1:
    FileExistsError(
        "SetupError: Only one '_about.py' file is allowed in the package")

readmefound = pathlib.Path(here / "README.md").is_file()
assert readmefound, "SetupError: 'README.md' file not found"

about: dict = {}
with open(aboutpath[0], "r", encoding='utf-8') as fhd:
    exec(fhd.read(), about)

setup(name=about['__title__'],
      version=about['__version__'],
      description=about['__summary__'],
      long_description=(here / "README.md").read_text(encoding="utf-8"),
      long_description_content_type="text/markdown",
      url=about['__uri__'],
      author=about['__author__'],
      author_email=about['__email__'],
      license=about['__license__'],
      packages=find_packages(),
      classifiers=about['CLASSIFIERS'],
      python_requires=about['PYTHON_REQUIRES'],
      install_requires=about['INSTALL_REQUIRES'],
      package_data=about['PACKAGE_DATA'])
