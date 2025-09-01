"""Test configuration and fixtures.

Educational example of pytest fixtures providing clean,
reusable test infrastructure with proper setup/teardown.
"""

import tempfile
import pytest
from pathlib import Path
try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    create_engine = None  # type: ignore
    sessionmaker = None  # type: ignore

from ..models import Base
from ..core.engine import TSVTranslateEngine
from ..services import SyncService, ConversionService


@pytest.fixture
def temp_directory():
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def test_database():
    """Create in-memory test database."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    engine.dispose()


@pytest.fixture
def sample_tsv_content():
    """Sample TSV content for testing."""
    return """hello	こんにちは
goodbye	さようなら
thank you	ありがとう"""


@pytest.fixture
def sample_tsv_file(temp_directory, sample_tsv_content):
    """Create sample TSV file for testing."""
    tsv_file = temp_directory / "test_rules.tsv"
    tsv_file.write_text(sample_tsv_content, encoding='utf-8')
    return tsv_file


@pytest.fixture
def test_config(temp_directory):
    """Test configuration dictionary."""
    return {
        "database_url": "sqlite:///:memory:",
        "tsv_directory": str(temp_directory),
        "enable_file_watching": False,
        "debug": True,
        "security": {"enable_encryption": False}
    }


@pytest.fixture
def translate_engine(test_config):
    """TSV translator engine for testing."""
    with TSVTranslateEngine(test_config) as engine:
        yield engine


@pytest.fixture
def sync_service(test_database):
    """Sync service instance for testing."""
    return SyncService(test_database)


@pytest.fixture
def conversion_service(test_database):
    """Conversion service instance for testing."""
    return ConversionService(test_database)