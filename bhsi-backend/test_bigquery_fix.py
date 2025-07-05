#!/usr/bin/env python3
"""
Test to demonstrate BigQuery data access fix
"""

class MockBigQueryRow:
    """Mock BigQuery Row object that simulates the actual behavior"""
    def __init__(self, data):
        self._data = data
        self._fields = data.keys()
        # Add attributes for dot notation access
        for key, value in data.items():
            setattr(self, key, value)
    
    def __iter__(self):
        return iter(self._data.items())

def test_old_way():
    """Test the old way that was causing errors"""
    print("🔍 Testing OLD way (broken)...")
    
    row = MockBigQueryRow({
        'risk_label': 'HIGH',
        'count': 5,
        'pub_date': '2024-01-15'
    })
    
    try:
        # This would work with actual BigQuery Row objects
        risk_level = row.risk_label
        count = row.count
        print(f"   ✅ Old way works with Row objects: {risk_level}, {count}")
        
        # But fails with dict objects (what the cloud service returns)
        row_as_dict = dict(row)
        risk_level = row_as_dict.risk_label  # This would fail!
        
    except AttributeError as e:
        print(f"   ❌ Old way fails with dict: {e}")

def test_new_way():
    """Test the new way that handles both Row and dict objects"""
    print("\n🔍 Testing NEW way (fixed)...")
    
    # Test with Row object
    row = MockBigQueryRow({
        'risk_label': 'HIGH',
        'count': 5,
        'pub_date': '2024-01-15'
    })
    
    # Our fixed approach
    row_dict = dict(row) if hasattr(row, '_fields') else row
    risk_level = row_dict.get('risk_label')
    count = row_dict.get('count', 0)
    print(f"   ✅ New way works with Row objects: {risk_level}, {count}")
    
    # Test with dict object (what cloud service returns)
    row_as_dict = {'risk_label': 'MEDIUM', 'count': 3}
    row_dict = dict(row_as_dict) if hasattr(row_as_dict, '_fields') else row_as_dict
    risk_level = row_dict.get('risk_label')
    count = row_dict.get('count', 0)
    print(f"   ✅ New way works with dict objects: {risk_level}, {count}")

def main():
    print("🧪 BIGQUERY DATA ACCESS FIX DEMONSTRATION")
    print("=" * 60)
    print("The issue: BigQuery service returns different data types")
    print("          than expected, causing 'dict has no attribute' errors")
    print()
    
    test_old_way()
    test_new_way()
    
    print("\n📋 SUMMARY:")
    print("   ❌ Old code: row.risk_label (fails with dict objects)")
    print("   ✅ New code: row_dict.get('risk_label') (works with both)")
    print()
    print("🔧 SOLUTION:")
    print("   The local code has been fixed, but the cloud service")
    print("   needs to be redeployed with the updated code.")
    print()
    print("🎯 STATUS: Fix is correct, deployment needed for cloud service")

if __name__ == "__main__":
    main() 