# src/main.py
import argparse
import sys
import os

# اضافه کردن مسیر جاری به sys.path برای اطمینان از شناسایی پکیج‌ها
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Clean Imports با استفاده از فایل‌های __init__.py ایجاد شده
from core import CodeAnalyzer, NSEV_LLM_Client, RefinementEngine
from solvers.z3_bridge import Z3Bridge

def run_nsev_pipeline(orig_path, mut_path):
    """
    اجرای کامل خط لوله NSEV بر اساس معماری ارائه شده در فایل arch.pdf.
    """
    # بارگذاری کدها
    with open(orig_path, 'r') as f: orig_code = f.read()
    with open(mut_path, 'r') as f: mut_code = f.read()

    # ۱. تحلیل ساختاری (Phases 2-5 & 7)
    analyzer = CodeAnalyzer(orig_code)
    metadata = analyzer.analyze()
    print(f"[*] Structural analysis complete: {len(metadata['loops'])} loops detected.")

    # ۲. آماده‌سازی اجزای هوشمند و صوری
    llm = NSEV_LLM_Client()
    bridge = Z3Bridge()
    refiner = RefinementEngine(max_budget=5)

    # ۳. شروع فاز ۱ (Semantic Lifting)
    # در صورت وجود حلقه‌های تو در تو، استراتژی فاز ۳ فعال می‌شود
    if len(metadata['loops']) > 1:
        current_prompt = llm.generate_nested_loop_prompt(metadata['loops'], orig_code)
    else:
        current_prompt = llm.generate_initial_prompt(orig_code, mut_code)

    print("--- Starting Neuro-Symbolic Verification Loop ---")

    # ۴. حلقه اصلی تایید و پالایش (Phases 6 & 8)
    while not refiner.is_budget_exceeded():
        print(f"[Attempt {refiner.current_attempt + 1}] Generating formal spec...")
        
        # Phases 1-5: دریافت مشخصات صوری از مدل زبانی
        formal_spec = llm.query_model(current_prompt)
        
        # Phase 6: اجرای پل صوری و دریافت نتیجه از Z3
        status, data = bridge.verify(formal_spec)
        
        if status == "unsat":
            print("✅ VERDICT: EQUIVALENT (Mathematically Proven)")
            return
        
        # Phase 8: تحلیل بازخورد و شروع حلقه خوداصلاحی
        error_log = data if status == "error" else None
        model = data if status == "sat" else None
        
        current_prompt = refiner.analyze_z3_feedback(status, model=model, error_log=error_log)
        
        if not current_prompt:
            break
            
        print(f"[!] Refinement triggered due to: {status}")

    print("❌ VERDICT: INDETERMINATE (Budget exceeded or non-equivalence found)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NSEV: Neuro-Symbolic Equivalence Verifier")
    parser.add_argument("--original", required=True, help="Path to original python file")
    parser.add_argument("--mutant", required=True, help="Path to mutant python file")
    
    args = parser.parse_args()
    run_nsev_pipeline(args.original, args.mutant)