"""Reproduce every result and plot. Add each new attack here as you build it.

    python run_all.py
"""
from bench import run_fermat, plot_fermat, run_wiener, plot_wiener
from bench.bench import run_sweep

if __name__ == "__main__":
    print("== Fermat ==")
    run_sweep("fermat", "gap_bits", run_fermat.GAPS, run_fermat.make_key,
              run_fermat.attack, run_fermat.check, trials=run_fermat.TRIALS)
    plot_fermat.main()
    print("== Wiener ==")
    run_sweep("wiener", "d_bits", run_wiener.D_BITS, run_wiener.make_key,
              run_wiener.attack, run_wiener.check, trials=run_wiener.TRIALS)
    plot_wiener.main()
    # Week 3: Coppersmith (Sage) goes here
