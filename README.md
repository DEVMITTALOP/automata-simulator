# Automata Simulator: NFA -> DFA Conversion

A small, crisp, and easy-to-use Automata Simulator developed for the **Simulator Design M2 Evaluation (23–27 November 2026)**.

---

## 🚀 How to Run (Choose Either Method)

### Method 1: Web Visualizer (Recommended for Demo)
1. Double-click **`index.html`** in Windows Explorer (or right-click -> Open with Chrome / Edge).
2. **Zero installation or server needed!** It runs immediately in any browser offline.
3. Use the **Quick Presets** buttons (e.g. *Ends with "01"*, *With ε transitions*) or enter your own custom states and alphabet.
4. Click **"Convert NFA to DFA"** to view:
   - Subset construction step-by-step log
   - Side-by-side NFA & DFA transition tables with state mappings
   - Canvas-rendered state diagrams
   - Interactive string tester & batch test suite with instant PASS/FAIL status.

---

### Method 2: Python CLI Engine
Run from your command line / PowerShell inside this folder:
```bash
# Run automated normal & edge case verification tests:
python simulator.py --test

# Run interactive CLI mode to enter custom automata:
python simulator.py --interactive
```

---

## 📂 File Structure

| File | Description |
| :--- | :--- |
| **`index.html`** | Single-file interactive GUI with Canvas graph diagrams, presets, transition tables, and string tester. |
| **`simulator.py`** | Standalone Python 3 engine with subset construction, table printing, and test suite. |
| **`REPORT.md`** | Complete formal Technical Report & Documentation matching all 9 marks criteria on the rubric. |
| **`README.md`** | Quick-start guide and demonstration instructions. |

---


