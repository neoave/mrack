import pytest
import yaml

from mrack.outputs.pytest_mh import PytestMhOutput

from .mock_data import get_db_from_metadata, provisioning_config


@pytest.fixture
def mock_metadata():
    return yaml.safe_load(
        """
    domains:
    - name: test
      hosts:
      - name: dns.test
        group: medium
        os: fedora-37
      - name: client.test
        group: medium
        groups:
        - base_ground
        - base_client
        - client
        role: client
        os: fedora-37
        pytest_mh:
          artifacts:
          - /etc/sssd/*
          - /var/log/sssd/*
          - /var/lib/sss/db/*
      - name: master.ipa.test
        group: ipa
        groups:
        - base_ground
        - base_ldap
        - base_ipa
        - ipa
        role: ipa
        os: fedora-37
        pytest_mh:
          ssh:
            username: tuser
            password: tuserpassword
          config:
            client:
              ipa_domain: ipa.test
              krb5_keytab: /enrollment/ipa.keytab
              ldap_krb5_keytab: /enrollment/ipa.keytab
      - name: dc.ad.test
        group: ad
        role: ad
        os: windows-2016
    """
    )


class TestPytestMhOutput:
    def test_output(self, mock_metadata):
        config = provisioning_config()
        db = get_db_from_metadata(mock_metadata)

        # Set username and password in the host object of Windows host,
        # this should be reflected in the resulting configuration.
        db.hosts["dc.ad.test"]._username = "Administrator"
        db.hosts["dc.ad.test"]._password = "adpassword"

        mhcfg_output = PytestMhOutput(config, db, mock_metadata)
        mhcfg = mhcfg_output.create_mh_config()

        expected = yaml.safe_load(
            """
        domains:
        - id: test
          hosts:
          - hostname: client.test
            os:
              family: linux
            role: client
            ssh:
              host: 192.168.0.1
            artifacts:
            - /etc/sssd/*
            - /var/log/sssd/*
            - /var/lib/sss/db/*
          - hostname: master.ipa.test
            os:
              family: linux
            role: ipa
            ssh:
              host: 192.168.0.1
              username: tuser
              password: tuserpassword
            config:
              client:
                ipa_domain: ipa.test
                krb5_keytab: /enrollment/ipa.keytab
                ldap_krb5_keytab: /enrollment/ipa.keytab
          - hostname: dc.ad.test
            os:
              family: windows
            role: ad
            ssh:
              host: 192.168.0.1
              username: Administrator
              password: adpassword
        """
        )

        print(mhcfg)

        assert mhcfg == expected
