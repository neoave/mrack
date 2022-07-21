from mrack.outputs.pytest_multihost import PytestMultihostOutput

from .mock_data import get_db_from_metadata, metadata_extra, provisioning_config


class TestPytestMultihostOutput:
    def test_arbitrary_attrs(self):
        """
        Test that values defined in `pytest_multihost` dictionary in host part
        of job metadata file gets into host attributes in generated pytest-multihost
        output.
        """
        metadata = metadata_extra()
        m_srv1 = metadata["domains"][0]["hosts"][0]
        m_srv2 = metadata["domains"][0]["hosts"][1]
        m_srv1["pytest_multihost"] = {
            "readonly_dc": "yes",
            "something_else": "for_fun",
        }
        m_srv2["pytest_multihost"] = {
            "no_ca": "yes",
            "something_else": "for_fun",
        }

        config = provisioning_config()
        db = get_db_from_metadata(metadata)
        mhcfg_output = PytestMultihostOutput(config, db, metadata)
        mhcfg = mhcfg_output.create_multihost_config()

        srv1 = mhcfg["domains"][0]["hosts"][0]

        assert "readonly_dc" in srv1
        assert srv1["readonly_dc"] == "yes"
        assert "something_else" in srv1
        assert srv1["something_else"] == "for_fun"

        srv2 = mhcfg["domains"][0]["hosts"][1]
        assert "no_ca" in srv2
        assert "something_else" in srv2
        assert srv2["no_ca"] == "yes"
        assert srv2["something_else"] == "for_fun"
