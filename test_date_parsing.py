#!/usr/bin/env python3
"""
Quick test to verify date parsing works for all formats including "Tue 27 Jan"
"""

from datetime import datetime
from main import TermDetector

def test_date_formats():
    """Test various date formats including the new "Day DD Mon" format."""
    test_cases = [
        ("2026-06-03", "YYYY-MM-DD format"),
        ("03/06/2026", "DD/MM/YYYY format"),
        ("03/06/26", "DD/MM/YY format"),
        ("06/03/2026", "MM/DD/YYYY format"),
        ("03-06-2026", "DD-MM-YYYY format"),
        ("Tue 27 Jan", "Day DD Mon format (no year)"),
        ("Thu 02 Apr", "Day DD Mon format (April)"),
    ]

    print("\n" + "="*70)
    print("DATE PARSING TEST")
    print("="*70)
    print(f"\nTesting at: {datetime.now()}\n")

    passed = 0
    failed = 0

    for date_str, description in test_cases:
        try:
            parsed = TermDetector._parse_date(date_str)
            print(f"✅ {description:40} '{date_str:20}' -> {parsed.strftime('%Y-%m-%d %A')}")
            passed += 1
        except ValueError as e:
            print(f"❌ {description:40} '{date_str:20}' -> ERROR: {e}")
            failed += 1

    print("\n" + "="*70)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*70 + "\n")

    return failed == 0

if __name__ == "__main__":
    success = test_date_formats()
    exit(0 if success else 1)
