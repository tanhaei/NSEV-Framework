# src/main.py
import sys
from core.refinement import RefinementEngine
from solvers.z3_bridge import Z3Bridge
# Assume an LLM interface is defined to handle Phases 1-5 & 7
from core.llm_client import NSEV_LLM_Client 

def run_nsev_pipeline(original_code, mutant_code):
    """
    Orchestrates the 8-phase verification pipeline.
    """
    # Initialize components
    llm = NSEV_LLM_Client()
    bridge = Z3Bridge()
    refiner = RefinementEngine(max_budget=5) # Phase 8: Adaptive Budget
    
    # Phase 1: Initial Semantic Lifting & Ensemble Prompting
    # This combines analysis from Phases 2-5 and 7 into a prompt
    current_prompt = llm.generate_initial_prompt(original_code, mutant_code)
    
    print("--- Starting NSEV Neuro-Symbolic Pipeline ---")
    
    while not refiner.is_budget_exceeded():
        print(f"Attempt {refiner.current_attempt + 1}: Generating Formal Specifications...")
        
        # Phases 1-5 & 7: LLM generates the Z3 Python script components
        # (Invariants, Function Summaries, and Path Conditions)
        formal_spec = llm.query_model(current_prompt)
        
        try:
            # Phase 6: Formal Bridge & VC Generation
            # Translate the specs into a Verification Condition
            verdict, model = bridge.verify(formal_spec)
            
            if verdict == "unsat":
                return "✅ VERDICT: EQUIVALENT (Mathematically Proven)"
            
            # Phase 8: If SAT, a counter-example exists or invariant is weak
            print("Z3 result: SAT. Triggering Refinement Loop...")
            current_prompt = refiner.analyze_z3_feedback(solver_status="sat", model=model)
            
        except Exception as e:
            # Phase 8.1: Syntax-Level Refinement
            print(f"Z3 Error detected: {e}. Attempting self-correction...")
            current_prompt = refiner.analyze_z3_feedback(solver_status="error", error_log=str(e))
            
        if not current_prompt:
            break

    return "❌ VERDICT: INDETERMINATE (Refinement budget exceeded or Non-equivalent)"

if __name__ == "__main__":
    # Example usage
    with open("benchmarks/parity_check.py", "r") as f:
        code = f.read()
    
    # In a real scenario, you'd separate original and mutant
    result = run_nsev_pipeline(code, code) 
    print(result)
