"""
Dependency injection container and utilities.

This module provides a lightweight dependency injection system following
the Dependency Inversion Principle (DIP) of SOLID.
"""

from __future__ import annotations

import inspect
from collections.abc import Callable, Mapping
from typing import Any, TypeVar, Generic, get_type_hints, get_origin, get_args
from typing_extensions import ParamSpec

from ..exceptions import ValidationError, ConfigurationError

T = TypeVar('T')
P = ParamSpec('P')


class ServiceNotFoundError(ConfigurationError):
    """Raised when a requested service is not registered in the container."""
    pass


class CircularDependencyError(ConfigurationError):
    """Raised when a circular dependency is detected during resolution."""
    pass


class DIContainer:
    """
    Lightweight dependency injection container.
    
    Provides service registration, dependency resolution, and lifecycle management
    following the Dependency Inversion Principle. Supports constructor injection,
    singleton patterns, and factory functions.
    """
    
    def __init__(self) -> None:
        """Initialize the dependency injection container."""
        self._services: dict[type, Any] = {}
        self._singletons: dict[type, Any] = {}
        self._factories: dict[type, Callable[..., Any]] = {}
        self._resolving: set[type] = set()  # Track circular dependencies
    
    def register_singleton(self, service_type: type[T], instance: T) -> None:
        \"\"\"
        Register a singleton instance.
        
        Args:
            service_type: The type/interface this instance implements
            instance: The singleton instance
            
        Raises:
            ValidationError: If parameters are invalid
        \"\"\"
        if not inspect.isclass(service_type):\n            raise ValidationError(f\"Service type must be a class: {service_type}\")\n        \n        if not isinstance(instance, service_type):\n            raise ValidationError(\n                f\"Instance must be of type {service_type.__name__}\"\n            )\n        \n        self._singletons[service_type] = instance\n    \n    def register_transient(\n        self, \n        service_type: type[T], \n        implementation: type[T] | Callable[..., T]\n    ) -> None:\n        \"\"\"Register a transient service (new instance each time).\"\"\"\n        if not inspect.isclass(service_type):\n            raise ValidationError(f\"Service type must be a class: {service_type}\")\n        \n        if inspect.isclass(implementation):\n            if not issubclass(implementation, service_type):\n                raise ValidationError(\n                    f\"{implementation.__name__} must implement {service_type.__name__}\"\n                )\n            self._services[service_type] = implementation\n        elif callable(implementation):\n            self._factories[service_type] = implementation\n        else:\n            raise ValidationError(\"Implementation must be a class or callable\")\n    \n    def register_factory(\n        self, \n        service_type: type[T], \n        factory: Callable[..., T]\n    ) -> None:\n        \"\"\"Register a factory function for creating instances.\"\"\"\n        if not inspect.isclass(service_type):\n            raise ValidationError(f\"Service type must be a class: {service_type}\")\n        \n        if not callable(factory):\n            raise ValidationError(\"Factory must be callable\")\n        \n        self._factories[service_type] = factory\n    \n    def get(self, service_type: type[T]) -> T:\n        \"\"\"Get an instance of the requested service type.\"\"\"\n        return self.resolve(service_type)\n    \n    def resolve(self, service_type: type[T]) -> T:\n        \"\"\"Resolve a service and its dependencies.\"\"\"\n        # Check for circular dependencies\n        if service_type in self._resolving:\n            dependency_chain = \" -> \".join(cls.__name__ for cls in self._resolving)\n            raise CircularDependencyError(\n                f\"Circular dependency detected: {dependency_chain} -> {service_type.__name__}\"\n            )\n        \n        # Check singletons first\n        if service_type in self._singletons:\n            return self._singletons[service_type]\n        \n        # Check factories\n        if service_type in self._factories:\n            factory = self._factories[service_type]\n            return self._create_with_dependencies(factory)\n        \n        # Check registered services\n        if service_type in self._services:\n            implementation = self._services[service_type]\n            return self._create_instance(implementation)\n        \n        # Try to create directly if it's a concrete class\n        if inspect.isclass(service_type) and not inspect.isabstract(service_type):\n            return self._create_instance(service_type)\n        \n        raise ServiceNotFoundError(\n            f\"Service not registered: {service_type.__name__}\",\n            {\"service_type\": service_type.__name__}\n        )\n    \n    def _create_instance(self, cls: type[T]) -> T:\n        \"\"\"Create an instance with dependency injection.\"\"\"\n        self._resolving.add(cls)\n        try:\n            # Get constructor parameters\n            constructor = cls.__init__\n            type_hints = get_type_hints(constructor)\n            sig = inspect.signature(constructor)\n            \n            # Prepare constructor arguments\n            kwargs = {}\n            for param_name, param in sig.parameters.items():\n                if param_name == 'self':\n                    continue\n                \n                param_type = type_hints.get(param_name)\n                if param_type is None:\n                    if param.default is not inspect.Parameter.empty:\n                        continue  # Use default value\n                    raise ValidationError(\n                        f\"No type hint for parameter '{param_name}' in {cls.__name__}\"\n                    )\n                \n                # Handle Optional types\n                origin = get_origin(param_type)\n                if origin is not None:\n                    args = get_args(param_type)\n                    if len(args) == 2 and type(None) in args:\n                        # This is Optional[T] or Union[T, None]\n                        actual_type = args[0] if args[1] is type(None) else args[1]\n                        try:\n                            kwargs[param_name] = self.resolve(actual_type)\n                        except ServiceNotFoundError:\n                            if param.default is not inspect.Parameter.empty:\n                                continue  # Use default value\n                            kwargs[param_name] = None\n                        continue\n                \n                # Resolve dependency\n                try:\n                    kwargs[param_name] = self.resolve(param_type)\n                except ServiceNotFoundError:\n                    if param.default is not inspect.Parameter.empty:\n                        continue  # Use default value\n                    raise\n            \n            return cls(**kwargs)\n        finally:\n            self._resolving.discard(cls)\n    \n    def _create_with_dependencies(self, factory: Callable[..., T]) -> T:\n        \"\"\"Create instance using factory with dependency injection.\"\"\"\n        # Get factory parameters\n        type_hints = get_type_hints(factory)\n        sig = inspect.signature(factory)\n        \n        # Prepare factory arguments\n        kwargs = {}\n        for param_name, param in sig.parameters.items():\n            param_type = type_hints.get(param_name)\n            if param_type is None:\n                if param.default is not inspect.Parameter.empty:\n                    continue  # Use default value\n                raise ValidationError(\n                    f\"No type hint for parameter '{param_name}' in factory\"\n                )\n            \n            # Resolve dependency\n            try:\n                kwargs[param_name] = self.resolve(param_type)\n            except ServiceNotFoundError:\n                if param.default is not inspect.Parameter.empty:\n                    continue  # Use default value\n                raise\n        \n        return factory(**kwargs)\n    \n    def clear(self) -> None:\n        \"\"\"Clear all registered services and singletons.\"\"\"\n        self._services.clear()\n        self._singletons.clear()\n        self._factories.clear()\n        self._resolving.clear()\n    \n    def is_registered(self, service_type: type) -> bool:\n        \"\"\"Check if a service type is registered.\"\"\"\n        return (\n            service_type in self._services or\n            service_type in self._singletons or\n            service_type in self._factories\n        )\n    \n    def get_registered_services(self) -> list[type]:\n        \"\"\"Get list of all registered service types.\"\"\"\n        return list(set(\n            list(self._services.keys()) +\n            list(self._singletons.keys()) +\n            list(self._factories.keys())\n        ))\n\n\nclass ServiceRegistry:\n    \"\"\"Service registry for managing application-wide dependencies.\"\"\"\n    \n    _container: DIContainer | None = None\n    \n    @classmethod\n    def get_container(cls) -> DIContainer:\n        \"\"\"Get the global DI container instance.\"\"\"\n        if cls._container is None:\n            cls._container = DIContainer()\n        return cls._container\n    \n    @classmethod\n    def reset(cls) -> None:\n        \"\"\"Reset the global container (useful for testing).\"\"\"\n        if cls._container is not None:\n            cls._container.clear()\n        cls._container = None\n    \n    @classmethod\n    def configure(cls, configurator: Callable[[DIContainer], None]) -> None:\n        \"\"\"Configure services using a configuration function.\"\"\"\n        container = cls.get_container()\n        configurator(container)\n\n\ndef inject(service_type: type[T]) -> T:\n    \"\"\"Convenience function to inject a service dependency.\"\"\"\n    return ServiceRegistry.get_container().get(service_type)\n\n\ndef injectable(cls: type[T]) -> type[T]:\n    \"\"\"Class decorator to mark a class as injectable.\"\"\"\n    # This is mainly for documentation purposes in Python\n    # The actual injection happens in the container\n    return cls"