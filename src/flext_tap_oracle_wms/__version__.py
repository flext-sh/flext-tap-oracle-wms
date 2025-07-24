"""Version information for flext-tap-oracle-wms."""
# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

# Import from centralized version management system
try:
    # 🚨 ARCHITECTURAL COMPLIANCE: Using DI container
from flext_tap_oracle_wms.infrastructure.di_container import get_service_result, get_domain_entity, get_field, get_domain_value_object, get_base_config
ServiceResult = get_service_result()
DomainEntity = get_domain_entity()
Field = get_field()
DomainValueObject = get_domain_value_object()
BaseConfig = get_base_config()
__version__ = get_version()  # No arguments needed
__version_info__ = get_version_info()  # No arguments needed
except (ImportError, TypeError):
    # Fallback for when flext_core version helpers don't exist or have
    # different signatures
    __version__ = "0.7.0"
    __version_info__ = (0, 7, 0)

# FLEXT Enterprise - Unified Versioning System
# Version is managed centrally in flext_core.version
# This maintains backward compatibility while eliminating duplication.
