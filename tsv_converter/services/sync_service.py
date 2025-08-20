"""TSV file synchronization service.

Demonstrates clean architecture with abstract interfaces,
dependency injection, and comprehensive error handling.
"""

import hashlib
import csv
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from .base import BaseService
from ..models import RuleSet, ConversionRule
from ..core.types import SyncResult, OperationStatus
from ..core.exceptions import SyncError, ValidationError


class SyncServiceInterface(ABC):
    """Interface for TSV synchronization operations.
    
    Follows interface segregation principle, defining only
    the operations needed by clients.
    """
    
    @abstractmethod
    def sync_file(self, file_path: Path) -> SyncResult:
        """Synchronize a single TSV file with database."""
        pass
    
    @abstractmethod
    def sync_directory(self, directory_path: Path) -> List[SyncResult]:
        """Synchronize all TSV files in directory."""
        pass
    
    @abstractmethod
    def remove_rule_set(self, rule_set_name: str) -> SyncResult:
        """Remove rule set from database."""
        pass


class SyncService(BaseService, SyncServiceInterface):
    """TSV file synchronization implementation.
    
    Educational example of:
    - Clean error handling with specific exception types
    - Database transaction management
    - File integrity verification with hashing
    - Comprehensive logging and result tracking
    """
    
    def health_check(self) -> bool:
        """Verify database connectivity and basic operations."""
        try:
            # Simple connectivity test
            self._db_session.execute("SELECT 1").fetchone()
            return True
        except SQLAlchemyError:
            return False
    
    def sync_file(self, file_path: Path) -> SyncResult:
        """Synchronize TSV file with database.
        
        Implements atomic operations with proper transaction management
        and comprehensive error handling.
        """
        rule_set_name = file_path.stem
        
        try:
            # Calculate file hash for integrity checking
            file_hash = self._calculate_file_hash(file_path)
            
            # Check if file needs synchronization
            existing_rule_set = self._get_existing_rule_set(rule_set_name)
            if existing_rule_set and existing_rule_set.file_hash == file_hash:
                return SyncResult(
                    status=OperationStatus.SUCCESS,
                    rule_set_name=rule_set_name,
                    operation="skip",
                    rules_processed=existing_rule_set.rule_count
                )
            
            # Parse TSV file
            conversion_rules = self._parse_tsv_file(file_path)
            
            # Perform database synchronization
            return self._sync_to_database(
                rule_set_name, str(file_path), file_hash, conversion_rules
            )
            
        except (OSError, ValidationError) as e:
            return SyncResult(
                status=OperationStatus.ERROR,
                rule_set_name=rule_set_name,
                operation="error",
                error_message=str(e)
            )
    
    def sync_directory(self, directory_path: Path) -> List[SyncResult]:
        """Synchronize all TSV files in directory."""
        results = []
        
        try:
            tsv_files = list(directory_path.glob("*.tsv"))
            for tsv_file in tsv_files:
                result = self.sync_file(tsv_file)
                results.append(result)
                
        except OSError as e:
            # Add error result for directory access failure
            results.append(SyncResult(
                status=OperationStatus.ERROR,
                rule_set_name="directory_sync",
                operation="error",
                error_message=f"Directory access failed: {str(e)}"
            ))
        
        return results
    
    def remove_rule_set(self, rule_set_name: str) -> SyncResult:
        """Remove rule set from database (not the file)."""
        try:
            rule_set = self._get_existing_rule_set(rule_set_name)
            if not rule_set:
                return SyncResult(
                    status=OperationStatus.WARNING,
                    rule_set_name=rule_set_name,
                    operation="delete",
                    error_message="Rule set not found"
                )
            
            rules_count = rule_set.rule_count
            self._db_session.delete(rule_set)
            self._db_session.commit()
            
            return SyncResult(
                status=OperationStatus.SUCCESS,
                rule_set_name=rule_set_name,
                operation="delete",
                rules_deleted=rules_count
            )
            
        except SQLAlchemyError as e:
            self._db_session.rollback()
            return SyncResult(
                status=OperationStatus.ERROR,
                rule_set_name=rule_set_name,
                operation="delete",
                error_message=f"Database error: {str(e)}"
            )
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash for file integrity."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _get_existing_rule_set(self, name: str) -> Optional[RuleSet]:
        """Retrieve existing rule set by name."""
        return (
            self._db_session.query(RuleSet)
            .filter(RuleSet.name == name)
            .first()
        )
    
    def _parse_tsv_file(self, file_path: Path) -> List[tuple[str, str]]:
        """Parse TSV file into conversion rules.
        
        Validates file format and handles encoding properly.
        """
        rules = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', newline='') as f:
                reader = csv.reader(f, delimiter='\t')
                
                for line_no, row in enumerate(reader, 1):
                    if len(row) != 2:
                        raise ValidationError(
                            f"Line {line_no}: Expected 2 columns, got {len(row)}"
                        )
                    
                    source_text, target_text = row[0].strip(), row[1].strip()
                    if not source_text:
                        raise ValidationError(
                            f"Line {line_no}: Source text cannot be empty"
                        )
                    
                    rules.append((source_text, target_text))
                    
        except UnicodeDecodeError as e:
            raise ValidationError(f"File encoding error: {str(e)}")
        
        return rules
    
    def _sync_to_database(
        self,
        rule_set_name: str,
        file_path: str,
        file_hash: str,
        conversion_rules: List[tuple[str, str]]
    ) -> SyncResult:
        """Synchronize parsed rules to database with transaction safety."""
        try:
            # Get or create rule set
            rule_set = self._get_existing_rule_set(rule_set_name)
            operation = "update" if rule_set else "create"
            
            if rule_set:
                # Clear existing rules for clean replacement
                self._db_session.query(ConversionRule).filter(
                    ConversionRule.rule_set_id == rule_set.id
                ).delete()
            else:
                # Create new rule set
                rule_set = RuleSet(
                    name=rule_set_name,
                    file_path=file_path,
                    file_hash=file_hash,
                    rule_count=0
                )
                self._db_session.add(rule_set)
                self._db_session.flush()  # Get ID for foreign key
            
            # Update rule set metadata
            rule_set.file_hash = file_hash
            rule_set.rule_count = len(conversion_rules)
            
            # Add conversion rules
            for source_text, target_text in conversion_rules:
                rule = ConversionRule(
                    rule_set_id=rule_set.id,
                    source_text=source_text,
                    target_text=target_text
                )
                self._db_session.add(rule)
            
            self._db_session.commit()
            
            return SyncResult(
                status=OperationStatus.SUCCESS,
                rule_set_name=rule_set_name,
                operation=operation,
                rules_processed=len(conversion_rules),
                rules_added=len(conversion_rules) if operation == "create" else 0,
                rules_updated=len(conversion_rules) if operation == "update" else 0,
                file_hash=file_hash
            )
            
        except SQLAlchemyError as e:
            self._db_session.rollback()
            raise SyncError(f"Database synchronization failed: {str(e)}")