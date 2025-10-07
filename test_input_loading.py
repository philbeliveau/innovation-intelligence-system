#!/usr/bin/env python3
"""
Test script for validating input document loading.

This script:
1. Loads the input manifest from data/input-manifest.yaml
2. Attempts to load each PDF using LangChain's PyPDFLoader
3. Validates each document contains minimum 100 characters
4. Prints character count and loading status for each document
"""

import sys
import yaml
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader


def load_manifest(manifest_path: Path) -> dict:
    """Load the input manifest YAML file."""
    try:
        with open(manifest_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"❌ ERROR: Manifest file not found at {manifest_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"❌ ERROR: Invalid YAML in manifest file: {e}")
        sys.exit(1)


def test_document_loading(document_dir: Path, inputs: list) -> dict:
    """
    Test loading each document and return results.

    Args:
        document_dir: Path to directory containing PDF files
        inputs: List of input document metadata from manifest

    Returns:
        Dict with test results summary
    """
    results = {
        'total': len(inputs),
        'passed': 0,
        'failed': 0,
        'details': []
    }

    print(f"\n{'='*70}")
    print(f"Testing {len(inputs)} input documents")
    print(f"{'='*70}\n")

    for input_doc in inputs:
        doc_id = input_doc['id']
        filename = input_doc['filename']
        doc_type = input_doc['type']
        description = input_doc['description']

        file_path = document_dir / filename

        print(f"📄 Testing: {doc_id}")
        print(f"   File: {filename}")
        print(f"   Type: {doc_type}")

        # Test 1: File exists
        if not file_path.exists():
            print(f"   ❌ FAILED: File not found at {file_path}")
            results['failed'] += 1
            results['details'].append({
                'id': doc_id,
                'status': 'failed',
                'error': 'File not found'
            })
            print()
            continue

        # Test 2: Load with PyPDFLoader
        try:
            loader = PyPDFLoader(str(file_path))
            documents = loader.load()

            if not documents:
                print(f"   ❌ FAILED: No content extracted from PDF")
                results['failed'] += 1
                results['details'].append({
                    'id': doc_id,
                    'status': 'failed',
                    'error': 'No content extracted'
                })
                print()
                continue

            # Combine all page content
            full_content = " ".join([doc.page_content for doc in documents])
            char_count = len(full_content)
            page_count = len(documents)

            print(f"   📊 Pages: {page_count}")
            print(f"   📊 Characters: {char_count:,}")

            # Test 3: Minimum character count
            if char_count < 100:
                print(f"   ❌ FAILED: Content below minimum 100 characters ({char_count})")
                results['failed'] += 1
                results['details'].append({
                    'id': doc_id,
                    'status': 'failed',
                    'error': f'Insufficient content ({char_count} chars)'
                })
            else:
                print(f"   ✅ PASSED: All validations successful")
                results['passed'] += 1
                results['details'].append({
                    'id': doc_id,
                    'status': 'passed',
                    'pages': page_count,
                    'characters': char_count
                })

        except Exception as e:
            print(f"   ❌ FAILED: Error loading PDF: {str(e)}")
            results['failed'] += 1
            results['details'].append({
                'id': doc_id,
                'status': 'failed',
                'error': str(e)
            })

        print()

    return results


def print_summary(results: dict):
    """Print test results summary."""
    print(f"{'='*70}")
    print(f"TEST SUMMARY")
    print(f"{'='*70}")
    print(f"Total documents: {results['total']}")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"{'='*70}\n")

    if results['failed'] > 0:
        print("Failed documents:")
        for detail in results['details']:
            if detail['status'] == 'failed':
                print(f"  - {detail['id']}: {detail['error']}")
        print()


def main():
    """Main test execution."""
    # Define paths
    project_root = Path(__file__).parent
    manifest_path = project_root / 'data' / 'input-manifest.yaml'
    document_dir = project_root / 'documentation' / 'document'

    print("\n🧪 Input Document Loading Test")
    print(f"Project root: {project_root}")
    print(f"Manifest: {manifest_path}")
    print(f"Document directory: {document_dir}")

    # Load manifest
    manifest = load_manifest(manifest_path)
    inputs = manifest.get('inputs', [])

    if not inputs:
        print("❌ ERROR: No inputs found in manifest")
        sys.exit(1)

    # Test all documents
    results = test_document_loading(document_dir, inputs)

    # Print summary
    print_summary(results)

    # Exit with appropriate code
    sys.exit(0 if results['failed'] == 0 else 1)


if __name__ == '__main__':
    main()
