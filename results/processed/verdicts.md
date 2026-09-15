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


*Budget note (amortised accounting):* circuit shots per run are identical across methods (243,000-243,000); the REM arms additionally pay a one-time calibration of 600 shots (0.2% extra), a reported inequality in REM's disfavour rather than a hidden advantage.


```
   task     noise  method  n_seeds  mean_abs_error    std  ci_lo  ci_hi  mean_shots  mean_execs  mean_wall_clock_s  mean_evals  mean_calibration_shots  mean_circuit_shots
qaoa_p1 dev_lagos    none        5          0.0046 0.0038 0.0020 0.0078    243000.0        81.0           135.0916        81.0                     0.0            243000.0
qaoa_p1 dev_lagos     rem        5          0.0527 0.0768 0.0077 0.1220    243600.0        93.0           126.2820        81.0                   600.0            243000.0
qaoa_p1 dev_lagos     zne        5          0.0236 0.0159 0.0114 0.0357    243000.0       243.0           244.6346        81.0                     0.0            243000.0
qaoa_p1 dev_lagos zne_rem        5          0.7669 0.8244 0.1415 1.3923    243600.0       255.0           253.4309        81.0                   600.0            243000.0
   tfim dev_lagos    none        5          3.0891 1.2618 2.1707 4.1328    243000.0       162.0           197.9954        81.0                     0.0            243000.0
   tfim dev_lagos     rem        5          2.8844 1.3083 1.9823 3.9746    243600.0       170.0           156.9412        81.0                   600.0            243000.0
   tfim dev_lagos     zne        5          3.1338 0.6742 2.6313 3.7157    243000.0       486.0           371.6719        81.0                     0.0            243000.0
   tfim dev_lagos zne_rem        5          4.2767 0.8806 3.6472 4.9972    243600.0       494.0           351.0110        81.0                   600.0            243000.0
```


### RQ3 diagnostics — did the optimiser converge, and was it misled?


`mean_observed_descent` is the change in the NOISY objective the optimiser saw (negative = it thought it was improving). `unphysical_pct` is the share of in-loop objective evaluations that were physically impossible (VQE energy below the exact ground state, or QAOA cut above the exact maximum).


```
                 mean_observed_descent  mean_final_err  unphysical_pct
task    method                                                        
qaoa_p1 none                    -0.334           0.005            0.00
        rem                     -0.834           0.053            0.00
        zne                     -0.742           0.024            0.00
        zne_rem                 -0.473           0.767            3.25
tfim    none                    -0.983           3.089            0.00
        rem                     -2.539           2.884            0.00
        zne                     -2.263           3.134            0.00
        zne_rem                 -2.196           4.277           10.25
```
