========================
GSpy-egse Python Package
========================


GSpy is a Python package for the verification of space instruments.

- Free software: BSD License
- Documentation: https://gspy-egse.readthedocs.io

Normal (user) installation
--------------------------
1. Clone this repository.
2. Create and activate a Python virtual environment.
3. From the repo root, install with GUI extras:

   .. code-block:: bash

      pip install .[gui]

4. Launch the GUI:

   .. code-block:: bash

      gspy-egse-gui

Editable (dev) installation
---------------------------
Use this if you plan to **modify the source** and see changes immediately (no reinstall needed).

.. code-block:: bash

   # from the repo root
   pip install -e .[dev]      # dev extras: lint/test tools, etc.
   # or minimal editable install:
   pip install -e .

Launch the GUI (same command):

.. code-block:: bash

   gspy-egse-gui

Using the Makefile
------------------
The repository includes a Makefile with common tasks. Run ``make help`` to see a summary.

.. code-block:: bash

   make help

Common targets:

- **Install (user mode):**

  .. code-block:: bash

     make install          # equivalent to: pip install .

- **Install (editable/dev mode):**

  .. code-block:: bash

     make install-dev      # equivalent to: pip install -e .

- **Quality & tests:**

  .. code-block:: bash

     make lint             # flake8 on package + tests
     make test             # pytest
     make coverage         # coverage HTML report and open it

- **Clean build/test artifacts:**

  .. code-block:: bash

     make clean            # removes build/, dist/, *.egg-info, __pycache__, etc.

- **Build distributions (sdist + wheel):**

  .. code-block:: bash

     make dist

- **Publish to PyPI (requires credentials & twine):**

  .. code-block:: bash

     make release

Windows: using the Makefile
---------------------------
Windows doesn’t ship with ``make`` by default. Choose **one** of the following:

1. **Git Bash + GNU Make (Chocolatey):**

   - Install Git for Windows (includes Git Bash).
   - Install make via Chocolatey:

     .. code-block:: bash

        choco install make

   - In **Git Bash**, run your Makefile commands:

     .. code-block:: bash

        make help
        make install
        make install-dev

2. **MSYS2:**

   - Install MSYS2, then:

     .. code-block:: bash

        pacman -S make

   - Use the MSYS2 shell to run ``make`` targets.

3. **Windows Subsystem for Linux (WSL):**

   - In your WSL distro (e.g., Ubuntu):

     .. code-block:: bash

        sudo apt update && sudo apt install make

   - Run the same ``make`` commands inside WSL.

Notes for Windows users
-----------------------
- If ``python`` maps to the Windows launcher, you can explicitly use it:

  .. code-block:: bash

     py -m pip install -e .[dev]

- Ensure your virtual environment is **activated** in the shell you use to run ``make``.
- If GUI shortcuts aren’t on PATH, you can still launch via:

  .. code-block:: bash

     python -m gspy_egse.gui


Demo GUI
---------------------
.. 
.. image:: figures/gspy-gui-demo16Jun.png
   :width: 600

.. list-table::
   :widths: 50 50
   :header-rows: 0

   * - .. image:: figures/gspy-gui-demo23Jun_spi.png
         :width: 200px
     - .. image:: figures/gspy-gui-demo23Jun_spacewire.png
         :width: 200px
   * - .. image:: figures/gspy-gui-demo23Jun_powersupply_single.png
         :width: 200px
     - .. image:: figures/gspy-gui-demo23Jun_powersupply_double.png
         :width: 200px
   * - .. image:: figures/gspy-gui-demo23Jun_housekeeping.png
         :width: 200px
     - .. image:: figures/gspy-gui-demo23Jun_file.png
         :width: 200px


Package Structure
-----------------
The project code lives under ``src/gspy_egse`` and is organized into:

* ``main.py`` – CLI entry point that launches the PyQt6 GUI.
* ``gui/`` – Qt widgets, plugin system, and hardware modules such as SpaceWire and power-supply drivers.
* ``utils/`` – shared helpers including the external recorder utility.
* ``tests/`` – pytest suite for hardware and utility components.

