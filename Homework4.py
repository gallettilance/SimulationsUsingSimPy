from SimPy.Simulation import *
import random as rnd
import numpy.random as rnp
import argparse
import matplotlib.pyplot as plt

#global parameters with fixed values for assignment - could easily extend to a more flexible program that takes input from
#user to determine what these quantities should be (for later maybe?)
class Parameters:
  
    vMcpu = Monitor()
    vMdisk = Monitor()
    vMnet = Monitor()
    packageArrivalCounter = 0
    seed = 123


#generate packets with poisson arrival rate (so exponential interarrival time) 
class CPUGenerator( Process ):
  def __init___(self):
    self.name = Parameters.n
  
  def produce( self, b ):
    while True:
      Parameters.n +=1
      c = CPU_Behavior( b )
      c.start( c.doit() )
      yield hold, self, rnd.expovariate(1.0/40)

      
      
#generate queue with an exponential service time
class CPU_Behavior( Process ):
    def __init__( self, resource ):
        Process.__init__( self )
        self.bank = resource

    def doit( self ):
        arrive = now()
        print "Time %f : %d arrived and about to join the queue  "%(now(), PacketGenerator.name)
        yield request, self, self.bank
        wait = now() - arrive
        Parameters.wMcpu.observe(wait)
        print "Time %f : %d is about to get its service initiated "%(now(), PacketGenerator.name)
        yield hold, self, self.bank.servicetime()
        yield release, self, self.bank
        print "Time %f : %d service terminated and exits " %(now(), PacketGenerator.name)
        if Parameters.rand < .1:
          Disk_Behavior.doit()
        if Parameters.rand > .6:
          Network_Behavior.doit()

        
class Disk_Behavior( Process ):
  def __init__( self, resource ):
        Process.__init__( self )
        self.bank = resource


    def doit( self ):
        arrive = now()
        print "Time %f : %d arrived and about to join the queue  "%(now(), PacketGenerator.name)
        yield request, self, self.bank
        wait = now() - arrive
        Parameters.wMdisk.observe(wait)
        print "Time %f : %d is about to get its service initiated "%(now(), PacketGenerator.name)
        yield hold, self, self.bank.servicetime()
        yield release, self, self.bank
        print "Time %f : %d service terminated and exits " %(now(), PacketGenerator.name)
        if Parameters.rand < .5:
          CPU_Behavior.doit()
        else:
          Network_Behavior.doit()

  
class Network_Behavior( Process ):
  
  def __init__( self, resource ):
        Process.__init__( self )
        self.bank = resource


    def doit( self ):
        arrive = now()
        print "Time %f : %d arrived and about to join the queue  "%(now(), PacketGenerator.name)
        yield request, self, self.bank
        wait = now() - arrive
        Parameters.wMnet.observe(wait)
        print "Time %f : %d is about to get its service initiated "%(now(), PacketGenerator.name)
        yield hold, self, self.bank.servicetime()
        yield release, self, self.bank
        print "Time %f : %d service terminated and exits " %(now(), PacketGenerator.name)
        CPU_Behavior.doit()

        
#generates an exponential service time
class CPU( Resource ):
    def servicetime( self ):
        return rnd.expovariate(1.0/.02) 
      
class Disk( Resource ):
  def servicetime( self ):
        return rnd.expovariate(1.0/.1)
  
class Network ( Resource ):
  def servicetime( self ):
        return rnd.expovariate(1.0/.025)

    
#either we run the simulation once with a specified seed to verify validity of simulation or we run multiple simultaions
#each simulation should repeat 10 times while varying the service time and then plot service time against mean waiting time
def run_simulation( totaltime, numberofsimulations):
  CPUBank = CPU( capacity=2, monitored=True, monitorType=Monitor )

  
  for r in range(numberofsimulations):
    rnp.seed(Parameters.seed)
    initialize()
    src = CPUGenerator()
    activate( src, src.produce( CPUBank ))
    
    startCollection(when=totaltime/2)
    simulate(until=totaltime)
               
    result = Parameters.wM.count(), Parameters.wM.mean()
    Parameters.seed+= 25
    print "Average wait for %3d completions was %5.3f minutes."% result




  


run_simulation( 100, 1)



#print Parameters.x
#print Parameters.y
#plt.scatter(Parameters.x, Parameters.y) #resulting plot
#plt.show()
