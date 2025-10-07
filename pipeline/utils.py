"""
Utility functions for the Innovation Intelligence Pipeline.

This module provides helper functions for output directory management,
logging configuration, and common utilities used across pipeline stages.
"""

import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Optional
from langchain_openai import ChatOpenAI


def create_llm(temperature: float = 0.5, max_tokens: int = 4000) -> ChatOpenAI:
    """Create configured LLM instance with centralized model settings.

    ⚡ SINGLE SOURCE OF TRUTH FOR MODEL CONFIGURATION ⚡
    Change LLM_MODEL in .env to switch models across entire pipeline.

    Args:
        temperature: LLM temperature (0.0-1.0, default: 0.5)
        max_tokens: Maximum tokens in response (default: 4000)

    Returns:
        Configured ChatOpenAI instance

    Raises:
        ValueError: If required environment variables not set

    Example:
        >>> llm = create_llm(temperature=0.7, max_tokens=3000)
        >>> # Uses model from LLM_MODEL env variable
    """
    # Validate environment variables
    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENROUTER_BASE_URL")
    model = os.getenv("LLM_MODEL", "deepseek/deepseek-chat")  # Default to DeepSeek

    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY not set. "
            "Please configure in .env file (see .env.template)"
        )

    if not base_url:
        raise ValueError(
            "OPENROUTER_BASE_URL not set. "
            "Please configure in .env file (see .env.template)"
        )

    logging.debug(
        f"Creating LLM: model={model}, temperature={temperature}, "
        f"max_tokens={max_tokens}"
    )

    return ChatOpenAI(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        openai_api_key=api_key,
        base_url=base_url
    )


def create_test_output_dir(
    input_id: str,
    brand_id: str,
    base_dir: Path = Path("data/test-outputs")
) -> Path:
    """Create test output directory with timestamp and subdirectory structure.

    Directory naming convention: {input-id}-{brand-id}-{timestamp}
    Example: savannah-bananas-lactalis-canada-20251007-142345

    Creates the following subdirectories:
    - stage1/, stage2/, stage3/, stage4/, stage5/ (pipeline stage outputs)
    - logs/ (pipeline and error logs)

    Each subdirectory includes a .gitkeep file to preserve structure in git.

    Args:
        input_id: Input document ID
        brand_id: Brand profile ID
        base_dir: Base directory for test outputs (default: data/test-outputs)

    Returns:
        Path to created output directory

    Raises:
        OSError: If directory creation fails

    Example:
        >>> output_dir = create_test_output_dir("savannah-bananas", "lactalis-canada")
        >>> print(output_dir)
        data/test-outputs/savannah-bananas-lactalis-canada-20251007-142345
    """
    # Generate timestamp in ISO format (YYYYMMDD-HHMMSS)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir_name = f"{input_id}-{brand_id}-{timestamp}"
    output_dir = base_dir / output_dir_name

    try:
        # Create base output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        logging.debug(f"Created base output directory: {output_dir}")

        # Create stage output directories with .gitkeep files
        for stage_num in range(1, 6):
            stage_dir = output_dir / f"stage{stage_num}"
            stage_dir.mkdir(exist_ok=True)

            # Add .gitkeep to preserve empty directory in git
            gitkeep_file = stage_dir / ".gitkeep"
            gitkeep_file.touch()
            logging.debug(f"Created stage directory: {stage_dir}")

        # Create logs directory with .gitkeep
        logs_dir = output_dir / "logs"
        logs_dir.mkdir(exist_ok=True)

        gitkeep_file = logs_dir / ".gitkeep"
        gitkeep_file.touch()
        logging.debug(f"Created logs directory: {logs_dir}")

        logging.info(f"Output directory created: {output_dir}")
        return output_dir

    except OSError as e:
        logging.error(f"Failed to create output directory {output_dir}: {e}")
        raise


def setup_pipeline_logging(
    output_dir: Path,
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG
) -> None:
    """Configure pipeline logging with console and file handlers.

    Sets up three logging destinations:
    1. Console: INFO level (or specified console_level)
    2. File (pipeline.log): DEBUG level (or specified file_level) - all logs
    3. File (errors.log): ERROR level only - errors and exceptions

    Logging format includes timestamp, logger name, level, and message.

    Args:
        output_dir: Output directory path (must contain logs/ subdirectory)
        console_level: Logging level for console output (default: INFO)
        file_level: Logging level for file output (default: DEBUG)

    Example:
        >>> output_dir = create_test_output_dir("savannah-bananas", "lactalis-canada")
        >>> setup_pipeline_logging(output_dir)
        >>> logging.info("Pipeline started")  # Goes to console and pipeline.log
        >>> logging.debug("Detailed info")    # Goes only to pipeline.log
        >>> logging.error("Error occurred")   # Goes to console, pipeline.log, and errors.log
    """
    # Clear any existing handlers to avoid duplication
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.DEBUG)  # Capture all levels, handlers will filter

    # Define log format with timestamp
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler (INFO level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)

    # File handler - pipeline.log (DEBUG level - all logs)
    logs_dir = output_dir / "logs"
    pipeline_log_file = logs_dir / "pipeline.log"

    file_handler = logging.FileHandler(pipeline_log_file, encoding='utf-8')
    file_handler.setLevel(file_level)
    file_handler.setFormatter(log_format)
    root_logger.addHandler(file_handler)

    # File handler - errors.log (ERROR level only)
    error_log_file = logs_dir / "errors.log"

    error_handler = logging.FileHandler(error_log_file, encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(log_format)
    root_logger.addHandler(error_handler)

    logging.info(f"Logging configured: console={logging.getLevelName(console_level)}, file={logging.getLevelName(file_level)}")
    logging.debug(f"Pipeline log: {pipeline_log_file}")
    logging.debug(f"Error log: {error_log_file}")


def load_brand_profile(brand_id: str, brand_profiles_dir: Path = Path("data/brand-profiles")) -> dict:
    """Load brand profile from YAML file.

    Args:
        brand_id: Brand profile ID (filename without .yaml extension)
        brand_profiles_dir: Directory containing brand profile YAML files

    Returns:
        Dictionary containing brand profile data

    Raises:
        FileNotFoundError: If brand profile file doesn't exist
        ValueError: If brand profile YAML is invalid
    """
    import yaml

    profile_path = brand_profiles_dir / f"{brand_id}.yaml"

    if not profile_path.exists():
        logging.error(f"Brand profile not found: {profile_path}")
        raise FileNotFoundError(
            f"Brand profile '{brand_id}' not found. "
            f"Expected: {profile_path}"
        )

    try:
        with open(profile_path, 'r', encoding='utf-8') as f:
            profile = yaml.safe_load(f)
            logging.debug(f"Loaded brand profile: {profile_path}")
            return profile
    except yaml.YAMLError as e:
        logging.error(f"Invalid YAML in {profile_path}: {e}")
        raise ValueError(f"Invalid brand profile YAML: {e}")


def load_input_document(input_id: str, input_manifest_path: Path = Path("data/input-manifest.yaml")) -> str:
    """Load input document content from PDF file specified in manifest.

    Args:
        input_id: Input document ID from manifest
        input_manifest_path: Path to input manifest YAML file

    Returns:
        Extracted text content from PDF document

    Raises:
        FileNotFoundError: If manifest or PDF file doesn't exist
        ValueError: If input_id not found in manifest
    """
    import yaml
    from pypdf import PdfReader

    # Load manifest
    if not input_manifest_path.exists():
        raise FileNotFoundError(f"Input manifest not found: {input_manifest_path}")

    with open(input_manifest_path, 'r', encoding='utf-8') as f:
        manifest = yaml.safe_load(f)

    # Find input document in manifest
    input_doc = None
    for doc in manifest.get('inputs', []):
        if doc['id'] == input_id:
            input_doc = doc
            break

    if not input_doc:
        raise ValueError(f"Input ID '{input_id}' not found in manifest")

    # Load PDF file
    pdf_path = Path(input_doc['file_path'])
    if not pdf_path.exists():
        raise FileNotFoundError(f"Input PDF not found: {pdf_path}")

    # Extract text from PDF
    reader = PdfReader(pdf_path)
    text_content = ""
    for page in reader.pages:
        text_content += page.extract_text()

    logging.debug(f"Loaded input document: {pdf_path} ({len(text_content)} characters)")
    return text_content


def load_research_data(
    brand_id: str,
    research_directory: Path = Path("docs/web-search-setup")
) -> str:
    """Load pre-generated brand research from markdown file.

    Each brand has comprehensive research (~550-720 lines, 35-48KB) with 8 sections:
    1. Brand Overview & Positioning
    2. Product Portfolio & Innovation
    3. Recent Innovations (Last 18 Months)
    4. Strategic Priorities & Business Strategy
    5. Target Customers & Market Positioning
    6. Sustainability & Social Responsibility
    7. Competitive Context & Market Trends
    8. Recent News & Market Signals (Last 6 Months)

    File naming convention: {brand-id}-research.md
    Example: lactalis-canada-research.md

    Args:
        brand_id: Brand identifier (e.g., 'lactalis-canada', 'mccormick-usa')
        research_directory: Directory containing research markdown files
                           (default: docs/web-search-setup)

    Returns:
        Complete research content as string for Stage 4 prompt injection.
        Returns empty string if file missing or unreadable (non-fatal error).

    Example:
        >>> research = load_research_data("lactalis-canada")
        >>> print(f"Loaded {len(research)} characters of research")
    """
    research_file = research_directory / f"{brand_id}-research.md"

    # Handle missing file gracefully (non-fatal)
    if not research_file.exists():
        logging.warning(
            f"Research file not found: {research_file}. "
            f"Proceeding without research data."
        )
        return ""

    try:
        # Read research content with UTF-8 encoding
        research_content = research_file.read_text(encoding='utf-8')

        # Calculate file statistics for logging
        line_count = research_content.count('\n') + 1
        file_size_kb = research_file.stat().st_size / 1024

        logging.info(
            f"Loaded research data: {research_file} "
            f"({line_count} lines, {file_size_kb:.1f} KB)"
        )

        return research_content

    except Exception as e:
        # Log warning but return empty string (non-fatal error)
        logging.warning(
            f"Failed to read research file {research_file}: {e}. "
            f"Proceeding without research data."
        )
        return ""
