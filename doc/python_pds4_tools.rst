:orphan:

Python PDS4 Tools
=================

Introduction
------------

Python PDS4 Tools is pure-Python package that can read and display PDS4 data and
meta data. This tool supports all common PDS4 data structures as listed in the
Supported Data Structures section. The package expects valid PDS4 labels
formatted according to the PDS4 Standard.

An `PDS4 reader and visualizer for IDL <https://pds-smallbodies.astro.umd.edu/tools/tools_readPDS.shtml>`_
is separately available.

Contact `Lev Nagdimunov <https://sbnwiki.asteroiddata.org/User:Lnagdi1.html>`__
with questions or comments regarding this tool, or report issues on
`GitHub <https://github.com/Small-Bodies-Node/pds4_tools>`_.

Installation
------------

Python PDS4 Tools is a pure-Python package available in PyPi and CondaForge.

Install an official release
"""""""""""""""""""""""""""

To install the package via ``pip``, run this command::

  python -m pip install -U pds4_tools

To install the package via ``conda``, run this command::

  conda install -c conda-forge pds4_tools

Install from source
"""""""""""""""""""

You may also install the latest development version from `GitHub <https://github.com/Small-Bodies-Node/pds4_tools>`_::

  git clone https://github.com/Small-Bodies-Node/pds4_tools.git
  cd pds4_tools
  python -m pip install .

.. _download_python_pds4_tools:

Download
--------

| Download the `development source code <https://github.com/Small-Bodies-Node/pds4_tools>`_
  from GitHub.
| Download the latest official release:
  `PDS4 tools-1.4.tar.gz <https://pdssbn.astro.umd.edu/toolsrc/readpds_python/1.4/PDS4_tools-1.4.tar.gz>`_.
  Released on March 16, 2025.

Note: A distributable version of the viewer only, which does not require Python,
is :doc:`available <pds4_viewer>`.

Requirements
------------

Python 2.7 or 3.5+

| pds4_read: `NumPy <https://www.numpy.org>`_
| pds4_viewer: `NumPy <https://www.numpy.org>`_, `matplotlib <https://www.matplotlib.org>`_

User Manual
-----------

Online `documentation <https://pdssbn.astro.umd.edu/tools/pds4_tools_docs/current/>`_,
both for scientists and for developers, is available.

Supported Data Structures
-------------------------

| PDS4 Data Standards >= v1.0 are supported.
| PDS3 Data Standards are not supported.

The table below lists the main PDS4 data structures and the current status.

.. list-table::
   :widths: 25 25 25 25 25
   :header-rows: 1

   * - Structure
     - Read-in
     - Display as Table
     - Display as Image
     - Display Columns as Plot
   * - Header
     -  Yes
     -  No
     -  No
     -  No
   * - Array
     - Yes
     - Yes
     - Yes, N-dims
     - Yes, 1-D only
   * - Array_2D
     - Yes
     - Yes
     - Yes
     - No
   * - Array_2D_*
     - Yes
     - Yes
     - Yes
     - No
   * - Array_3D
     - Yes
     - Yes
     - Yes
     - No
   * - Array_3D_*
     - Yes
     - Yes
     - Yes
     - No
   * - Table_Character
     - Yes
     - Yes
     - No
     - Yes
   * - Table_Binary
     - Yes, except BitFields
     - Yes
     - No
     - Yes
   * - Table_Delimited
     - Yes
     - Yes
     - No
     - Yes
   * - Composite_Structure
     - No
     - No
     - No
     - No
