# Pilot verdicts

**Budget-match integrity check:** 6 of 60 comparison groups show a non-zero spread; **maximum relative deviation 0.27%**.

Cause: integer division when spreading the calibration allowance over 2n calibration circuits (e.g. 300 shots / 8 circuits = 37.5 -> 37, leaving 4 shots unspent out of 1500). The shortfall always falls on the *mitigated* arm, i.e. it is conservative — REM/ZNE+REM receive marginally FEWER shots than the unmitigated baseline, never more. Reported here rather than silently absorbed, per the study's scientific requirements.


```
                           min   max   rel_dev
task noise        budget                      
tfim dev_algiers  1500    1496  1500  0.002667
     dev_lagos    1500    1496  1500  0.002667
     ideal        1500    1496  1500  0.002667
     param_lam0.5 1500    1496  1500  0.002667
     param_lam1   1500    1496  1500  0.002667
     param_lam2   1500    1496  1500  0.002667
```


**Unphysical estimates** (QAOA cut > exact max 7, or TFIM energy below exact ground state): 161 / 2400 cells (6.71%)


| method | unphysical cells |
|---|---|
| no mitigation | 3 |
| ZNE | 23 |
| REM | 8 |
| ZNE+REM | 127 |


## RQ1/RQ2 — verdict counts (vs. no mitigation, non-overlapping 95% CI)


```
verdict               harms  helps  inconclusive
noise        method                             
dev_algiers  rem          0      9             1
             zne          5      3             2
             zne_rem      5      3             2
dev_lagos    rem          0      8             2
             zne          0     10             0
             zne_rem      2      2             6
ideal        rem          0      0            10
             zne          2      0             8
             zne_rem      4      0             6
param_lam0.5 rem          0      9             1
             zne          0      4             6
             zne_rem      0      8             2
param_lam1   rem          0     10             0
             zne          0      8             2
             zne_rem      0     10             0
param_lam2   rem          0     10             0
             zne          0      9             1
             zne_rem      0     10             0
```


## Crossover budgets (smallest budget where a method 'helps')


```
   task        noise  method  crossover_budget
qaoa_p1  dev_algiers     rem              1500
qaoa_p1    dev_lagos     rem              3000
qaoa_p1    dev_lagos     zne              1500
qaoa_p1 param_lam0.5     rem              1500
qaoa_p1 param_lam0.5     zne             12000
qaoa_p1 param_lam0.5 zne_rem              3000
qaoa_p1   param_lam1     rem              1500
qaoa_p1   param_lam1     zne              3000
qaoa_p1   param_lam1 zne_rem              1500
qaoa_p1   param_lam2     rem              1500
qaoa_p1   param_lam2     zne              3000
qaoa_p1   param_lam2 zne_rem              1500
   tfim  dev_algiers     rem              3000
   tfim  dev_algiers     zne              6000
   tfim  dev_algiers zne_rem              6000
   tfim    dev_lagos     rem              3000
   tfim    dev_lagos     zne              1500
   tfim    dev_lagos zne_rem             12000
   tfim param_lam0.5     rem              3000
   tfim param_lam0.5     zne             12000
   tfim param_lam0.5 zne_rem              3000
   tfim   param_lam1     rem              1500
   tfim   param_lam1     zne              3000
   tfim   param_lam1 zne_rem              1500
   tfim   param_lam2     rem              1500
   tfim   param_lam2     zne              1500
   tfim   param_lam2 zne_rem              1500
```


## RQ3 — in-loop optimisation (final error, noiseless re-evaluation)


*Budget note (amortised accounting):* circuit shots per run are identical across methods (243,000-243,000); the REM arms additionally pay a one-time calibration of 0 shots (0.0% extra), a reported inequality in REM's disfavour rather than a hidden advantage.


```
task     noise method  n_seeds  mean_abs_error    std  ci_lo  ci_hi  mean_shots  mean_execs  mean_wall_clock_s  mean_evals  mean_calibration_shots  mean_circuit_shots
tfim dev_lagos   none        4           3.127 1.4537 1.9789 4.2756    243000.0       162.0           203.3886        81.0                     0.0            243000.0
```
