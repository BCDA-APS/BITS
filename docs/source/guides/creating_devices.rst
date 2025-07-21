.. _creating_devices:

Adding Devices to an Instrument
-----------------------------------------

Every new instrument comes pre-loaded with a simulated motor and a detector. To add a new device to your instrument startup, a couple of steps must be taken.
For the purpose of this tutorial we assume you have already used BITS to create an instrument called `new_instrument`.

1. Create a new device class in the devices folder

.. code-block:: python

    from ophyd import Device, EpicsMotor
    from ophyd import Component as Cpt

    class StageXY(Device):
        x = Cpt(EpicsMotor, ':X')
        y = Cpt(EpicsMotor, ':Y')

2. Add the new device class to the device ``my_instrument/devices/__init__.py`` file

If you want to use a device from an external package, make sure to add it to the ``my_instrument/devices/__init__.py`` file in the device folder of your instrument.

.. code-block:: python

    from .stage_xy import StageXY ##import from your own devices folder

3. Add the new device to the instrument configuration file

Depending on if the device can only function on the aps network or not add it to the ``device.yml`` file or the ``devices_aps_only.yml`` file.


.. code-block:: yaml

    new_instrument.devices.StageXY:
    - name: stage
      prefix: BITS
      labels: ["motors"]

You can also add a device from an external package to the ``devices.yml`` file.

.. code-block:: yaml

     apstools.synApps.Optics2Slit2D_HV:
     - name: slit1
       prefix: ioc:Slit1
       labels: ["slits"]


.. tip::
    `APSTOOLS <https://github.com/BCDA-APS/apstools/tree/main/apstools>`_ has a lot of devices commonly used at the APS. Consider first checking the package and overwriting the device class to fit your needs before creating a new device.

.. tip::
    You can add the `label: baseline` to any device in your configuration to automatically track its state during scans. This is particularly useful for monitoring environmental conditions or instrument parameters. For example:

    .. code-block:: yaml

        apstools.devices.ApsMachineParametersDevice:
        - name: aps
          labels:
          - baseline

        ophyd.EpicsSignalRO:
        - name: temperature_monitor
          prefix: "IOC:TEMP"
          labels:
          - baseline

    Baseline devices will be automatically included in the metadata of each scan, making it easy to track changes in environmental conditions or instrument parameters over time.
