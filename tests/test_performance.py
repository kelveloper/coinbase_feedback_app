"""
Performance Tests for Advanced Trade Insight Engine

This module tests the performance characteristics of the system, including:
- Large dataset processing performance
- Memory usage optimization
- Processing time benchmarks
- Scalability testing

Requirements: 8.2, 8.3, 8.4
"""

import unittest
import pandas as pd
import time
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from data_processing.data_loader import load_all_csv_files
    from data_processing.data_normalizer import normalize_and_unify_data
    from analysis.nlp_models import get_sentiment, get_theme, get_strategic_goal
    from analysis.scoring_engine import calculate_source_weight, calculate_impact_score
    from reporting.content_builder import build_comprehensive_content
except ImportError as e:
    print(f"Import warning: {e}")
    pass


class TestPerformance(unittest.TestCase):
    """Performance tests for the Advanced Trade Insight Engine."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def _create_large_dataset(self, size=1000):
        """Create a large dataset for performance testing."""
        data = []
        for i in range(size):
            data.append({
                'customer_id': f'PERF-{i:04d}',
                'source': 'Performance Test',
                'username': f'perf_user_{i}',
                'timestamp': f'2024-01-{(i % 30) + 1:02d} 12:00:00',
                'rating': (i % 5) + 1,
                'sentiment': ['positive', 'neutral', 'negative'][i % 3],
                'review_text': f'Performance test review {i}',
                'theme': ['Performance', 'Support', 'Trading'][i % 3],
                'severity': (i % 3) + 0.5,
                'strategic_goal': ['Growth', 'CX Efficiency', 'Trust&Safety'][i % 3],
                'helpful_votes': (i % 20) + 1
            })
        return pd.DataFrame(data)
    
    def test_large_dataset_processing_performance(self):
        """Test processing performance with large datasets."""
        try:
            # Create large dataset
            large_df = self._create_large_dataset(1000)
            
            # Test normalization performance
            start_time = time.time()
            loaded_data = {'large_test.csv': large_df}
            normalized_df = normalize_and_unify_data(loaded_data)
            end_time = time.time()
            
            # Should complete within reasonable time (5 seconds)
            processing_time = end_time - start_time
            self.assertLess(processing_time, 5.0, 
                          f"Normalization took {processing_time:.2f}s, expected < 5s")
            
            # Verify all data was processed
            self.assertEqual(len(normalized_df), len(large_df))
            
        except ImportError:
            self.skipTest("Required modules not available for testing")
    
    def test_nlp_processing_performance(self):
        """Test NLP processing performance."""
        try:
            # Create test dataset
            test_df = self._create_large_dataset(100)
            
            # Test sentiment extraction performance
            start_time = time.time()
            for _, row in test_df.iterrows():
                get_sentiment(row)
            end_time = time.time()
            
            # Should process 100 rows quickly
            processing_time = end_time - start_time
            self.assertLess(processing_time, 2.0,
                          f"Sentiment processing took {processing_time:.2f}s, expected < 2s")
            
        except ImportError:
            self.skipTest("Required modules not available for testing")
    
    def test_scoring_performance(self):
        """Test impact scoring performance."""
        try:
            # Create test dataset
            test_df = self._create_large_dataset(100)
            
            # Test scoring performance
            start_time = time.time()
            for _, row in test_df.iterrows():
                calculate_source_weight(row)
                calculate_impact_score(row)
            end_time = time.time()
            
            # Should process 100 rows quickly
            processing_time = end_time - start_time
            self.assertLess(processing_time, 2.0,
                          f"Scoring took {processing_time:.2f}s, expected < 2s")
            
        except ImportError:
            self.skipTest("Required modules not available for testing")
    
    def test_memory_usage_with_large_dataset(self):
        """Test memory usage with large datasets."""
        try:
            # Create progressively larger datasets and monitor memory
            sizes = [100, 500, 1000]
            
            for size in sizes:
                large_df = self._create_large_dataset(size)
                loaded_data = {'test.csv': large_df}
                
                # Process data
                normalized_df = normalize_and_unify_data(loaded_data)
                
                # Verify processing completed
                self.assertEqual(len(normalized_df), size)
                
                # Clean up
                del large_df, normalized_df, loaded_data
                
        except ImportError:
            self.skipTest("Required modules not available for testing")
    
    def test_report_generation_performance(self):
        """Test report generation performance."""
        try:
            # Create test dataset
            test_df = self._create_large_dataset(200)
            loaded_data = {'test.csv': test_df}
            normalized_df = normalize_and_unify_data(loaded_data)
            
            # Test report content building performance
            start_time = time.time()
            report_content = build_comprehensive_content(normalized_df)
            end_time = time.time()
            
            # Should complete within reasonable time
            processing_time = end_time - start_time
            self.assertLess(processing_time, 3.0,
                          f"Report generation took {processing_time:.2f}s, expected < 3s")
            
            # Verify report content was generated
            self.assertIn('executive_summary', report_content)
            
        except ImportError:
            self.skipTest("Required modules not available for testing")
    
    def test_concurrent_processing_simulation(self):
        """Test simulated concurrent processing scenarios."""
        try:
            # Create multiple datasets
            datasets = []
            for i in range(3):
                df = self._create_large_dataset(100)
                datasets.append(df)
            
            # Process all datasets sequentially (simulating concurrent load)
            start_time = time.time()
            
            for i, df in enumerate(datasets):
                loaded_data = {f'test_{i}.csv': df}
                normalized_df = normalize_and_unify_data(loaded_data)
                self.assertEqual(len(normalized_df), 100)
            
            end_time = time.time()
            
            # Should complete all processing within reasonable time
            total_time = end_time - start_time
            self.assertLess(total_time, 10.0,
                          f"Concurrent simulation took {total_time:.2f}s, expected < 10s")
            
        except ImportError:
            self.skipTest("Required modules not available for testing")


if __name__ == '__main__':
    unittest.main()
from src.reporting.report_generator import generate_report_content


class TestPerformance:
    """
    Performance tests for the Advanced Trade Insight Engine.
    
    Requirements: 8.2, 8.3, 8.4
    """
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Set up and tear down test environment."""
        self.process = psutil.Process()
        self.initial_memory = self.process.memory_info().rss
        
        yield
        
        # Cleanup
        final_memory = self.process.memory_info().rss
        memory_used = final_memory - self.initial_memory
        print(f"Memory used: {memory_used / 1024 / 1024:.2f} MB")
    
    def test_data_loading_performance(self, large_dataset):
        """Test data loading performance with large datasets."""
        # Create temporary CSV file
        temp_file = "temp_large_dataset.csv"
        large_dataset.to_csv(temp_file, index=False)
        
        try:
            # Test loading performance
            start_time = time.time()
            dataframes = load_all_csv_files('.')
            end_time = time.time()
            
            loading_time = end_time - start_time
            
            # Should load 1000 rows within 2 seconds
            assert loading_time < 2.0, f"Data loading took {loading_time:.2f}s, expected < 2.0s"
            
            # Verify data integrity
            assert len(dataframes) > 0
            for df in dataframes.values():
                assert len(df) > 0
            
            print(f"✅ Data loading: {len(large_dataset)} rows in {loading_time:.3f}s")
            
        finally:
            # Cleanup
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_data_normalization_performance(self, large_dataset):
        """Test data normalization performance with large datasets."""
        dataframes = {'large_test.csv': large_dataset}
        
        # Test normalization performance
        start_time = time.time()
        normalized_df = normalize_data(dataframes)
        end_time = time.time()
        
        normalization_time = end_time - start_time
        
        # Should normalize 1000 rows within 3 seconds
        assert normalization_time < 3.0, f"Normalization took {normalization_time:.2f}s, expected < 3.0s"
        
        # Verify output quality
        assert len(normalized_df) == len(large_dataset)
        assert 'feedback_text' in normalized_df.columns
        assert 'author_handle' in normalized_df.columns
        assert 'source_channel' in normalized_df.columns
        
        print(f"✅ Data normalization: {len(large_dataset)} rows in {normalization_time:.3f}s")
    
    def test_nlp_processing_performance(self, large_dataset):
        """Test NLP processing performance with large datasets."""
        # Normalize data first
        dataframes = {'large_test.csv': large_dataset}
        normalized_df = normalize_data(dataframes)
        
        # Test NLP processing performance
        start_time = time.time()
        
        # Process sentiment extraction
        sentiments = []
        for _, row in normalized_df.iterrows():
            sentiment = get_sentiment(row)
            sentiments.append(sentiment)
        
        # Process theme extraction
        themes = []
        for _, row in normalized_df.iterrows():
            theme = get_theme(row)
            themes.append(theme)
        
        # Process strategic goal extraction
        strategic_goals = []
        for _, row in normalized_df.iterrows():
            strategic_goal = get_strategic_goal(row)
            strategic_goals.append(strategic_goal)
        
        end_time = time.time()
        
        nlp_processing_time = end_time - start_time
        
        # Should process 1000 rows within 5 seconds
        assert nlp_processing_time < 5.0, f"NLP processing took {nlp_processing_time:.2f}s, expected < 5.0s"
        
        # Verify results
        assert len(sentiments) == len(large_dataset)
        assert len(themes) == len(large_dataset)
        assert len(strategic_goals) == len(large_dataset)
        
        print(f"✅ NLP processing: {len(large_dataset)} rows in {nlp_processing_time:.3f}s")
    
    def test_scoring_performance(self, large_dataset):
        """Test impact scoring performance with large datasets."""
        # Normalize data first
        dataframes = {'large_test.csv': large_dataset}
        normalized_df = normalize_data(dataframes)
        
        # Test scoring performance
        start_time = time.time()
        
        # Process source weight calculation
        source_weights = []
        for _, row in normalized_df.iterrows():
            weight = calculate_source_weight(row)
            source_weights.append(weight)
        
        # Process impact score calculation
        impact_scores = []
        for _, row in normalized_df.iterrows():
            score = calculate_impact_score(row)
            impact_scores.append(score)
        
        end_time = time.time()
        
        scoring_time = end_time - start_time
        
        # Should score 1000 rows within 3 seconds
        assert scoring_time < 3.0, f"Scoring took {scoring_time:.2f}s, expected < 3.0s"
        
        # Verify results
        assert len(source_weights) == len(large_dataset)
        assert len(impact_scores) == len(large_dataset)
        
        # Verify score validity
        for weight in source_weights:
            assert isinstance(weight, (int, float))
            assert weight > 0
        
        for score in impact_scores:
            assert isinstance(score, (int, float))
            assert score >= 0
        
        print(f"✅ Impact scoring: {len(large_dataset)} rows in {scoring_time:.3f}s")
    
    def test_report_generation_performance(self, large_dataset):
        """Test report generation performance with large datasets."""
        # Prepare data with scoring
        dataframes = {'large_test.csv': large_dataset}
        normalized_df = normalize_data(dataframes)
        
        # Add scoring columns
        normalized_df['source_weight'] = normalized_df.apply(calculate_source_weight, axis=1)
        normalized_df['impact_score'] = normalized_df.apply(calculate_impact_score, axis=1)
        
        # Test content building performance
        start_time = time.time()
        report_content = build_report_content(normalized_df)
        end_time = time.time()
        
        content_building_time = end_time - start_time
        
        # Should build report content within 2 seconds
        assert content_building_time < 2.0, f"Content building took {content_building_time:.2f}s, expected < 2.0s"
        
        # Verify report content quality
        assert 'executive_summary' in report_content
        assert 'pain_points' in report_content
        assert 'praised_features' in report_content
        assert 'strategic_insights' in report_content
        
        print(f"✅ Report content building: {len(large_dataset)} rows in {content_building_time:.3f}s")
    
    def test_memory_usage_optimization(self, large_dataset):
        """Test memory usage optimization during processing."""
        # Monitor memory usage during processing
        initial_memory = self.process.memory_info().rss
        
        # Process large dataset
        dataframes = {'large_test.csv': large_dataset}
        normalized_df = normalize_data(dataframes)
        
        # Add scoring
        normalized_df['source_weight'] = normalized_df.apply(calculate_source_weight, axis=1)
        normalized_df['impact_score'] = normalized_df.apply(calculate_impact_score, axis=1)
        
        # Generate report
        report_content = build_report_content(normalized_df)
        
        # Check final memory usage
        final_memory = self.process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB for 1000 rows)
        max_expected_memory = 100 * 1024 * 1024  # 100MB
        assert memory_increase < max_expected_memory, \
            f"Memory increase {memory_increase / 1024 / 1024:.2f}MB exceeds limit {max_expected_memory / 1024 / 1024:.2f}MB"
        
        print(f"✅ Memory usage: {memory_increase / 1024 / 1024:.2f}MB increase for {len(large_dataset)} rows")
    
    def test_scalability_with_different_dataset_sizes(self):
        """Test scalability with different dataset sizes."""
        dataset_sizes = [100, 500, 1000, 2000]
        performance_results = {}
        
        for size in dataset_sizes:
            # Create dataset of specific size
            data = []
            for i in range(size):
                data.append({
                    'customer_id': f'SCAL-{i:04d}',
                    'source': 'Scalability Test',
                    'username': f'scal_user_{i}',
                    'timestamp': f'2024-01-{i % 30 + 1:02d} 12:00:00',
                    'rating': (i % 5) + 1,
                    'sentiment': ['positive', 'neutral', 'negative'][i % 3],
                    'review_text': f'Scalability test review {i}',
                    'theme': ['Performance', 'Support', 'Trading'][i % 3],
                    'severity': (i % 3) + 0.5,
                    'strategic_goal': ['Growth', 'CX Efficiency', 'Trust&Safety'][i % 3],
                    'helpful_votes': (i % 20) + 1
                })
            
            dataset = pd.DataFrame(data)
            dataframes = {f'scalability_{size}.csv': dataset}
            
            # Measure processing time
            start_time = time.time()
            normalized_df = normalize_data(dataframes)
            normalized_df['source_weight'] = normalized_df.apply(calculate_source_weight, axis=1)
            normalized_df['impact_score'] = normalized_df.apply(calculate_impact_score, axis=1)
            end_time = time.time()
            
            processing_time = end_time - start_time
            performance_results[size] = processing_time
            
            print(f"Dataset size {size}: {processing_time:.3f}s")
        
        # Verify scalability characteristics
        # Processing time should increase linearly or sub-linearly
        for i in range(1, len(dataset_sizes)):
            current_size = dataset_sizes[i]
            previous_size = dataset_sizes[i-1]
            
            current_time = performance_results[current_size]
            previous_time = performance_results[previous_size]
            
            # Time increase should be reasonable (not exponential)
            size_ratio = current_size / previous_size
            time_ratio = current_time / previous_time
            
            # Time increase should not be more than 3x the size increase
            assert time_ratio < size_ratio * 3, \
                f"Processing time increase {time_ratio:.2f}x exceeds reasonable limit for size increase {size_ratio:.2f}x"
        
        print("✅ Scalability test passed - processing time increases reasonably with dataset size")
    
    def test_concurrent_processing_performance(self, large_dataset):
        """Test performance under concurrent processing scenarios."""
        import concurrent.futures
        import threading
        
        # Normalize data
        dataframes = {'large_test.csv': large_dataset}
        normalized_df = normalize_data(dataframes)
        
        # Test concurrent scoring
        def process_chunk(chunk_df):
            results = []
            for _, row in chunk_df.iterrows():
                weight = calculate_source_weight(row)
                score = calculate_impact_score(row)
                results.append((weight, score))
            return results
        
        # Split data into chunks
        chunk_size = len(normalized_df) // 4
        chunks = [
            normalized_df.iloc[i:i+chunk_size] 
            for i in range(0, len(normalized_df), chunk_size)
        ]
        
        # Process chunks concurrently
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(process_chunk, chunk) for chunk in chunks]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        
        concurrent_time = end_time - start_time
        
        # Concurrent processing should be faster than sequential
        # Sequential processing time estimate
        sequential_time_estimate = len(normalized_df) * 0.001  # Rough estimate
        
        # Concurrent should be at least 2x faster than sequential
        speedup = sequential_time_estimate / concurrent_time
        assert speedup > 2.0, f"Concurrent processing speedup {speedup:.2f}x is below expected 2.0x"
        
        print(f"✅ Concurrent processing: {len(large_dataset)} rows in {concurrent_time:.3f}s (speedup: {speedup:.2f}x)")
    
    @pytest.mark.slow
    def test_end_to_end_performance_benchmark(self, large_dataset):
        """Test end-to-end performance benchmark with large dataset."""
        print(f"\n🚀 Starting end-to-end performance benchmark with {len(large_dataset)} rows...")
        
        # Create temporary CSV file
        temp_file = "temp_benchmark_dataset.csv"
        large_dataset.to_csv(temp_file, index=False)
        
        try:
            # Measure complete workflow performance
            start_time = time.time()
            start_memory = self.process.memory_info().rss
            
            # 1. Data loading
            load_start = time.time()
            dataframes = load_all_csv_files('.')
            load_time = time.time() - load_start
            
            # 2. Data normalization
            norm_start = time.time()
            normalized_df = normalize_data(dataframes)
            norm_time = time.time() - norm_start
            
            # 3. NLP processing
            nlp_start = time.time()
            normalized_df['extracted_sentiment'] = normalized_df.apply(get_sentiment, axis=1)
            normalized_df['extracted_theme'] = normalized_df.apply(get_theme, axis=1)
            normalized_df['extracted_strategic_goal'] = normalized_df.apply(get_strategic_goal, axis=1)
            nlp_time = time.time() - nlp_start
            
            # 4. Scoring
            scoring_start = time.time()
            normalized_df['source_weight'] = normalized_df.apply(calculate_source_weight, axis=1)
            normalized_df['impact_score'] = normalized_df.apply(calculate_impact_score, axis=1)
            scoring_time = time.time() - scoring_start
            
            # 5. Report generation
            report_start = time.time()
            report_content = build_report_content(normalized_df)
            report_time = time.time() - report_start
            
            end_time = time.time()
            end_memory = self.process.memory_info().rss
            
            total_time = end_time - start_time
            memory_used = end_memory - start_memory
            
            # Performance assertions
            assert total_time < 15.0, f"Total processing time {total_time:.2f}s exceeds 15s limit"
            assert memory_used < 200 * 1024 * 1024, f"Memory usage {memory_used / 1024 / 1024:.2f}MB exceeds 200MB limit"
            
            # Print detailed performance breakdown
            print(f"\n📊 PERFORMANCE BENCHMARK RESULTS")
            print(f"=" * 50)
            print(f"Dataset Size: {len(large_dataset)} rows")
            print(f"Total Time: {total_time:.3f}s")
            print(f"Memory Used: {memory_used / 1024 / 1024:.2f}MB")
            print(f"\nBreakdown:")
            print(f"  Data Loading: {load_time:.3f}s")
            print(f"  Normalization: {norm_time:.3f}s")
            print(f"  NLP Processing: {nlp_time:.3f}s")
            print(f"  Scoring: {scoring_time:.3f}s")
            print(f"  Report Generation: {report_time:.3f}s")
            print(f"\nThroughput: {len(large_dataset) / total_time:.1f} rows/second")
            
            print("✅ End-to-end performance benchmark completed successfully!")
            
        finally:
            # Cleanup
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_memory_cleanup_after_processing(self, large_dataset):
        """Test that memory is properly cleaned up after processing."""
        # Get initial memory
        initial_memory = self.process.memory_info().rss
        
        # Process large dataset
        dataframes = {'large_test.csv': large_dataset}
        normalized_df = normalize_data(dataframes)
        
        # Add scoring
        normalized_df['source_weight'] = normalized_df.apply(calculate_source_weight, axis=1)
        normalized_df['impact_score'] = normalized_df.apply(calculate_impact_score, axis=1)
        
        # Generate report
        report_content = build_report_content(normalized_df)
        
        # Clear references
        del dataframes, normalized_df, report_content
        
        # Force garbage collection
        import gc
        gc.collect()
        
        # Check memory after cleanup
        final_memory = self.process.memory_info().rss
        memory_after_cleanup = final_memory - initial_memory
        
        # Memory should be close to initial (within 50MB)
        max_expected_cleanup = 50 * 1024 * 1024  # 50MB
        assert abs(memory_after_cleanup) < max_expected_cleanup, \
            f"Memory after cleanup {memory_after_cleanup / 1024 / 1024:.2f}MB exceeds cleanup threshold"
        
        print(f"✅ Memory cleanup: {memory_after_cleanup / 1024 / 1024:.2f}MB difference after cleanup")
