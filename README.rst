Pyswan: Better dates & times for Python of Chinese
==================================================
**Pyswan** is a Python library that offers a sensible and human-friendly approach to creating, manipulating, formatting and converting dates, times and timestamps. It implements and updates the datetime type, plugging gaps in functionality and providing an intelligent module API that supports many common creation scenarios. Simply put, it helps you work with dates and times with fewer imports and a lot less code.


Quick Start
-----------

Installation
~~~~~~~~~~~~

To install Pyswan:

.. code-block:: console

    $ pip install -U pyswan

Example Usage
~~~~~~~~~~~~~

.. code-block:: python

    >>> import pyswan
    >>> pyswan.digitize(u"梁山一百零八好汉")
    '梁山108好汉'
    >>> pyswan.digitize("今天是周日")
    '今天是周7'
    >>> pyswan.parse('十二点三十分', dim=['time', 'number'])
    "[{'type': 'time', 'body': '12点30分', 'value': '2022-01-09 12:30:56'}, {'type': 'number', 'start': 0, 'end': 2, 'value': '12'}, {'type': 'number', 'start': 3, 'end': 5, 'value': '30'}]"

.. end-inclusion-marker-do-not-remove
