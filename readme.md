# Generating benchmark problems

## Random n-ary DCOPs
To generate a random DCOP, pass the following arguments to `main.py`:
```bash
-t randomDCOP         specifies the problem type to random DCOP
-f filename           the destination file of the generated problems
optinal arguments:
-md minimum_domain    minimum domain size (default=2)
-xd maximum_domain    maximum domain size (default=5)
-ma minimum_arity     minimum arity (default=2)
-xa maximum_arity     maximum arity (default=5)
-fn fac_num           the number of function node (default=10)
-mt minimum_tightness minimum variable tightness (default=0.1)
-xt maximum_tightness maximum variable tightness (default=0.5)
-mu minimum_utility   minimum utility value (default=0)
-xu maximum_utility   maximum utility value (default=1000)
```
Examples:
```bash
python -um entry.main -t  randomDCOP -f foo.xml -md 3 -xd 5 -ma 3 -xa 5 -fn 30 -mt .2 -xt .4
```

## NetRad systems
To generate a NetRad system problem, pass the following arguments to `main.py`:
```bash
-t netRad             specifies the problem type to random DCOP
-f filename           the destination file of the generated problems
optinal arguments:
-r row                number of rows in the grid (default=6)
-c col                number of columns in the grid (default=8)
-np num_phenomona     number of phenomona (default=48)
```
Examples:
```bash
python -um entry.main -t netRad -f foo.xml -r 6 -c 8 -np 56
```

## Channel allocation
To generate a channel allocation system problem, pass the following arguments to `main.py`:
```bash
-t channelAllocation  specifies the problem type to random DCOP
-f filename           the destination file of the generated problems
optinal arguments:
-r row                number of rows in the grid (default=6)
-c col                number of columns in the grid (default=8)
-cn channels          number of channels (default=10)
-ap access_points     number of access points (default=60)
-xp maximum_power     maximum power (default=510)
-mp minimum_power     minimum power (default=490)
-bkg bkg_noise        background noise (default=1)
```
Examples:
```bash
python -um entry.main -t channelAllocation -f foo.xml -r 300 -c 300 -ap 70 -bkg 0.5
```
