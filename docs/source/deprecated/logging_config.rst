.. _logging.session:
.. index:: !Logging

=================
Configure Logging
=================

Configure logging for this session.

The level of detail for the logger is controlled by the *level*.
The level indicates the minimum severity of message to be reported, and can be set in the iconfig file.
In order of increasing detail: ``critical``, ``error``, ``warning`` (the default
level), ``info``, ``debug``.



Python logging's named levels
-----------------------------

BITS has seven *named* log levels.  The level specifies the minimum severity of
messages to report. Each named level is assigned a specific integer indicating
the severity of the log.

=========   =========   ==================================================
name        severity    comments
=========   =========   ==================================================
CRITICAL    50          Examine immediately. **Quietest** level.
ERROR       40          Something has failed.
WARNING     30          Something needs attention.
INFO        20          A report that may be of interest.
BSDEV       15          A report of interest to developers.
DEBUG       10          Diagnostic. **Noisiest** level.
NOTSET      0           Initial setting, defaults to WARNING.
=========   =========   ==================================================

.. tip:: Level names used in the ``configs/logging.yml`` file may be
    upper or lower case.  The code converts them to upper case.

References
----------

* https://blueskyproject.io/bluesky/main/debugging.html#logger-names
* https://blueskyproject.io/ophyd/user_v1/reference/logging.html#logger-names
