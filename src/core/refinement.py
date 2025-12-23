# src/core/refinement.py
import re

class RefinementEngine:
    """
    Implements Phase 8: Automated Refinement and Self-Correction Loop.
    This module bridges the gap between SMT solver feedback and LLM reasoning
    to ensure the soundness of the generated formal specifications.
    """
    
    def __init__(self, max_budget=3):
        """
        Initialize the refinement engine with a dynamic budget.
        
        Args:
            max_budget (int): Maximum number of correction attempts per mutant.
        """
        self.max_budget = max_budget
        self.current_attempt = 0

    def analyze_z3_feedback(self, solver_status, model=None, error_log=None):
        """
        Analyzes Z3 output to decide if the refinement loop should be triggered.
        
        Args:
            solver_status (str): The result from Z3 (sat, unsat, or unknown).
            model: The counter-example model if status is 'sat'.
            error_log (str): The raw error message if a syntax failure occurred.
            
        Returns:
            str: A refinement prompt for the LLM, or None if the proof is finalized.
        """
        # Phase 8.1: Syntax-Level Refinement
        # Handles Z3 parsing errors or invalid SMT-Lib operators
        if error_log:
            self.current_attempt += 1
            return self._generate_syntax_feedback(error_log)
        
        # Phase 8.2: Semantic Invariant Strengthening (CEGAR)
        # Triggered when Z3 finds a counter-example that might be impossible in real code
        if solver_status == "sat" and model is not None:
            self.current_attempt += 1
            return self._generate_cegar_feedback(model)
            
        # If status is 'unknown', the invariant might be outside Z3's decidable fragment
        if solver_status == "unknown":
            self.current_attempt += 1
            return "Z3 returned UNKNOWN. Please simplify the invariant logic."

        return None

    def _generate_syntax_feedback(self, error):
        """Formats an error message for the LLM to fix Z3 API calls."""
        return (
            f"REFINE_PROMPT: A Z3 Syntax/Type Error occurred: {str(error)}. "
            "Please review the SMT-Lib 2.0 mapping and ensure all variables "
            "are declared before use with correct sorts."
        )

    def _generate_cegar_feedback(self, model):
        """Formats a counter-example guided feedback to strengthen invariants."""
        # Represents the state where the formal proof failed
        counter_example = str(model)
        return (
            f"REFINE_PROMPT: The proof failed with counter-example: {counter_example}. "
            "The proposed invariant is too weak. Please strengthen it by adding "
            "constraints that exclude this unreachable state while maintaining induction."
        )

    def is_budget_exceeded(self):
        """Checks if the refinement loop has reached its maximum attempts."""
        return self.current_attempt >= self.max_budget
