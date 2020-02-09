Developing get dem nuts
=======================

Prerequisites
-------------
* Python 3.6+
* Pip

Environment
-----------

### Windows

```cmd
python3 -m venv env
env\Scripts\activate.bat
pip install -r requirements.txt
```

### Linux/OSX

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

Run get dem nuts
----------------

Activate the envionment as above and run:

```bash
python -m main
```

Testing
-------

Activate the envionment as above and run:

```bash
pytest test
```

Packaging
---------

[PyInstaller](https://www.pyinstaller.org/) is used to package get dem nuts into a standalone binary for Windows, Linux, and OSX.

Activate the envionment as above and run:

### Windows

```cmd
package.bat
```

### Linux/OSX

```bash
./package.sh
```
