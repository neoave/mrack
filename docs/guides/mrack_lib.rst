How to use mrack as library
===========================

mrack can be used as python library in automation and may provide fast provisioning
of resources when needed.

This short guide demonstrate how we can use mrack in python automation.

First we should set up authentication for each provider in this example we will use aws.key file for boto3 library.
.. code-block::

    $ export AWS_CONFIG_FILE=`readlink -f /path/to/aws.key`

We start to include all providers from mrack which we would like to use.
.. code-block::

    from mrack.providers import providers
    from mrack.providers.aws import PROVISIONER_KEY as AWS
    from mrack.providers.aws import AWSProvider
    from mrack.providers.beaker import PROVISIONER_KEY as BEAKER
    from mrack.providers.beaker import BeakerProvider
    from mrack.providers.openstack import PROVISIONER_KEY as OPENSTACK
    from mrack.providers.openstack import OpenStackProvider
    from mrack.providers.podman import PROVISIONER_KEY as PODMAN
    from mrack.providers.podman import PodmanProvider
    from mrack.providers.static import PROVISIONER_KEY as STATIC
    from mrack.providers.static import StaticProvider
    from mrack.providers.virt import PROVISIONER_KEY as VIRT
    from mrack.providers.virt import VirtProvider

Then register all supported providers:
.. code-block::

    providers.register(AWS, AWSProvider)
    providers.register(OPENSTACK, OpenStackProvider)
    providers.register(BEAKER, BeakerProvider)
    providers.register(PODMAN, PodmanProvider)
    providers.register(STATIC, StaticProvider)
    providers.register(VIRT, VirtProvider)

Then register all supported providers:
.. code-block::

    import mrack
    global_context = mrack.context.global_context

After that we init global context with paths to files:
.. code-block::

    mrack_config = "mrack.conf"
    provisioning_config = "provisioning-config.yaml"
    db_file = "mrackdb.json"
    global_context.init(mrack_config, provisioning_config, db_file)

    # load the metadata to global_context
    metadata = "./metadata-f34.yaml"
    global_context.init_metadata(metadata)

We pick default provider:
.. code-block::

    provider = "aws"


Create Up action and provision machines:
.. code-block::

    from mrack.actions.up import Up

    up_action = Up()
    await up_action.init(provider)

    # provision machines:
    await up_action.provision()


Create output action which handles DB saving:
.. code-block::

    # store the output to db or just use the db later on
    from mrack.actions.output import Output
    output_action = Output()
    await output_action.generate_outputs()

After successfully using our resources we cleanup machines by creating destroy action:
.. code-block::

    # cleanup the machines:
    from mrack.actions.destroy import Destroy
    destroy_action = Destroy()
    await destroy_action.destroy()
