"""
Device factories
================

Device factories are used to:

* *Create* several similar ophyd-style devices (such as ``ophyd.Device``
  or ``ophyd.Signal``) that fit a pattern.

* *Import* a device which is pre-defined in a module, such as the
  ophyd simulators in ``ophyd.sim``.

.. autosummary::

    ~factory_base
    ~motors
    ~predefined_device
"""

import logging

from apstools.utils import dynamic_import

logger = logging.getLogger(__name__)
logger.bsdev(__file__)


def predefined_device(*, name="", creator=""):
    """
    Provide a predefined device such as from the 'ophyd.sim' module.

    PARAMETERS

    creator : str
        Name of the predefined device to be used
    name : str
        Simulator will be assigned this name.  (default: use existing name)

    Example entry in `devices.yml` file:

    .. code-block:: yaml
        :linenos:

        instrument.devices.factories.predefined_device:
          - {creator: ophyd.sim.motor, name: sim_motor}
          - {creator: ophyd.sim.noisy_det, name: sim_det}
    """
    if creator == "":
        raise ValueError("Must provide a value for 'creator'.")
    device = dynamic_import(creator)
    if name != "":
        device.name = name
    logger.debug(device)
    yield device


def factory_base(
    *,
    prefix=None,
    names="object{}",
    first=0,
    last=0,
    creator="ophyd.Signal",
    **kwargs,
):
    """
    Make one or more objects using  'creator'.

    PARAMETERS

    prefix : str
        Prefix *pattern* for the EPICS PVs (default: ``None``).

    names : str
        Name *pattern* for the objects.  The default pattern is ``"object{}"`` which
        produces devices named ``object1, object2, ..., ```.  If a formatting
        specification (``{}``) is not provided, it is appended.  Each object
        will be named using this code: ``names.format(number)``, such as::

            In [23]: "object{}".format(22)
            Out[23]: 'object22'

    first : int
        The first object number in the continuous series from 'first' through
        'last' (inclusive).

    last : int
        The first object number in the continuous series from 'first' through
        'last' (inclusive).

    creator : str
        Name of the *creator* code that will be used to construct each device.
        (default: ``"ophyd.Signal"``)

    kwargs : dict
        Dictionary of additional keyword arguments.  This is included
        when creating each object.
    """
    if "{" not in names:
        names += "{}"
    if prefix is not None and "{" not in prefix:
        prefix += "{}"

    klass = dynamic_import(creator)

    first, last = sorted([first, last])
    for i in range(first, 1 + last):
        keywords = {"name": names.format(i)}
        if prefix is not None:
            keywords["prefix"] = prefix.format(i)
        keywords.update(kwargs)
        device = klass(**keywords)
        logger.debug(device)
        yield device


def motors(
    *,
    prefix=None,
    names="m{}",
    first=0,
    last=0,
    **kwargs,
):
    """
    Make one or more '``ophyd.EpicsMotor``' objects.

    Example entry in `devices.yml` file:

    .. code-block:: yaml
        :linenos:

        instrument.devices.factories.motors:
          - {prefix: "ioc:m", first: 1, last: 4, labels: ["motor"]}
          # skip m5 & m6
          - {prefix: "ioc:m", first: 7, last: 22, labels: ["motor"]}

    Uses this pattern:

    .. code-block:: py
        :linenos:

        ophyd.EpicsMotor(
                prefix=prefix.format(i),
                name=names.format(i),
                **kwargs,
            )

    where ``i`` iterates from 'first' through 'last' (inclusive).

    PARAMETERS

    prefix : str
        Name *pattern* for the EPICS PVs.  There is no default pattern. If a
        formatting specification (``{}``) is not  provided, it is appended (as
        with other ophyd devices).  Each motor will be configured with this
        prefix: ``prefix.format(number)``, such as::

            In [23]: "ioc:m{}".format(22)
            Out[23]: 'ioc:m22'

    names : str
        Name *pattern* for the motors.  The default pattern is ``"m{}"`` which
        produces motors named ``m1, m2, ..., m22, m23, ...```.  If a formatting
        specification (``{}``) is not provided, it is appended.  Each motor
        will be named using this code: ``names.format(number)``, such as::

            In [23]: "m{}".format(22)
            Out[23]: 'm22'

    first : int
        The first motor number in the continuous series from 'first' through
        'last' (inclusive).

    last : int
        The first motor number in the continuous series from 'first' through
        'last' (inclusive).

    kwargs : dict
        Dictionary of additional keyword arguments.  This is included
        with each EpicsMotor object.
    """
    if prefix is None:
        raise ValueError("Must define a string value for 'prefix'.")

    kwargs["names"] = names or "m{}"
    kwargs["prefix"] = prefix
    kwargs.update(
        {
            "prefix": prefix,
            "names": names or "m{}",
            "first": first,
            "last": last,
            "creator": "ophyd.EpicsMotor",
        }
    )

    for motor in factory_base(**kwargs):
        yield motor
