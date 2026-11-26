"""
Automata Simulator: NFA to DFA Conversion using Subset Construction
-------------------------------------------------------------------
Features:
- NFA with optional Epsilon (e / ε) transitions
- Epsilon-Closure computation
- Powerset / Subset Construction Algorithm
- Transition Table generation for both NFA and DFA
- Subset state mapping (e.g. {q0, q1} -> S0)
- DFA string simulation with step-by-step execution trace
- Automated test suite covering normal and edge cases
"""

from typing import Set, Dict, Tuple, List, FrozenSet


class NFA:
    def __init__(self, states: Set[str], alphabet: Set[str], 
                 transitions: Dict[Tuple[str, str], Set[str]], 
                 start_state: str, accept_states: Set[str]):
        self.states = sorted(list(states))
        self.alphabet = sorted(list(alphabet))
        self.transitions = transitions  # (state, symbol) -> set of states
        self.start_state = start_state
        self.accept_states = set(accept_states)
        self.epsilon_symbols = {"", "e", "E", "eps", "ε"}

    def get_transitions(self, state: str, symbol: str) -> Set[str]:
        return self.transitions.get((state, symbol), set())

    def epsilon_closure(self, states: Set[str]) -> FrozenSet[str]:
        """Calculates the epsilon-closure of a set of states."""
        closure = set(states)
        stack = list(states)

        while stack:
            curr = stack.pop()
            for eps in self.epsilon_symbols:
                for nxt in self.get_transitions(curr, eps):
                    if nxt not in closure:
                        closure.add(nxt)
                        stack.append(nxt)
        return frozenset(closure)


class DFA:
    def __init__(self, states: List[str], alphabet: List[str],
                 transitions: Dict[Tuple[str, str], str],
                 start_state: str, accept_states: Set[str],
                 subset_mapping: Dict[str, FrozenSet[str]]):
        self.states = states
        self.alphabet = sorted(list(alphabet))
        self.transitions = transitions  # (dfa_state, symbol) -> dfa_state
        self.start_state = start_state
        self.accept_states = set(accept_states)
        self.subset_mapping = subset_mapping  # S0 -> frozenset({q0, q1})

    def simulate(self, input_string: str) -> Tuple[bool, List[Tuple[str, str, str]]]:
        """
        Simulate an input string on the DFA.
        Returns:
            (is_accepted, trace_list)
            where trace_list is list of tuples: (current_state, symbol, next_state)
        """
        curr = self.start_state
        trace = []

        if input_string == "" or input_string in {"ε", "e"}:
            return (curr in self.accept_states, trace)

        for sym in input_string:
            if sym not in self.alphabet:
                trace.append((curr, sym, "ERROR: Invalid Symbol"))
                return (False, trace)

            nxt = self.transitions.get((curr, sym), None)
            if nxt is None:
                trace.append((curr, sym, "DEAD_STATE"))
                return (False, trace)

            trace.append((curr, sym, nxt))
            curr = nxt

        is_accepted = curr in self.accept_states
        return (is_accepted, trace)


def convert_nfa_to_dfa(nfa: NFA) -> DFA:
    """
    Implements Subset Construction (Powerset Construction) Algorithm.
    Converts given NFA to an equivalent DFA.
    """
    initial_closure = nfa.epsilon_closure({nfa.start_state})
    
    # Mapping from frozenset of NFA states -> DFA State Name (e.g. S0, S1, ...)
    subset_to_name: Dict[FrozenSet[str], str] = {initial_closure: "S0"}
    name_to_subset: Dict[str, FrozenSet[str]] = {"S0": initial_closure}
    
    unprocessed = [initial_closure]
    dfa_transitions: Dict[Tuple[str, str], str] = {}
    dfa_accept_states: Set[str] = set()
    state_counter = 1

    # Check if S0 is accept state
    if any(st in nfa.accept_states for st in initial_closure):
        dfa_accept_states.add("S0")

    while unprocessed:
        curr_subset = unprocessed.pop(0)
        curr_name = subset_to_name[curr_subset]

        for sym in nfa.alphabet:
            # 1. Compute direct transitions on symbol for all states in subset
            direct_next = set()
            for st in curr_subset:
                direct_next.update(nfa.get_transitions(st, sym))
            
            # 2. Compute epsilon closure of the resulting set
            target_subset = nfa.epsilon_closure(direct_next)

            # If target subset is empty, represent as trap / dead state or Φ
            if not target_subset:
                target_subset = frozenset()

            if target_subset not in subset_to_name:
                new_state_name = f"S{state_counter}" if target_subset else "DEAD"
                if target_subset:
                    state_counter += 1
                subset_to_name[target_subset] = new_state_name
                name_to_subset[new_state_name] = target_subset
                unprocessed.append(target_subset)

                # Check if this new DFA state is an accepting state
                if any(st in nfa.accept_states for st in target_subset):
                    dfa_accept_states.add(new_state_name)

            dest_name = subset_to_name[target_subset]
            dfa_transitions[(curr_name, sym)] = dest_name

    all_dfa_states = list(name_to_subset.keys())
    return DFA(
        states=all_dfa_states,
        alphabet=nfa.alphabet,
        transitions=dfa_transitions,
        start_state="S0",
        accept_states=dfa_accept_states,
        subset_mapping=name_to_subset
    )


def print_nfa_table(nfa: NFA):
    print("\n--- NFA Transition Table ---")
    headers = ["State"] + nfa.alphabet + ["ε"]
    col_w = 14
    header_str = " | ".join(h.center(col_w) for h in headers)
    print("=" * len(header_str))
    print(header_str)
    print("=" * len(header_str))

    for state in nfa.states:
        prefix = ""
        if state == nfa.start_state:
            prefix += "-> "
        if state in nfa.accept_states:
            prefix += "* "
        state_label = f"{prefix}{state}".center(col_w)

        row = [state_label]
        for sym in nfa.alphabet:
            nxt = nfa.get_transitions(state, sym)
            txt = "{" + ", ".join(sorted(nxt)) + "}" if nxt else "Φ"
            row.append(txt.center(col_w))
        
        # Epsilon column
        eps_nxt = set()
        for eps in nfa.epsilon_symbols:
            eps_nxt.update(nfa.get_transitions(state, eps))
        txt = "{" + ", ".join(sorted(eps_nxt)) + "}" if eps_nxt else "Φ"
        row.append(txt.center(col_w))

        print(" | ".join(row))
    print("=" * len(header_str))


def print_dfa_table(dfa: DFA):
    print("\n--- Converted DFA Transition Table & Subset Mappings ---")
    headers = ["DFA State", "NFA Subset Mapping"] + dfa.alphabet
    col_w = 16
    header_str = " | ".join(h.center(col_w) for h in headers)
    print("=" * len(header_str))
    print(header_str)
    print("=" * len(header_str))

    for state in dfa.states:
        prefix = ""
        if state == dfa.start_state:
            prefix += "-> "
        if state in dfa.accept_states:
            prefix += "* "
        state_label = f"{prefix}{state}".center(col_w)

        subset = dfa.subset_mapping.get(state, frozenset())
        subset_str = "{" + ", ".join(sorted(subset)) + "}" if subset else "Φ"
        row = [state_label, subset_str.center(col_w)]

        for sym in dfa.alphabet:
            dest = dfa.transitions.get((state, sym), "DEAD")
            row.append(dest.center(col_w))

        print(" | ".join(row))
    print("=" * len(header_str))
    print(f"Start State: {dfa.start_state}")
    print(f"Accept States: {sorted(list(dfa.accept_states))}")


def run_tests():
    """Automated demonstration suite for normal and edge test cases."""
    print("================================================================")
    print("          AUTOMATA SIMULATOR - NFA TO DFA DEMO")
    print("================================================================")

    # Example 1: NFA that accepts strings ending with '01'
    # Alphabet: {0, 1}
    # States: q0, q1, q2
    # Start: q0, Accept: q2
    # Transitions:
    # q0 -0-> {q0, q1}
    # q0 -1-> {q0}
    # q1 -1-> {q2}
    print("\n[TEST CASE 1] Normal Case: Language of strings ending with '01'")
    nfa1 = NFA(
        states={"q0", "q1", "q2"},
        alphabet={"0", "1"},
        transitions={
            ("q0", "0"): {"q0", "q1"},
            ("q0", "1"): {"q0"},
            ("q1", "1"): {"q2"}
        },
        start_state="q0",
        accept_states={"q2"}
    )
    print_nfa_table(nfa1)
    dfa1 = convert_nfa_to_dfa(nfa1)
    print_dfa_table(dfa1)

    test_inputs = [
        ("01", True, "Ends with '01' (Valid normal case)"),
        ("1001", True, "Ends with '01' with preceding characters"),
        ("11101", True, "Multiple 1s ending in '01'"),
        ("010", False, "Ends in '0', not '01' (Rejected)"),
        ("1111", False, "All 1s without '01' (Rejected)"),
        ("", False, "Empty string ε (Edge case: start is not accept)"),
        ("0", False, "Single symbol '0' (Edge case)"),
        ("1", False, "Single symbol '1' (Edge case)")
    ]

    print("\n--- String Simulation Results on Converted DFA ---")
    for s, expected, desc in test_inputs:
        accepted, trace = dfa1.simulate(s)
        status = "PASS" if accepted == expected else "FAIL"
        verdict = "ACCEPTED" if accepted else "REJECTED"
        s_display = f"'{s}'" if s else "ε (empty string)"
        
        # Path trace string
        if not trace:
            trace_str = f"Start at {dfa1.start_state}"
        else:
            trace_str = f"{dfa1.start_state} " + " ".join([f"--({sym})--> {nxt}" for _, sym, nxt in trace])
            
        print(f"[{status}] String: {s_display:20} -> Verdict: {verdict:8} | {desc}")
        print(f"       Trace: {trace_str}")

    # Example 2: NFA with Epsilon Transitions
    # Accepts string 'ab' with epsilon transitions
    print("\n\n[TEST CASE 2] Edge Case: NFA with Epsilon (ε) Transitions")
    nfa2 = NFA(
        states={"A", "B", "C"},
        alphabet={"a", "b"},
        transitions={
            ("A", "e"): {"B"},   # Epsilon transition A -> B
            ("B", "a"): {"B"},
            ("B", "b"): {"C"}
        },
        start_state="A",
        accept_states={"C"}
    )
    print_nfa_table(nfa2)
    dfa2 = convert_nfa_to_dfa(nfa2)
    print_dfa_table(dfa2)

    eps_tests = [
        ("b", True, "Direct epsilon to B then 'b' to accept C"),
        ("ab", True, "Epsilon to B, 'a' then 'b'"),
        ("aab", True, "Epsilon to B, multiple 'a's then 'b'"),
        ("a", False, "Stops at non-accepting state B"),
        ("", False, "Empty string"),
        ("ba", False, "Transition not allowed after C")
    ]

    print("\n--- String Simulation on Epsilon NFA Converted DFA ---")
    for s, expected, desc in eps_tests:
        accepted, trace = dfa2.simulate(s)
        status = "PASS" if accepted == expected else "FAIL"
        verdict = "ACCEPTED" if accepted else "REJECTED"
        print(f"[{status}] String: '{s}': {verdict} | {desc}")


def interactive_cli():
    print("\n--- Interactive Automata Simulator CLI ---")
    try:
        raw_states = input("Enter states separated by comma (e.g. q0, q1, q2): ").strip()
        states = set(s.strip() for s in raw_states.split(",") if s.strip())
        
        raw_alphabet = input("Enter alphabet symbols separated by comma (e.g. 0, 1): ").strip()
        alphabet = set(s.strip() for s in raw_alphabet.split(",") if s.strip())

        start_state = input("Enter start state (e.g. q0): ").strip()
        raw_accept = input("Enter accept states separated by comma (e.g. q2): ").strip()
        accept_states = set(s.strip() for s in raw_accept.split(",") if s.strip())

        transitions = {}
        print("\nEnter transitions for each state and symbol (comma-separated next states, or press Enter for empty/None):")
        for st in sorted(list(states)):
            for sym in sorted(list(alphabet)):
                nxt = input(f"  δ({st}, '{sym}') -> ").strip()
                if nxt:
                    transitions[(st, sym)] = set(s.strip() for s in nxt.split(",") if s.strip())
            
            # Epsilon transition
            nxt_eps = input(f"  δ({st}, 'ε') -> ").strip()
            if nxt_eps:
                transitions[(st, "e")] = set(s.strip() for s in nxt_eps.split(",") if s.strip())

        nfa = NFA(states, alphabet, transitions, start_state, accept_states)
        print_nfa_table(nfa)

        print("\nConverting NFA to DFA via Subset Construction...")
        dfa = convert_nfa_to_dfa(nfa)
        print_dfa_table(dfa)

        while True:
            test_str = input("\nEnter a string to test on DFA (or 'q' to quit): ").strip()
            if test_str.lower() == 'q':
                break
            accepted, trace = dfa.simulate(test_str)
            verdict = "ACCEPTED" if accepted else "REJECTED"
            print(f"Verdict: {verdict}")
            if trace:
                trace_str = f"{dfa.start_state} " + " ".join([f"--({sym})--> {nxt}" for _, sym, nxt in trace])
                print(f"Path Trace: {trace_str}")
            else:
                print(f"Path Trace: Start at {dfa.start_state}")

    except Exception as e:
        print(f"Error: {e}")


def main():
    print("=" * 66)
    print("        AUTOMATA SIMULATOR: NFA TO DFA CONVERTER")
    print("=" * 66)
    print("1. Run Automated Test Cases (Normal, Edge Cases & Verification)")
    print("2. Enter Custom NFA (Interactive Input)")
    print("3. Exit")
    choice = input("\nSelect an option [1-3] (Default: 1): ").strip()
    
    if choice == "2":
        interactive_cli()
    else:
        run_tests()
        print("\n[NOTE] To enter custom NFAs in CLI, select option 2.")
        print("[NOTE] You can also open 'index.html' in your browser for the full visual GUI!")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
    elif len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_cli()
    else:
        main()

