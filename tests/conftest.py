import pytest
import sys
import logging
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging for tests to reduce memory usage
logging.basicConfig(
    level=logging.WARNING,
    format='%(levelname)s: %(message)s'
)

# Define fixtures that can be reused across tests
@pytest.fixture
def temp_db_path(tmp_path):
    """Return a temporary database path for testing"""
    return tmp_path / "test_esocial.db"

@pytest.fixture
def sample_xml_path():
    """Return path to sample XML files for testing"""
    base_path = Path(__file__).parent / "data"
    return base_path

@pytest.fixture(autouse=True)
def setup_logging():
    """Setup logging for all tests"""
    # Set all loggers to WARNING level to reduce output
    for logger_name in logging.root.manager.loggerDict:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
