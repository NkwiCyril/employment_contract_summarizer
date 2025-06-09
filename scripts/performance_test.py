# Performance testing script
# scripts/performance_test.py
"""
Performance testing for the employment contract system
"""

import time
import requests
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor
import json
from create_sample_data import create_sample_contracts, create_sample_files

class PerformanceTest:
    def __init__(self, base_url='http://localhost:5000/api'):
        self.base_url = base_url
        self.results = []
    
    def time_request(self, func, *args, **kwargs):
        """Time a request and return duration"""
        start_time = time.time()
        try:
            response = func(*args, **kwargs)
            duration = time.time() - start_time
            success = response.status_code < 400
            return duration, success, response.status_code
        except Exception as e:
            duration = time.time() - start_time
            return duration, False, str(e)
    
    def test_contract_upload(self, num_requests=10):
        """Test contract upload performance"""
        print(f"Testing contract upload with {num_requests} requests...")
        
        def upload_contract():
            files = {'file': ('test.pdf', b'sample content', 'application/pdf')}
            data = {'user_id': '1'}
            
            duration, success, status = self.time_request(
                requests.post,
                f'{self.base_url}/contracts/upload',
                files=files,
                data=data
            )
            return duration, success, status
        
        # Run tests concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(upload_contract) for _ in range(num_requests)]
            results = [future.result() for future in futures]
        
        durations = [r[0] for r in results]
        successes = [r[1] for r in results]
        
        print(f"Upload Performance Results:")
        print(f"  Average time: {statistics.mean(durations):.2f}s")
        print(f"  Min time: {min(durations):.2f}s")
        print(f"  Max time: {max(durations):.2f}s")
        print(f"  Success rate: {sum(successes)/len(successes)*100:.1f}%")
        
        return results
    
    def test_summary_generation(self, contract_ids, num_requests=5):
        """Test summary generation performance"""
        print(f"Testing summary generation with {num_requests} requests...")
        
        def generate_summary(contract_id):
            duration, success, status = self.time_request(
                requests.post,
                f'{self.base_url}/summaries/generate/{contract_id}',
                json={'type': 'standard'}
            )
            return duration, success, status
        
        results = []
        for contract_id in contract_ids[:num_requests]:
            result = generate_summary(contract_id)
            results.append(result)
            time.sleep(1)  # Avoid overwhelming the server
        
        durations = [r[0] for r in results]
        successes = [r[1] for r in results]
        
        print(f"Summary Generation Performance Results:")
        print(f"  Average time: {statistics.mean(durations):.2f}s")
        print(f"  Min time: {min(durations):.2f}s")
        print(f"  Max time: {max(durations):.2f}s")
        print(f"  Success rate: {sum(successes)/len(successes)*100:.1f}%")
        
        return results

def run_performance_tests():
    """Run all performance tests"""
    tester = PerformanceTest()
    
    print("Starting Performance Tests...")
    print("=" * 50)
    
    # Test uploads
    upload_results = tester.test_contract_upload(10)
    
    print("\n" + "=" * 50)
    
    # Test summary generation (assuming some contracts exist)
    summary_results = tester.test_summary_generation([1, 2, 3], 3)
    
    print("\nPerformance testing completed!")

if __name__ == '__main__':
    # Choose what to run
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'sample':
            create_sample_contracts()
            create_sample_files()
        elif sys.argv[1] == 'test':
            run_performance_tests()
    else:
        print("Usage:")
        print("  python create_sample_data.py sample  # Create sample data")
        print("  python create_sample_data.py test    # Run performance tests")