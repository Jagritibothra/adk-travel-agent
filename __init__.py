"""Dynamic agent package initializer.

This `__init__` selects which submodule's `root_agent` to expose based on the
`ADK_AGENT_MODULE` environment variable. It falls back to `agent` (agent.py).

Set ADK_AGENT_MODULE to the module filename (without .py) you want to run.
For example:
  $env:ADK_AGENT_MODULE='agent'
  adk run agent_tool

This keeps a single package entrypoint while allowing multiple agent files.
"""
import importlib
import importlib.util
import sys
import os
from types import ModuleType

_default = "agent"
_raw_module = os.environ.get("ADK_AGENT_MODULE", _default)

# Normalize module name: allow paths like 'app/agents/conversationAgent' or
# 'app.agents.conversationAgent' or 'app/agents/conversationAgent.py'
def _normalize_module_name(name: str) -> str:
	if not name:
		return _default
	n = name.strip()
	# remove .py suffix if present
	if n.endswith('.py'):
		n = n[:-3]
	# convert Windows/Unix separators to dots
	n = n.replace('\\', '/').strip('/')
	n = n.replace('/', '.')
	return n or _default

_module_name = _normalize_module_name(_raw_module)

def _import_selected_module(pkg: str, module_name: str) -> ModuleType:
	# Robust import helper:
	# 1. Try absolute import of the normalized module name.
	# 2. If that fails, attempt to locate a .py file under the package directory and import by file path.
	# 3. As a last resort, try a package-relative import if the package name is usable.
	name = (module_name or '').lstrip('.')

	# Create a safe package name (module names cannot contain '-') and
	# ensure we import/load submodules under that namespace. This lets
	# package-internal relative imports (e.g. "from ..prompts import ...")
	# resolve correctly even when the containing folder name contains a
	# hyphen on disk.
	safe_pkg = (pkg or '').replace('-', '_') or None

	# Try absolute import first (use safe_pkg prefix when available)
	try:
		if safe_pkg:
			return importlib.import_module(f"{safe_pkg}.{name}")
		return importlib.import_module(name)
	except Exception:
		pass

	# Try locating the module under this package's filesystem (supports 'app.agents.foo' or 'app/agents/foo')
	base_dir = os.path.dirname(__file__)
	rel_path = name.replace('.', os.sep).replace('/', os.sep)
	candidates = [
		os.path.join(base_dir, rel_path + '.py'),
		os.path.join(base_dir, rel_path, '__init__.py'),
		os.path.join(base_dir, 'app', rel_path + '.py'),
		os.path.join(base_dir, 'app', rel_path, '__init__.py'),
		os.path.join(base_dir, 'app', 'agents', rel_path + '.py'),
		os.path.join(base_dir, 'app', 'agents', rel_path, '__init__.py'),
	]
	for full in candidates:
		if os.path.exists(full):
			# Use the safe package namespace as the module's name so that
			# internal relative imports resolve against it.
			fq_name = (f"{safe_pkg}.{name}" if safe_pkg else name).replace(os.sep, '.')
			spec = importlib.util.spec_from_file_location(fq_name, full)
			if spec and spec.loader:
				# Ensure the top-level safe package exists in sys.modules and
				# points to this package directory so import machinery can
				# find subpackages like 'app' under it.
				base_dir = os.path.dirname(__file__)
				if safe_pkg and safe_pkg not in sys.modules:
					pkg_mod = ModuleType(safe_pkg)
					pkg_mod.__path__ = [base_dir]
					pkg_mod.__package__ = safe_pkg
					sys.modules[safe_pkg] = pkg_mod

				mod = importlib.util.module_from_spec(spec)
				# Register module in sys.modules under fq_name to support
				# further imports that may reference it.
				sys.modules[fq_name] = mod
				spec.loader.exec_module(mod)
				return mod

	# Final attempt: package-relative import (only if pkg is a valid package name)
	try:
		# Package-relative import using safe package namespace
		if safe_pkg:
			return importlib.import_module(f".{name}", package=safe_pkg)
		return importlib.import_module(f".{name}", package=pkg)
	except Exception as e:
		raise ImportError(f"Fail to load '{pkg}' module. {e}") from e

_mod = _import_selected_module(__package__ or "adk-travel-agent", _module_name)

# Expose root_agent for ADK loader
if hasattr(_mod, "root_agent"):
	root_agent = getattr(_mod, "root_agent")
else:
	# Provide a clearer error when ADK imports the package and root_agent is missing
	raise ImportError(
		f"Selected module '{_module_name}' does not define 'root_agent'."
	)

# Also expose the selected module for debugging
selected_module = _mod
