Beaker hostRequires feature
===========================

mrack's Beaker hostRequires feature enables the specification of machine requirements in BeakerHub.
The Beaker transformer performs the translation of basic specifications from the input YAML's `domains` section.
It also handles more advanced specifications, including hardware requirements, by utilizing the `beaker` key in the host requirement section.
These values are later translated to XML accordingly.

This guide provides a demonstration of how requirements are translated and highlights the currently supported options.

Here is an example of Beaker provisioning using the hostRequires feature:

.. code:: yaml

    domains:
    - hosts:
      #########
      # Provisioning c9s
      #########
      - group: client
        name: bkr-c9s-latest.eagle.test
        os: c9s
        provider: beaker
        beaker:  # use some beaker specific requirements
          hostRequires:
            and:
              - cpu_count:
                  _value: 1
                  _op: "="
      name: eagle.test
      type: linux


This requirement is then translated to XML for the Beaker job, along with other specifics:

.. code:: xml

    <distroRequires>
      <and>
        <distro_name op="like" value="CentOS-Stream-9%"/>
        <distro_variant op="=" value="BaseOS"/>  // from provisioning config
        <distro_arch op="=" value="x86_64"/>  // default
        <distro_tag op="=" value="RC-0.1"/>  // from provisioning config
      </and>
    </distroRequires>
    <hostRequires>  // translated `hostRequires` key
      <and>  // translated `and` key
        <cpu_count value="1" op="="/>  // translated `cpu_count`, `_value` and `_op` keys
      </and>
      <system_type value="Machine"/>
    </hostRequires>

It is also possible to require RAM amount using `memory` key:

.. code:: yaml

    domains:
    - hosts:
      #########
      # Provisioning rhel-9.2
      #########
      - group: ipaserver
        name: bkr-rhel-9-2.eagle.test
        os: rhel-9.2
        provider: beaker
        beaker:  # use some beaker specific requirements
          hostRequires:
            and:
              - system:
                  memory:
                    _value: 4096
                    _op: "="
      name: eagle.test
      type: ipa

Which results into:

.. code:: xml

    <distroRequires>
      <and>
        <distro_name op="like" value="RHEL-9.2%"/>
        <distro_variant op="=" value="BaseOS"/>  // from provisioning config
        <distro_arch op="=" value="x86_64"/>  // default
        <distro_tag op="=" value="RC-0.1"/>  // from provisioning config
      </and>
    </distroRequires>
    <hostRequires>  // translated `hostRequires` key
      <and>  // translated `and` key
        <memory value="4096" op="="/>  // translated `memory`, `_value` and `_op` keys
      </and>
      <system_type value="Machine"/>
    </hostRequires>


Nowadays it is hard to find a machine with exactly one core thus we can use less strict requirement in hostRequires:

.. code:: yaml

    domains:
    - hosts:
      #########
      # Provisioning rhel-8.8
      #########
      - group: ipaserver
        name: bkr-rhel-8-8.eagle.test
        os: rhel-8.8
        provider: beaker
        beaker:  # use some beaker specific requirements
          hostRequires:
            and:
              - system:
                  memory:
                    _value: 2048
                    _op: ">=" # if there is problem finding system with exactly this amount
              - cpu_count:
                  _value: 2
                  _op: ">=" # if there is problem finding system with exactly this amount
      name: eagle.test
      type: ipa


And the result would be following XML:

.. code:: xml

    <distroRequires>
      <and>
        <distro_name op="like" value="RHEL-8.8%"/>
        <distro_variant op="=" value="BaseOS"/>  // from provisioning config
        <distro_arch op="=" value="x86_64"/>  // default
        <distro_tag op="=" value="RC-0.1"/>  // from provisioning config
      </and>
    </distroRequires>
    <hostRequires>  // translated `hostRequires` key
      <and>  // translated `and` key
        <cpu_count value="2" op="&gt="/>  // translated `cpu_count`, `_value` and `_op` keys
        <memory value="2048" op="&gt="/>  // translated `memory`, `_value` and `_op` keys
      </and>
      <system_type value="Machine"/>
    </hostRequires>

Here is an example of Beaker provisioning using hostRequires without and/or:

.. code:: yaml

    domains:
    - hosts:
      #########
      # Provisioning c9s
      #########
      - group: client
        name: bkr-c9s-latest.eagle.test
        os: c9s
        provider: beaker
        beaker:  # use some beaker specific requirements
          hostRequires:
            cpu_count:
              _value: 1
              _op: "="
      name: eagle.test
      type: linux


This requirement is then translated to XML for the Beaker job, along with other specifics:

.. code:: xml

    <distroRequires>
      <and>
        <distro_name op="like" value="CentOS-Stream-9%"/>
        <distro_variant op="=" value="BaseOS"/>  // from provisioning config
        <distro_arch op="=" value="x86_64"/>  // default
        <distro_tag op="=" value="RC-0.1"/>  // from provisioning config
      </and>
    </distroRequires>
    <hostRequires>  // translated `hostRequires` key
      <cpu_count value="1" op="="/>  // translated `cpu_count`, `_value` and `_op` keys
      <system_type value="Machine"/>
    </hostRequires>
