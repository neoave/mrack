How to configure provider's provisioning strategy
=================================================

mrack supports several providers and each provider can be configured to retry
the provisioning of resource when needed.
By default mrack's strategy is to abort the process of providing resources and fail.

This short guide explains how we can configure each provider to retry provisioning on any failure.
After reaching `max_retry` count mrack will fail as it could not provide required VMs in desired attempts count.

Provisioning config enablement:

.. code:: yaml

    aws|beaker|openstack|pomdan|virt:
        # feature to switch provisioning strategy from abort or retry on fail
        strategy: retry # use either `abort` or `retry`
        # maximum count of the retries when re-provisioning resources
        # fails if retry does not provide resource after max_retry count
        max_retry: 3
        ...
