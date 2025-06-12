import openpyxl
from openpyxl import Workbook
import os
from datetime import datetime


class MetricsLogger:
    def __init__(self, filename="metrics_log.xlsx"):
        self.filename = filename
        self.metrics = {}
        self.init_file()

    def init_file(self):
        if not os.path.exists(self.filename):
            wb = Workbook()
            ws = wb.active
            ws.append(["Timestamp", "Metric", "Value"])
            wb.save(self.filename)

    def mark_event(self, name, timestamp=None):
        self.metrics[name] = timestamp or datetime.now().timestamp()

    def log_metric(self, name, value):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        wb = openpyxl.load_workbook(self.filename)
        ws = wb.active
        ws.append([timestamp, name, value])
        wb.save(self.filename)

    def log_summary(self):
        self.log_metric("Summary", str(self.metrics))

