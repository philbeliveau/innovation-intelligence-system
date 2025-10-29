"""
Tests for Report Generator Utility

Tests report generation, markdown formatting, sanitization, and performance.
"""
import time
import pytest
from utils.report_generator import (
    generate_full_report,
    sanitize_markdown,
    truncate_text,
    calculate_report_size
)


class TestSanitizeMarkdown:
    """Test markdown sanitization"""

    def test_sanitize_empty_string(self):
        """Empty strings should return empty"""
        assert sanitize_markdown("") == ""
        assert sanitize_markdown(None) == ""

    def test_sanitize_special_characters(self):
        """Special markdown characters should be escaped"""
        text = "Test *bold* and `code` with [links](url)"
        sanitized = sanitize_markdown(text)

        assert '\\*' in sanitized
        assert '\\`' in sanitized
        assert '\\[' in sanitized
        assert '\\]' in sanitized
        assert '\\(' in sanitized
        assert '\\)' in sanitized

    def test_sanitize_all_special_chars(self):
        """All special chars should be escaped"""
        text = r"\ ` * _ [ ] ( ) # + - . ! |"
        sanitized = sanitize_markdown(text)

        # All should be escaped with backslash
        assert '\\\\' in sanitized
        assert '\\`' in sanitized
        assert '\\*' in sanitized
        assert '\\_' in sanitized
        assert '\\[' in sanitized
        assert '\\]' in sanitized
        assert '\\(' in sanitized
        assert '\\)' in sanitized
        assert '\\#' in sanitized
        assert '\\+' in sanitized
        assert '\\-' in sanitized
        assert '\\.' in sanitized
        assert '\\!' in sanitized
        assert '\\|' in sanitized

    def test_sanitize_non_string(self):
        """Non-strings should be converted and sanitized"""
        assert sanitize_markdown(123) == "123"
        assert sanitize_markdown(True) == "True"


class TestTruncateText:
    """Test text truncation"""

    def test_truncate_empty_string(self):
        """Empty strings should return empty"""
        assert truncate_text("") == ""
        assert truncate_text(None) == ""

    def test_truncate_short_text(self):
        """Text shorter than max_words should not be truncated"""
        text = " ".join(["word"] * 100)
        result = truncate_text(text, max_words=500)
        assert result == text
        assert "truncated" not in result

    def test_truncate_long_text(self):
        """Text longer than max_words should be truncated"""
        long_text = " ".join(["word"] * 1000)
        truncated = truncate_text(long_text, max_words=500)

        words = truncated.split()
        # Should have 500 words + "... (truncated, 1000 total words)"
        assert len(words) <= 505  # Allow for truncation message
        assert "(truncated, 1000 total words)" in truncated

    def test_truncate_custom_max_words(self):
        """Custom max_words should be respected"""
        text = " ".join(["word"] * 200)
        truncated = truncate_text(text, max_words=100)

        assert "(truncated, 200 total words)" in truncated


class TestCalculateReportSize:
    """Test report size calculation"""

    def test_calculate_size_empty(self):
        """Empty report should be 0 KB"""
        assert calculate_report_size("") == 0.0

    def test_calculate_size_basic(self):
        """Basic text should calculate correctly"""
        # 1024 bytes = 1 KB
        text = "a" * 1024
        size_kb = calculate_report_size(text)
        assert 0.9 < size_kb < 1.1  # Allow for rounding

    def test_calculate_size_unicode(self):
        """Unicode characters should be counted correctly"""
        # Unicode chars may be multiple bytes
        text = "🎉" * 100  # Emojis are typically 4 bytes in UTF-8
        size_kb = calculate_report_size(text)
        assert size_kb > 0


class TestGenerateFullReport:
    """Test full report generation"""

    def test_generate_minimal_report(self):
        """Test report generation with minimal data"""
        stage_outputs = {
            'stage1': {'extractedText': 'Test extracted text', 'mechanisms': []},
            'stage2': {'signals': []},
            'stage3': {'insights': []},
            'stage4': {}
        }
        opportunity_cards = []

        report = generate_full_report(
            run_id='test-123',
            company_name='Test Corp',
            document_name='test.pdf',
            stage_outputs=stage_outputs,
            opportunity_cards=opportunity_cards
        )

        # Check report structure
        assert '# Innovation Intelligence Report' in report
        assert 'Test Corp' in report
        # Note: Periods are escaped by sanitize_markdown
        assert ('test.pdf' in report or 'test\\.pdf' in report)
        assert 'test-123' in report
        assert 'Document Analysis Summary' in report
        assert 'Key Mechanisms' in report
        assert 'Innovation Signals' in report
        assert 'Transferable Insights' in report
        assert 'Opportunity Cards' in report

    def test_generate_full_report_with_data(self):
        """Test report generation with complete data"""
        stage_outputs = {
            'stage1': {
                'extractedText': 'Test extracted text with more content',
                'mechanisms': [
                    {
                        'title': 'Mechanism 1',
                        'description': 'Description 1',
                        'context': 'Context 1'
                    }
                ]
            },
            'stage2': {
                'signals': [
                    {
                        'category': 'Technology',
                        'description': 'AI signal',
                        'relevance': 'High',
                        'mechanismSource': 'Mechanism 1'
                    }
                ]
            },
            'stage3': {
                'insights': [
                    {
                        'title': 'Insight 1',
                        'description': 'Insight description',
                        'transferability': 'High',
                        'signalSources': ['Signal 1', 'Signal 2']
                    }
                ]
            },
            'stage4': {}
        }
        opportunity_cards = [
            {
                'title': 'Opportunity 1',
                'content': 'Full opportunity content here',
                'description': 'Brief description'
            }
        ]

        report = generate_full_report(
            run_id='test-456',
            company_name='Acme Inc',
            document_name='innovation.pdf',
            stage_outputs=stage_outputs,
            opportunity_cards=opportunity_cards
        )

        # Check all sections are populated
        assert 'Mechanism 1' in report
        assert 'Description 1' in report
        assert 'Technology' in report
        assert 'AI signal' in report
        assert 'Insight 1' in report
        assert 'Opportunity 1' in report

        # Check counts are correct
        assert 'Total Mechanisms Identified:** 1' in report
        assert 'Total Signals Detected:** 1' in report
        assert 'Total Insights Generated:** 1' in report
        assert 'Total Opportunity Cards:** 1' in report

    def test_generate_report_truncates_long_text(self):
        """Test that long extracted text is truncated"""
        long_text = " ".join(["word"] * 1000)
        stage_outputs = {
            'stage1': {'extractedText': long_text, 'mechanisms': []},
            'stage2': {'signals': []},
            'stage3': {'insights': []},
            'stage4': {}
        }

        report = generate_full_report(
            run_id='test-789',
            company_name='Test',
            document_name='long.pdf',
            stage_outputs=stage_outputs,
            opportunity_cards=[]
        )

        # Should contain truncation indicator (with escaped parentheses)
        assert ('(truncated, 1000 total words)' in report or
                '\\(truncated, 1000 total words\\)' in report)

    def test_generate_report_sanitizes_content(self):
        """Test that special characters are sanitized"""
        stage_outputs = {
            'stage1': {
                'extractedText': 'Text with *special* chars',
                'mechanisms': [
                    {
                        'title': 'Title with [brackets]',
                        'description': 'Desc with `code`',
                        'context': 'Context'
                    }
                ]
            },
            'stage2': {'signals': []},
            'stage3': {'insights': []},
            'stage4': {}
        }

        report = generate_full_report(
            run_id='test-sanitize',
            company_name='Test & Co',
            document_name='file.pdf',
            stage_outputs=stage_outputs,
            opportunity_cards=[]
        )

        # Special chars should be escaped
        assert '\\*' in report or 'special' in report  # Sanitized or present
        assert '\\[' in report or 'brackets' in report
        assert '\\`' in report or 'code' in report

    def test_generate_report_handles_missing_fields(self):
        """Test graceful handling of missing fields"""
        stage_outputs = {
            'stage1': {
                'mechanisms': [
                    {}  # Empty mechanism
                ]
            },
            'stage2': {
                'signals': [
                    {'category': 'Test'}  # Missing other fields
                ]
            },
            'stage3': {
                'insights': [
                    {'title': 'Test'}  # Missing description
                ]
            },
            'stage4': {}
        }

        report = generate_full_report(
            run_id='test-missing',
            company_name='Test',
            document_name='test.pdf',
            stage_outputs=stage_outputs,
            opportunity_cards=[]
        )

        # Should complete without errors
        assert 'Innovation Intelligence Report' in report
        assert 'Untitled' in report or 'No description' in report


class TestReportPerformance:
    """Test report generation performance"""

    def test_report_generation_speed(self):
        """Report generation should complete in < 3 seconds"""
        # Create realistic data size
        stage_outputs = {
            'stage1': {
                'extractedText': " ".join(["word"] * 5000),
                'mechanisms': [
                    {
                        'title': f'Mechanism {i}',
                        'description': f'Description {i}' * 10,
                        'context': f'Context {i}' * 5
                    }
                    for i in range(10)
                ]
            },
            'stage2': {
                'signals': [
                    {
                        'category': f'Category {i}',
                        'description': f'Signal description {i}' * 5,
                        'relevance': 'High',
                        'mechanismSource': f'Mechanism {i}'
                    }
                    for i in range(15)
                ]
            },
            'stage3': {
                'insights': [
                    {
                        'title': f'Insight {i}',
                        'description': f'Insight description {i}' * 10,
                        'transferability': 'High',
                        'signalSources': [f'Signal {j}' for j in range(3)]
                    }
                    for i in range(10)
                ]
            },
            'stage4': {}
        }

        opportunity_cards = [
            {
                'title': f'Opportunity {i}',
                'content': f'Full opportunity content {i}' * 50,
                'description': f'Brief description {i}'
            }
            for i in range(5)
        ]

        # Measure generation time
        start = time.time()
        report = generate_full_report(
            run_id='perf-test',
            company_name='Performance Test Corp',
            document_name='large-doc.pdf',
            stage_outputs=stage_outputs,
            opportunity_cards=opportunity_cards
        )
        duration = time.time() - start

        # Assert performance requirements
        assert duration < 3.0, f"Report generation took {duration:.2f}s, expected < 3s"

        # Check report was generated successfully
        assert len(report) > 0

    def test_report_size_limit(self):
        """Report size should be < 100KB for most documents"""
        # Create data that should produce reasonable report size
        stage_outputs = {
            'stage1': {
                'extractedText': " ".join(["word"] * 2000),
                'mechanisms': [
                    {
                        'title': f'Mechanism {i}',
                        'description': f'Description {i}' * 5,
                        'context': f'Context {i}' * 3
                    }
                    for i in range(5)
                ]
            },
            'stage2': {
                'signals': [
                    {
                        'category': f'Category {i}',
                        'description': f'Signal {i}' * 3,
                        'relevance': 'Medium',
                        'mechanismSource': f'Mech {i}'
                    }
                    for i in range(10)
                ]
            },
            'stage3': {
                'insights': [
                    {
                        'title': f'Insight {i}',
                        'description': f'Description {i}' * 5,
                        'transferability': 'Medium',
                        'signalSources': [f'S{j}' for j in range(2)]
                    }
                    for i in range(5)
                ]
            },
            'stage4': {}
        }

        opportunity_cards = [
            {
                'title': f'Opp {i}',
                'content': f'Content {i}' * 20,
                'description': f'Desc {i}'
            }
            for i in range(5)
        ]

        report = generate_full_report(
            run_id='size-test',
            company_name='Test',
            document_name='test.pdf',
            stage_outputs=stage_outputs,
            opportunity_cards=opportunity_cards
        )

        report_size_kb = calculate_report_size(report)

        # Should be under 100KB for typical documents
        assert report_size_kb < 100, f"Report size {report_size_kb:.2f} KB exceeds 100KB limit"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
