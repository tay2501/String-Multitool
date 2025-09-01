"""File system monitoring for automatic TSV synchronization.

Demonstrates clean event-driven architecture using the watchdog library
with proper error handling and debouncing mechanisms.
"""

import time
from pathlib import Path
from typing import Callable, Dict, Set
from watchdog.observers import Observer
from watchdog.events import (
    FileSystemEventHandler, 
    FileSystemEvent,
    FileModifiedEvent, 
    FileCreatedEvent, 
    FileDeletedEvent,
    DirCreatedEvent,
    DirModifiedEvent,
    DirDeletedEvent
)

from ..core.exceptions import SyncError


class TSVFileHandler(FileSystemEventHandler):
    """File system event handler for TSV files.
    
    Educational patterns:
    - Event debouncing to prevent duplicate processing
    - Callback-based architecture for loose coupling
    - Clean separation of file monitoring and business logic
    """
    
    def __init__(
        self,
        sync_callback: Callable[[Path], None],
        delete_callback: Callable[[str], None],
        debounce_seconds: float = 1.0
    ) -> None:
        """Initialize with callback functions for decoupled processing.
        
        Args:
            sync_callback: Called when file needs synchronization
            delete_callback: Called when file is deleted
            debounce_seconds: Minimum time between processing same file
        """
        self._sync_callback = sync_callback
        self._delete_callback = delete_callback
        self._debounce_seconds = debounce_seconds
        
        # Debouncing mechanism to prevent excessive processing
        self._last_processed: Dict[str, float] = {}
        self._pending_deletes: Set[str] = set()
        
    def on_created(self, event: FileCreatedEvent | DirCreatedEvent) -> None:
        """Handle file creation events."""
        src_path = str(event.src_path)
        if not event.is_directory and self._is_tsv_file(src_path):
            self._schedule_sync(Path(src_path))
    
    def on_modified(self, event: FileModifiedEvent | DirModifiedEvent) -> None:
        """Handle file modification events."""
        src_path = str(event.src_path)
        if not event.is_directory and self._is_tsv_file(src_path):
            self._schedule_sync(Path(src_path))
    
    def on_deleted(self, event: FileDeletedEvent | DirDeletedEvent) -> None:
        """Handle file deletion events."""
        src_path = str(event.src_path)
        if not event.is_directory and self._is_tsv_file(src_path):
            rule_set_name = Path(src_path).stem
            self._pending_deletes.add(rule_set_name)
            self._schedule_delete(rule_set_name)
    
    def _is_tsv_file(self, file_path: str) -> bool:
        """Check if file is a TSV file."""
        return file_path.lower().endswith('.tsv')
    
    def _schedule_sync(self, file_path: Path) -> None:
        """Schedule file synchronization with debouncing."""
        current_time = time.time()
        file_key = str(file_path)
        
        # Check if we should process this file (debouncing)
        last_processed = self._last_processed.get(file_key, 0)
        if current_time - last_processed < self._debounce_seconds:
            return
        
        # Remove from pending deletes if file was recreated
        rule_set_name = file_path.stem
        self._pending_deletes.discard(rule_set_name)
        
        try:
            self._sync_callback(file_path)
            self._last_processed[file_key] = current_time
        except Exception as e:
            # Log error but don't crash the file watcher
            print(f"Sync error for {file_path}: {e}")
    
    def _schedule_delete(self, rule_set_name: str) -> None:
        """Schedule rule set deletion with delay to handle rapid recreates."""
        # Simple delay mechanism - in production, use proper task scheduling
        time.sleep(0.5)
        
        if rule_set_name in self._pending_deletes:
            try:
                self._delete_callback(rule_set_name)
                self._pending_deletes.remove(rule_set_name)
            except Exception as e:
                print(f"Delete error for {rule_set_name}: {e}")


class FileWatcher:
    """File system watcher for TSV directory monitoring.
    
    Clean implementation of file monitoring with proper resource management
    and graceful shutdown capabilities.
    """
    
    def __init__(
        self,
        watch_directory: Path,
        sync_callback: Callable[[Path], None],
        delete_callback: Callable[[str], None]
    ) -> None:
        """Initialize file watcher.
        
        Args:
            watch_directory: Directory to monitor for TSV files
            sync_callback: Function to call for file synchronization
            delete_callback: Function to call for rule set deletion
        """
        self._watch_directory = watch_directory
        self._observer = Observer()
        self._event_handler = TSVFileHandler(sync_callback, delete_callback)
        self._is_running = False
    
    def start(self) -> None:
        """Start monitoring the directory.
        
        Raises:
            SyncError: If directory doesn't exist or can't be monitored
        """
        if not self._watch_directory.exists():
            raise SyncError(f"Watch directory does not exist: {self._watch_directory}")
        
        if not self._watch_directory.is_dir():
            raise SyncError(f"Watch path is not a directory: {self._watch_directory}")
        
        try:
            self._observer.schedule(
                self._event_handler,
                str(self._watch_directory),
                recursive=False
            )
            self._observer.start()
            self._is_running = True
            
        except Exception as e:
            raise SyncError(f"Failed to start file watcher: {e}")
    
    def stop(self) -> None:
        """Stop monitoring and cleanup resources."""
        if self._is_running:
            self._observer.stop()
            self._observer.join(timeout=5.0)  # Wait for graceful shutdown
            self._is_running = False
    
    @property
    def is_running(self) -> bool:
        """Check if watcher is currently active."""
        return self._is_running and self._observer.is_alive()
    
    def __enter__(self) -> "FileWatcher":
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore[no-untyped-def]
        """Context manager exit with cleanup."""
        self.stop()