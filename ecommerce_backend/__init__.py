"""
Shim package to support imports like `ecommerce_backend.*` in tests.
It maps to the actual code located under the `ecommerce-backend/` directory.
"""

import os
import sys
import importlib
import types

# Compute path to the real backend folder (with hyphen)
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_REAL_BACKEND_DIR = os.path.join(_ROOT, "ecommerce-backend")

if os.path.isdir(_REAL_BACKEND_DIR) and _REAL_BACKEND_DIR not in sys.path:
    sys.path.insert(0, _REAL_BACKEND_DIR)

# Preload and alias common submodules
_SUBMODULES = [
    "api",
    "api_unified",
    "api_sqlite",
    "api_postgres",
    "database",
    "enums",
    "services",
    "services.auth_service",
    "utils",
]

for _name in _SUBMODULES:
    try:
        _mod = importlib.import_module(_name)
        sys.modules[f"ecommerce_backend.{_name}"] = _mod
        # Exposer aussi comme attribut du package pour les accès par getattr
        pkg = sys.modules[__name__]
        # Créer les sous-packages intermédiaires si nécessaire (ex: services)
        parts = _name.split('.')
        parent = pkg
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                setattr(parent, part, _mod)
            else:
                subpkg_name = '.'.join(parts[:i+1])
                full_key = f"ecommerce_backend.{subpkg_name}"
                subpkg = sys.modules.get(full_key)
                if subpkg is None:
                    # Créer un module conteneur simple
                    subpkg = types.ModuleType(full_key)
                    sys.modules[full_key] = subpkg
                    setattr(parent, part, subpkg)
                parent = subpkg
    except Exception:
        # Best effort; some modules may not exist in this repo variant
        pass

# Créer un shim explicite pour ecommerce_backend.api_unified si absent
if 'ecommerce_backend.api_unified' not in sys.modules:
    try:
        api_mod = importlib.import_module('api')
        repos = importlib.import_module('database.repositories_simple')
        shim = types.ModuleType('ecommerce_backend.api_unified')
        # Exporter les symboles attendus par les tests
        for attr in ('current_user', 'require_admin'):
            if hasattr(api_mod, attr):
                setattr(shim, attr, getattr(api_mod, attr))
        for attr in (
            'PostgreSQLProductRepository',
            'PostgreSQLCartRepository',
            'PostgreSQLOrderRepository',
        ):
            if hasattr(repos, attr):
                setattr(shim, attr, getattr(repos, attr))
        # Enregistrer le shim
        sys.modules['ecommerce_backend.api_unified'] = shim
        # L'attacher comme attribut du package
        setattr(sys.modules[__name__], 'api_unified', shim)
    except Exception:
        pass
