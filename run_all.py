"""Reproduce every result and plot. Add each new attack here as you build it.

    python run_all.py
"""
from bench import run_fermat, plot_fermat
from bench.bench import run_sweep

if __name__ == "__main__":
    print("== Fermat ==")
    run_sweep("fermat", "gap_bits", run_fermat.GAPS, run_fermat.make_key,
              run_fermat.attack, run_fermat.check, trials=run_fermat.TRIALS)
    plot_fermat.main()
    # Week 2: Wiener goes here
    # Week 3: Coppersmith (Sage) goes here
