.. _TestingPage:


Testing the system
******************

To test the systems it is necessary to be able to send data to NodeRED (MQTT/UDP) or directly
to the Kakfa server. Transmission can be either continuous over time, with the right frequency of each device,
or at a bulk of a certain period of time.

This section shows how to create mock-devices that will mimic the real devices.
Obviously, the data for all the fields is just randomized.

Device configuration
====================

The devices are specified by a JSON configuration file.

The configuration file can be created from the experiment that was downloaded from argosWEB
or manually.

The definition of each
.. code-block:: javascript

    {
        "device-type" : {
                "number" : <number of devices>,
                "nameprefix" : <nameprefix>,
                "numberformat" : <format>,
                "frequency"  : <Hz>,
                "transmission" : {
                        "type" : "bulk|continuous",
                        "bulkTimeUnit" : "time in bulk".
                }
                "tranmissionFrequency" : <frequency>,
                "fields" : {
                    <fieldName> : <datetime,int,float,str>
                }
        }

    }


