import pandas as pd
import time
from datetime import datetime
import os
from typing import Dict, Any


class MetricsLogger:
    def __init__(self, excel_file: str = "metrics_log.xlsx"):
        self.excel_file = excel_file
        self.metrics = {}
        self.events = {}
        self.session_id = self._generate_session_id()

    def _generate_session_id(self) -> str:
        """Generate a unique session ID based on timestamp"""
        return f"session_{int(time.time())}"

    def mark_event(self, event_name: str, timestamp: float = None):
        """Mark an event with timestamp"""
        if timestamp is None:
            timestamp = time.time()
        self.events[event_name] = timestamp

    def log_metric(self, metric_name: str, value: float):
        """Log a metric value"""
        self.metrics[metric_name] = value

    def save_to_excel(self):
        """Save metrics to Excel file"""
        try:
            # Prepare data for Excel
            data = {
                'Session_ID': [self.session_id],
                'Timestamp': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                'EOU_delay': [self.metrics.get('EOU_delay', 0)],
                'TTFT': [self.metrics.get('TTFT', 0)],
                'TTFB': [self.metrics.get('TTFB', 0)],
                'Total_latency': [self.metrics.get('Total_latency', 0)],
                'TTS_duration': [self.metrics.get('TTS_duration', 0)],
                'Session_duration': [self.metrics.get('Session_duration', 0)]
            }

            # Create DataFrame
            new_df = pd.DataFrame(data)

            # Check if file exists and append, otherwise create new
            if os.path.exists(self.excel_file):
                try:
                    existing_df = pd.read_excel(self.excel_file)
                    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                except Exception as e:
                    print(f"Error reading existing Excel file: {e}")
                    combined_df = new_df
            else:
                combined_df = new_df

            # Save to Excel
            combined_df.to_excel(self.excel_file, index=False)
            print(f"Metrics saved to {self.excel_file}")

        except Exception as e:
            print(f"Error saving metrics to Excel: {e}")
            # Fallback: save as CSV
            try:
                csv_file = self.excel_file.replace('.xlsx', '.csv')
                new_df.to_csv(csv_file, mode='a', header=not os.path.exists(csv_file), index=False)
                print(f"Metrics saved to {csv_file} as fallback")
            except Exception as csv_error:
                print(f"Error saving to CSV fallback: {csv_error}")

    def log_summary(self):
        """Print a summary of logged metrics"""
        print("\n" + "=" * 50)
        print(f"SESSION METRICS SUMMARY - {self.session_id}")
        print("=" * 50)

        for metric, value in self.metrics.items():
            if 'delay' in metric.lower() or 'latency' in metric.lower() or 'duration' in metric.lower():
                print(f"{metric:<20}: {value:.3f}s ({value*1000:.1f}ms)")
            else:
                print(f"{metric:<20}: {value:.3f}")

        print("\nEVENT TIMESTAMPS:")
        for event, timestamp in self.events.items():
            print(f"{event:<20}: {datetime.fromtimestamp(timestamp).strftime('%H:%M:%S.%f')[:-3]}")

        print("=" * 50)

    def get_metrics(self) -> Dict[str, Any]:
        """Return current metrics dictionary"""
        return self.metrics.copy()

    def reset_metrics(self):
        """Reset all metrics for a new session"""
        self.metrics.clear()
        self.events.clear()
        self.session_id = self._generate_session_id()
