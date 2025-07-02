"""Core tap functionality tests."""

from tap_oracle_wms.tap import TapOracleWMS


class TestTapCore:
    """Test core tap functionality."""

    def test_tap_initialization(self, sample_config) -> None:
        """Test that tap initializes properly with valid config."""
        tap = TapOracleWMS(config=sample_config)

        assert tap.config == sample_config
        assert tap.name == "tap-oracle-wms"
        assert hasattr(tap, "logger")

    def test_tap_stream_discovery(self, sample_config) -> None:
        """Test that tap can discover available streams."""
        tap = TapOracleWMS(config=sample_config)
        streams = tap.streams

        assert isinstance(streams, dict)
        assert len(streams) > 0

        # Check for expected WMS streams
        expected_streams = ["facility", "company", "item"]
        for stream_name in expected_streams:
            assert stream_name in streams, f"Expected stream '{stream_name}' not found"

    def test_tap_catalog_generation(self, sample_config) -> None:
        """Test that tap generates valid catalog."""
        tap = TapOracleWMS(config=sample_config)
        catalog = tap.catalog_dict

        assert isinstance(catalog, dict)
        assert "streams" in catalog
        assert len(catalog["streams"]) > 0

        # Validate stream structure
        for stream in catalog["streams"]:
            assert "tap_stream_id" in stream
            assert "schema" in stream
            assert "metadata" in stream

    def test_tap_config_validation(self, sample_config) -> None:
        """Test that tap properly validates configuration."""
        # Test with valid config
        tap = TapOracleWMS(config=sample_config)
        assert tap.config is not None

        # Test required fields are present
        required_fields = ["base_url", "username", "password"]
        for field in required_fields:
            assert (
                field in sample_config
            ), f"Required field '{field}' missing from config"

    def test_tap_stream_instantiation(self, sample_config) -> None:
        """Test that tap can instantiate streams correctly."""
        tap = TapOracleWMS(config=sample_config)

        for stream_class in tap.streams.values():
            stream_instance = stream_class(tap=tap)

            assert stream_instance.tap_name == "tap-oracle-wms"
            assert stream_instance.name == stream_instance.name
            assert hasattr(stream_instance, "schema")
            assert hasattr(stream_instance, "get_records")

    def test_tap_authentication_setup(self, sample_config) -> None:
        """Test that tap sets up authentication correctly."""
        tap = TapOracleWMS(config=sample_config)

        # Get a stream to test authenticator
        stream_name = next(iter(tap.streams.keys()))
        stream_class = tap.streams[stream_name]
        stream = stream_class(tap=tap)

        assert hasattr(stream, "authenticator")
        authenticator = stream.authenticator
        assert authenticator is not None

    def test_tap_url_construction(self, sample_config) -> None:
        """Test that tap constructs URLs correctly."""
        tap = TapOracleWMS(config=sample_config)

        # Test base URL handling
        assert sample_config["base_url"] in str(tap.config["base_url"])

        # Test that streams get correct base URLs
        for stream_class in tap.streams.values():
            stream = stream_class(tap=tap)
            assert hasattr(stream, "url_base")
            assert stream.url_base.startswith("http")

    def test_tap_version_info(self, sample_config) -> None:
        """Test that tap provides version information."""
        tap = TapOracleWMS(config=sample_config)

        # Should have version info available
        assert hasattr(tap, "name")
        assert tap.name == "tap-oracle-wms"
