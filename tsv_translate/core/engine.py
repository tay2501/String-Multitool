"""Main conversion engine orchestrating all components.

Clean facade pattern implementation providing a simple interface
to the complex subsystem with proper dependency management.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any, TYPE_CHECKING

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, Session
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    # SQLAlchemy is optional for basic functionality
    SQLALCHEMY_AVAILABLE = False
    if TYPE_CHECKING:
        from sqlalchemy.orm import Session  # type: ignore[import]
        from sqlalchemy import create_engine  # type: ignore[import]
        from sqlalchemy.orm import sessionmaker  # type: ignore[import]

from ..models import Base
from ..services import SyncService, ConversionService
from ..services.file_watcher import FileWatcher
from ..core.types import ConversionResult, SyncResult
from ..core.exceptions import TSVTranslateError


class TSVTranslateEngine:
    """Main engine coordinating all TSV conversion operations.
    
    Educational patterns:
    - Facade pattern for complex subsystem coordination
    - Dependency injection with proper lifecycle management
    - Resource management with context managers
    - Clean configuration management
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize engine with configuration.
        
        Args:
            config: Configuration dictionary with database and directory settings
        """
        self._config = config
        self._engine = None
        self._session_factory = None
        self._file_watcher: Optional[FileWatcher] = None
        self._is_initialized = False
    
    def initialize(self) -> None:
        """Initialize database and services.
        
        Separate from constructor to allow for proper error handling
        and resource management.
        """
        if self._is_initialized:
            return
            
        if not SQLALCHEMY_AVAILABLE:
            raise TSVTranslateError(
                "SQLAlchemy is required for database operations. Install with: pip install sqlalchemy"
            )
        
        try:
            # Database setup with SQLAlchemy 2.0 patterns
            database_url = self._config.get("database_url", "sqlite:///tsv_converter.db")
            self._engine = create_engine(
                database_url,
                echo=self._config.get("debug", False),
                future=True  # Use SQLAlchemy 2.0 behavior
            )
            
            # Create tables
            Base.metadata.create_all(self._engine)
            
            # Session factory for dependency injection
            self._session_factory = sessionmaker(
                bind=self._engine,
                expire_on_commit=False
            )
            
            # Setup file watcher if directory monitoring is enabled
            if self._config.get("enable_file_watching", True):
                self._setup_file_watcher()
            
            self._is_initialized = True
            
        except Exception as e:
            raise TSVTranslateError(f"Engine initialization failed: {e}")
    
    def convert_text(self, text: str, rule_set_name: str) -> ConversionResult:
        """Convert text using specified rule set.
        
        Main entry point for text conversion operations.
        """
        self._ensure_initialized()
        
        with self._create_session() as session:
            conversion_service = ConversionService(session)
            return conversion_service.convert_text(text, rule_set_name)
    
    def sync_file(self, file_path: Path) -> SyncResult:
        """Synchronize single TSV file with database."""
        self._ensure_initialized()
        
        with self._create_session() as session:
            sync_service = SyncService(session)
            return sync_service.sync_file(file_path)
    
    def sync_directory(self, directory_path: Path) -> List[SyncResult]:
        """Synchronize all TSV files in directory."""
        self._ensure_initialized()
        
        with self._create_session() as session:
            sync_service = SyncService(session)
            return sync_service.sync_directory(directory_path)
    
    def list_rule_sets(self) -> List[str]:
        """Get list of available rule set names."""
        self._ensure_initialized()
        
        with self._create_session() as session:
            conversion_service = ConversionService(session)
            return conversion_service.list_rule_sets()
    
    def get_rule_set_info(self, rule_set_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a rule set."""
        self._ensure_initialized()
        
        with self._create_session() as session:
            conversion_service = ConversionService(session)
            return conversion_service.get_rule_set_info(rule_set_name)
    
    def remove_rule_set(self, rule_set_name: str) -> SyncResult:
        """Remove rule set from database."""
        self._ensure_initialized()
        
        with self._create_session() as session:
            sync_service = SyncService(session)
            return sync_service.remove_rule_set(rule_set_name)
    
    def start_file_watching(self) -> None:
        """Start automatic file monitoring."""
        if self._file_watcher and not self._file_watcher.is_running:
            self._file_watcher.start()
    
    def stop_file_watching(self) -> None:
        """Stop automatic file monitoring."""
        if self._file_watcher and self._file_watcher.is_running:
            self._file_watcher.stop()
    
    def health_check(self) -> Dict[str, bool]:
        """Check health of all subsystems."""
        if not self._is_initialized:
            return {"engine": False, "database": False, "services": False}
        
        health_status = {"engine": True}
        
        try:
            with self._create_session() as session:
                sync_service = SyncService(session)
                conversion_service = ConversionService(session)
                
                health_status["database"] = True
                health_status["sync_service"] = sync_service.health_check()
                health_status["conversion_service"] = conversion_service.health_check()
                
        except Exception:
            health_status.update({
                "database": False,
                "sync_service": False,
                "conversion_service": False
            })
        
        return health_status
    
    def _ensure_initialized(self) -> None:
        """Ensure engine is initialized before operations."""
        if not self._is_initialized:
            raise TSVTranslateError("Engine not initialized. Call initialize() first.")
    
    def _create_session(self) -> Session:
        """Create database session for service operations."""
        if not self._session_factory:
            raise TSVTranslateError("Session factory not available")
        return self._session_factory()
    
    def _setup_file_watcher(self) -> None:
        """Setup file system monitoring."""
        watch_directory = Path(self._config.get("tsv_directory", "config/tsv_rules"))
        
        # Ensure directory exists
        watch_directory.mkdir(parents=True, exist_ok=True)
        
        # Create file watcher with callback functions
        self._file_watcher = FileWatcher(
            watch_directory=watch_directory,
            sync_callback=self._on_file_changed,
            delete_callback=self._on_file_deleted
        )
    
    def _on_file_changed(self, file_path: Path) -> None:
        """Callback for file system changes."""
        try:
            result = self.sync_file(file_path)
            if not result.is_successful:
                print(f"Sync failed for {file_path}: {result.error_message}")
        except Exception as e:
            print(f"Error processing file change {file_path}: {e}")
    
    def _on_file_deleted(self, rule_set_name: str) -> None:
        """Callback for file deletions."""
        try:
            result = self.remove_rule_set(rule_set_name)
            if not result.is_successful:
                print(f"Delete failed for {rule_set_name}: {result.error_message}")
        except Exception as e:
            print(f"Error processing file deletion {rule_set_name}: {e}")
    
    def shutdown(self) -> None:
        """Clean shutdown of all resources."""
        if self._file_watcher:
            self._file_watcher.stop()
        
        if self._engine:
            self._engine.dispose()
        
        self._is_initialized = False
    
    def __enter__(self) -> "TSVTranslateEngine":
        """Context manager entry."""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit with cleanup."""
        self.shutdown()