

Post provisioning ssh check configuration
=========================================


The feature which made post provisioning ssh check configurable is using
the `post_provisioning_check` section from `provisioning-config.yaml`.
An example is shown down below with the inline comments:

.. code:: yaml

    post_provisioning_check:
        ssh:
            # Default configurations for every host
            enabled: True # True | False
            disabled_providers: ["podman"] # Per provider override to `enabled: True`
            enabled_providers: [] # Would be relevant if 'enabled' is 'False'
            # port: 22
            # timeout: 10 # minutes

            # Overrides
            # Priority:
            # OS > Group > Default

            group:
                ipaclient:
                    timeout: 309090 # minutes
            # If we want to override based on OS
            os:
                win-2012r2:
                    timeout: 15 # minutes
                win-2016:
                    timeout: 15 # minutes
                win-2019:
                    timeout: 15 # minutes
                fedora-34:
                    enabled: False
                    timeout: 1
                    enabled_providers: ["static"]
                    disabled_providers: ["beaker"]

Priority is set to: `OS > Group > Default` which implies that per `group` configuration
overrides the `default` config and `os` overrides both `default` and `group`.

When the `post_provisioning_check` section is not set mrack uses these defaults:

.. code:: yaml

    enabled: True
    enabled_providers: []
    disabled_providers: []
    port: 22
    timeout: 10
