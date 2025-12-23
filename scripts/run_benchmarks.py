# scripts/run_benchmarks.py
import os
import sys
import time
from tabulate import tabulate # نیاز به نصب: pip install tabulate

# اضافه کردن مسیر src به پایتون
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from main import run_nsev_pipeline

def execute_suite():
    """
    اجرای خودکار بنچمارک‌ها و ارزیابی فازهای متدولوژی NSEV.
    """
    benchmarks = [
        {"name": "Parity Check (Bitwise)", "file": "parity_check.py", "category": "Phase 6: Logic"},
        {"name": "Matrix Sum (Nested)", "file": "matrix_sum.py", "category": "Phase 3: Hierarchical"},
        {"name": "Loop Optimization", "file": "math_opt.py", "category": "Phase 2: Induction"},
    ]

    results = []
    print("🚀 Starting NSEV Benchmark Execution...\n")

    for b in benchmarks:
        path = os.path.join("benchmarks", b["file"])
        if not os.path.exists(path):
            continue

        start_time = time.time()
        # اجرای خط لوله 8 مرحله‌ای
        # در اینجا فرض بر این است که فایل اصلی هر دو نسخه را شامل می‌شود یا مسیرها جدا هستند
        verdict = run_nsev_pipeline(path, path) 
        duration = time.time() - start_time

        results.append([
            b["name"],
            b["category"],
            verdict,
            f"{duration:.2f}s"
        ])

    # نمایش نتایج در قالب جدول مشابه جداول مقایسه‌ای مقالات علمی
    headers = ["Benchmark Name", "Focus Area", "Final Verdict", "Execution Time"]
    print("\n--- NSEV Experimental Results ---")
    print(tabulate(results, headers=headers, tablefmt="grid"))

if __name__ == "__main__":
    execute_suite()
