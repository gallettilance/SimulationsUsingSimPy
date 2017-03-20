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
    name = 0
  
    def produce( self, b ):
        while True:
            c = CPU_Behavior( b )
            c.start( c.doit() )
            yield hold, self, rnd.expovariate(1.0/40)

      
      
#generate queue with an exponential service time
class CPU_Behavior( Process ):
    def __init__( self, resource ):
        Process.__init__( self )
        self.bank = resource

    def doit( self ):
        Parameters.packageArrivalCounter +=1
        CPUGenerator.name = Parameters.packageArrivalCounter
        arrive = now()
        print "Time %f : %d arrived and about to join the CPU queue  "%(now(), CPUGenerator.name)
        yield request, self, self.bank
        wait = now() - arrive
        Parameters.vMcpu.observe(wait)
        print "Time %f : %d is about to get its CPU service initiated "%(now(),CPUGenerator.name)
        yield hold, self, self.bank.servicetime()
        yield release, self, self.bank
        print "Time %f : %d CPU service terminated " %(now(), CPUGenerator.name)
        rand = rnd.uniform(0,1)
        if rand < .1:
            DiskBank = Disk(capacity=1, monitored=True, monitorType=Monitor)
            c = Disk_Behavior( DiskBank )
            activate( c, c.doit(), prior=True )
        if rand > .6:
            NetBank = Network(capacity=1, monitored=True, monitorType=Monitor)
            c = Network_Behavior( NetBank )
            activate( c, c.doit(), prior=True )
                
    def again( self ):
        print "Time %f : %d arrived and about to join the CPU queue  "%(now(), CPUGenerator.name)
        yield request, self, self.bank
        print "Time %f : %d is about to get its CPU service initiated "%(now(),CPUGenerator.name)
        yield hold, self, self.bank.servicetime()
        yield release, self, self.bank
        print "Time %f : %d CPU service terminated " %(now(), CPUGenerator.name)
        rand = rnd.uniform(0,1)
        if rand < .1:
            DiskBank = Disk(capacity=1, monitored=True, monitorType=Monitor)
            c = Disk_Behavior( DiskBank )
            activate( c, c.doit(), prior=True )
        if rand > .6:
            NetBank = Network(capacity=1, monitored=True, monitorType=Monitor)
            c = Network_Behavior(NetBank )
            activate( c, c.doit(), prior=True) 

        
class Disk_Behavior( Process ):
    def __init__( self, resource ):
        Process.__init__( self )
        self.bank = resource


    def doit( self ):
        arrive = now()
        print "Time %f : %d arrived and about to join the disk queue  "%(now(), CPUGenerator.name)
        yield request, self, self.bank
        wait = now() - arrive
        Parameters.vMdisk.observe(wait)
        print "Time %f : %d is about to get its disk service initiated "%(now(), CPUGenerator.name)
        yield hold, self, self.bank.servicetime()
        yield release, self, self.bank
        print "Time %f : %d disk service terminated " %(now(), CPUGenerator.name)
        rand = rnd.uniform(0,1)
        if rand < .5:
            CPUBank = CPU( capacity=2, monitored=True, monitorType=Monitor )
            c = CPU_Behavior( CPUBank )
            activate( c, c.again(), prior=True  )
        else:
            NetBank = Network(capacity=1, monitored=True, monitorType=Monitor)
            c = Network_Behavior( NetBank )
            activate( c, c.doit(), prior=True  )


  
class Network_Behavior( Process ):
  
    def __init__( self, resource ):
        Process.__init__( self )
        self.bank = resource


    def doit( self ):
        arrive = now()
        print "Time %f : %d arrived and about to join the Network queue  "%(now(), CPUGenerator.name)
        yield request, self, self.bank
        wait = now() - arrive
        Parameters.vMnet.observe(wait)
        print "Time %f : %d is about to get its Network service initiated "%(now(), CPUGenerator.name)
        yield hold, self, self.bank.servicetime()
        yield release, self, self.bank
        print "Time %f : %d Network service terminated " %(now(), CPUGenerator.name)
        CPUBank = CPU( capacity=2, monitored=True, monitorType=Monitor )
        c = CPU_Behavior( CPUBank )
        activate( c, c.again(), prior=True  )

        
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
def run_simulation( totaltime, numberofsimulations ):
    for r in range(numberofsimulations):
        CPUBank = CPU( capacity=2, monitored=True, monitorType=Monitor )

        initialize()
        src = CPUGenerator()
        activate( src, src.produce( CPUBank ))
    
        startCollection(when=totaltime)
        simulate(until=2*totaltime)
               
        result = Parameters.vMcpu.count(), Parameters.vMcpu.mean()
        Parameters.seed+= 25
        print "Average wait for %3d completions was %5.3f minutes."% result


run_simulation( 100, 1)



#print Parameters.x
#print Parameters.y
#plt.scatter(Parameters.x, Parameters.y) #resulting plot
#plt.show()
