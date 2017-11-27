#Queue Simulations

###NetworkOfQueues.py

* Processes come into CPU with rate 40/s

* The CPU is an MM2, with service time .02s

* After being serviced by the CPU, the process moves on to:
          * the NetWork with probability .4
          * the disk with probability .1
          * is done with probability .5

* The Network is an MM1 queue with service time .025

* The Disk is an MM1 queue with service time .1

* After being serviced by the Network, the process circles back to get serviced by the CPU with probability 1

* After being serviced by the disk, the process:
          * circles back to get serviced by the CPU with probability .5
          * moves on to the Network with probability .5

###BasicQueueSimulation.py

* For MM1, compile with:

          
          python BasicQueueSimulation.py --type MM1
          
* For UU1, compile with:

          python BasicQueueSimultaion.py --type UU1
* For MM2, compile with:

          python BasicQueueSimulation.py --type MM2


To generate a plot of Average Queue Length (w) against Service Time (Ts) add -generateRawResults flag before --type flag

####Example:


    python BasicQueueSimulation.py -generateRawResults --type MM1
