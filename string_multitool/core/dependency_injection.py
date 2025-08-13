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
        """
        Register a singleton instance.
        
        Args:
            service_type: The type/interface this instance implements
            instance: The singleton instance
            
        Raises:
            ValidationError: If parameters are invalid
        """
        if not inspect.isclass(service_type):
            raise ValidationError(f"Service type must be a class: {service_type}")
        
        if not isinstance(instance, service_type):
            raise ValidationError(
                f"Instance must be of type {service_type.__name__}"
            )
        
        self._singletons[service_type] = instance
    
    def register_transient(
        self, 
        service_type: type[T], 
        implementation: type[T] | Callable[..., T]
    ) -> None:
        """Register a transient service (new instance each time)."""
        if not inspect.isclass(service_type):
            raise ValidationError(f"Service type must be a class: {service_type}")
        
        if inspect.isclass(implementation):
            if not issubclass(implementation, service_type):
                raise ValidationError(
                    f"{implementation.__name__} must implement {service_type.__name__}"
                )
            self._services[service_type] = implementation
        elif callable(implementation):
            self._factories[service_type] = implementation
        else:
            raise ValidationError("Implementation must be a class or callable")
    
    def register_factory(
        self, 
        service_type: type[T], 
        factory: Callable[..., T]
    ) -> None:
        """Register a factory function for creating instances."""
        if not inspect.isclass(service_type):
            raise ValidationError(f"Service type must be a class: {service_type}")
        
        if not callable(factory):
            raise ValidationError("Factory must be callable")
        
        self._factories[service_type] = factory
    
    def get(self, service_type: type[T]) -> T:
        """Get an instance of the requested service type."""
        return self.resolve(service_type)
    
    def resolve(self, service_type: type[T]) -> T:
        """Resolve a service and its dependencies."""
        # Check for circular dependencies
        if service_type in self._resolving:
            dependency_chain = " -> ".join(cls.__name__ for cls in self._resolving)
            raise CircularDependencyError(
                f"Circular dependency detected: {dependency_chain} -> {service_type.__name__}"
            )
        
        # Check singletons first
        if service_type in self._singletons:
            return self._singletons[service_type]
        
        # Check factories
        if service_type in self._factories:
            factory = self._factories[service_type]
            return self._create_with_dependencies(factory)
        
        # Check registered services
        if service_type in self._services:
            implementation = self._services[service_type]
            return self._create_instance(implementation)
        
        # Try to create directly if it's a concrete class
        if inspect.isclass(service_type) and not inspect.isabstract(service_type):
            return self._create_instance(service_type)
        
        raise ServiceNotFoundError(
            f"Service not registered: {service_type.__name__}",
            {"service_type": service_type.__name__}
        )
    
    def _create_instance(self, cls: type[T]) -> T:
        """Create an instance with dependency injection."""
        self._resolving.add(cls)
        try:
            # Get constructor parameters
            constructor = cls.__init__
            type_hints = get_type_hints(constructor)
            sig = inspect.signature(constructor)
            
            # Prepare constructor arguments
            kwargs = {}
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                
                param_type = type_hints.get(param_name)
                if param_type is None:
                    if param.default is not inspect.Parameter.empty:
                        continue  # Use default value
                    raise ValidationError(
                        f"No type hint for parameter '{param_name}' in {cls.__name__}"
                    )
                
                # Handle Optional types
                origin = get_origin(param_type)
                if origin is not None:
                    args = get_args(param_type)
                    if len(args) == 2 and type(None) in args:
                        # This is Optional[T] or Union[T, None]
                        actual_type = args[0] if args[1] is type(None) else args[1]
                        try:
                            kwargs[param_name] = self.resolve(actual_type)
                        except ServiceNotFoundError:
                            if param.default is not inspect.Parameter.empty:
                                continue  # Use default value
                            kwargs[param_name] = None
                        continue
                
                # Resolve dependency
                try:
                    kwargs[param_name] = self.resolve(param_type)
                except ServiceNotFoundError:
                    if param.default is not inspect.Parameter.empty:
                        continue  # Use default value
                    raise
            
            return cls(**kwargs)
        finally:
            self._resolving.discard(cls)
    
    def _create_with_dependencies(self, factory: Callable[..., T]) -> T:
        """Create instance using factory with dependency injection."""
        # Get factory parameters
        type_hints = get_type_hints(factory)
        sig = inspect.signature(factory)
        
        # Prepare factory arguments
        kwargs = {}
        for param_name, param in sig.parameters.items():
            param_type = type_hints.get(param_name)
            if param_type is None:
                if param.default is not inspect.Parameter.empty:
                    continue  # Use default value
                raise ValidationError(
                    f"No type hint for parameter '{param_name}' in factory"
                )
            
            # Resolve dependency
            try:
                kwargs[param_name] = self.resolve(param_type)
            except ServiceNotFoundError:
                if param.default is not inspect.Parameter.empty:
                    continue  # Use default value
                raise
        
        return factory(**kwargs)
    
    def clear(self) -> None:
        """Clear all registered services and singletons."""
        self._services.clear()
        self._singletons.clear()
        self._factories.clear()
        self._resolving.clear()
    
    def is_registered(self, service_type: type) -> bool:
        """Check if a service type is registered."""
        return (
            service_type in self._services or
            service_type in self._singletons or
            service_type in self._factories
        )
    
    def get_registered_services(self) -> list[type]:
        """Get list of all registered service types."""
        return list(set(
            list(self._services.keys()) +
            list(self._singletons.keys()) +
            list(self._factories.keys())
        ))


class ServiceRegistry:
    """Service registry for managing application-wide dependencies."""
    
    _container: DIContainer | None = None
    
    @classmethod
    def get_container(cls) -> DIContainer:
        """Get the global DI container instance."""
        if cls._container is None:
            cls._container = DIContainer()
        return cls._container
    
    @classmethod
    def reset(cls) -> None:
        """Reset the global container (useful for testing)."""
        if cls._container is not None:
            cls._container.clear()
        cls._container = None
    
    @classmethod
    def configure(cls, configurator: Callable[[DIContainer], None]) -> None:
        """Configure services using a configuration function."""
        container = cls.get_container()
        configurator(container)


def inject(service_type: type[T]) -> T:
    """Convenience function to inject a service dependency."""
    return ServiceRegistry.get_container().get(service_type)


def injectable(cls: type[T]) -> type[T]:
    """Class decorator to mark a class as injectable."""
    # This is mainly for documentation purposes in Python
    # The actual injection happens in the container
    return cls