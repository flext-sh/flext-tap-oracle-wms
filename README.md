# FLEXT-Tap-Oracle-WMS

[![Singer SDK](https://img.shields.io/badge/singer--sdk-compliant-brightgreen.svg)](https://sdk.meltano.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**FLEXT-Tap-Oracle-WMS** is a Singer-compliant tap for extracting data from Oracle Warehouse Management Systems. It integrates seamlessly with Meltano and the FLEXT ecosystem to provide reliable streams for inventory, orders, and operational metrics.

Part of the [FLEXT](https://github.com/flext-sh/flext) ecosystem.

## 🚀 Key Features

- **Comprehensive Coverage**: 10 functional streams including Inventory, Allocation, Orders, Shipments, Locations, and Items.
- **Incremental Sync**: State management with replication keys to ensure efficient data updates.
- **Authentication**: Supports both Basic Auth and OAuth2 for secure API access.
- **Catalog Discovery**: Automated schema inference for all supported WMS entities.
- **Built on FLEXT**: Leverages `flext-core` and `flext-oracle-wms` for robust API interaction and error handling.

## 📦 Installation

To usage in your Meltano project, add the extractor to your `meltano.yml`:

```yaml
plugins:
  extractors:
    - name: tap-oracle-wms
      namespace: tap_oracle_wms
      pip_url: flext-tap-oracle-wms
      config:
        base_url: ${WMS_BASE_URL}
        username: ${WMS_USERNAME}
        password: ${WMS_PASSWORD}
```

Or install via Poetry:

```bash
poetry add flext-tap-oracle-wms
```

## 🛠️ Usage

### Service Configuration

Configure the tap using environment variables or a `config.json` file:

```json
{
  "base_url": "https://wms.oraclecloud.com",
  "username": "api_user",
  "password": "secure_password",
  "auth_method": "basic",
  "start_date": "2024-01-01T00:00:00Z"
}
```

### Discovery Mode

Generate a catalog of available streams:

```bash
tap-oracle-wms --config config.json --discover > catalog.json
```

### Syncing Data

Run the tap to extract data, piping output to a Singer target:

```bash
tap-oracle-wms --config config.json --catalog catalog.json | target-jsonl
```

## 🏗️ Architecture

This project strictly adheres to Singer Protocol standards:

- **Streams**: Encapsulate logic for specific API endpoints (e.g., `/items`, `/orders`).
- **Authentication**: Strategy pattern implementation for interchangeable auth methods.
- **Validation**: Pydantic models ensure config integrity before execution.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/development.md) for details on adding new streams and running the test suite.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
