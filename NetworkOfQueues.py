from SimPy.Simulation import *
import random as rnd
import numpy.random as rnp
import argparse
import matplotlib.pyplot as plt


class Parameters:
  
    vM = Monitor()
    vMcpuwait = Monitor()
    vMcpulength = Monitor()
    vMdisk = Monitor()
    vMnet = Monitor()
    packageArrivalCounter = 0
    seed = 123



#generate packets with poisson arrival rate (so exponential interarrival time) 
class CPUGenerator( Process ):
    def produce( self, b ):
        while True:
            c = CPU_Behavior( b, Parameters.packageArrivalCounter )
            c.start( c.doit() )
            Parameters.packageArrivalCounter +=1
            yield hold, self, rnd.expovariate(1.0/40)

      
      
#CPU queue (MM2)
class CPU_Behavior( Process ):
    def __init__( self, resource, i ):
        Process.__init__( self )
        self.i = i
        self.bank = resource

    def doit( self ):
        arrive = now()
        print "Time %f : %d arrived and about to join the CPU queue  "%(now(), self.i)
        yield request, self, self.bank
        wait = now() - arrive
        Parameters.vMcpu.observe(wait)
        print "Time %f : %d is about to get its CPU service initiated "%(now(), self.i)
        yield hold, self, self.bank.servicetime()
        yield release, self, self.bank
        print "Time %f : %d CPU service terminated " %(now(), self.i)
        
        rand = rnd.uniform(0,1)
        if rand < .1:
            DiskBank = Disk(capacity=1, monitored=True, monitorType=Monitor)
            c = Disk_Behavior( DiskBank, self.i )
            activate( c, c.doit(), prior=True )
        if rand > .6:
            NetBank = Network(capacity=1, monitored=True, monitorType=Monitor)
            c = Network_Behavior( NetBank, self.i )
            activate( c, c.doit(), prior=True )
                
    def again( self ):
        print "Time %f : %d arrived and about to join the CPU queue  "%(now(), self.i)
        yield request, self, self.bank
        print "Time %f : %d is about to get its CPU service initiated "%(now(), self.i)
        yield hold, self, self.bank.servicetime()
        yield release, self, self.bank
        print "Time %f : %d CPU service terminated " %(now(), self.i)
        rand = rnd.uniform(0,1)
        if rand < .1:
            DiskBank = Disk(capacity=1, monitored=True, monitorType=Monitor)
            c = Disk_Behavior( DiskBank, self.i )
            activate( c, c.doit(), prior=True )
        if rand > .6:
            NetBank = Network(capacity=1, monitored=True, monitorType=Monitor)
            c = Network_Behavior( NetBank, self.i )
            activate( c, c.doit(), prior=True) 

#Disk Queue (MM1)        
class Disk_Behavior( Process ):
    def __init__( self, resource, i ):
        Process.__init__( self )
        self.i = i
        self.bank = resource


    def doit( self ):
        arrive = now()
        print "Time %f : %d arrived and about to join the disk queue  "%(now(), self.i)
        yield request, self, self.bank
        wait = now() - arrive
        Parameters.vMdisk.observe(wait)
        print "Time %f : %d is about to get its disk service initiated "%(now(), self.i)
        yield hold, self, self.bank.servicetime()
        yield release, self, self.bank
        print "Time %f : %d disk service terminated " %(now(), self.i)
        rand = rnd.uniform(0,1)
        if rand < .5:
            CPUBank = CPU( capacity=2, monitored=True, monitorType=Monitor )
            c = CPU_Behavior( CPUBank, self.i )
            activate( c, c.again(), prior=True  )
        else:
            NetBank = Network(capacity=1, monitored=True, monitorType=Monitor)
            c = Network_Behavior( NetBank, self.i )
            activate( c, c.doit(), prior=True  )


#Network queue (MM1)
class Network_Behavior( Process ):
  
    def __init__( self, resource, i ):
        Process.__init__( self )
        self.i = i
        self.bank = resource


    def doit( self ):
        arrive = now()
        print "Time %f : %d arrived and about to join the Network queue  "%(now(), self.i)
        yield request, self, self.bank
        wait = now() - arrive
        Parameters.vMnet.observe(wait)
        print "Time %f : %d is about to get its Network service initiated "%(now(), self.i)
        yield hold, self, self.bank.servicetime()
        yield release, self, self.bank
        print "Time %f : %d Network service terminated " %(now(), self.i)
        CPUBank = CPU( capacity=2, monitored=True, monitorType=Monitor )
        c = CPU_Behavior( CPUBank, self.i )
        activate( c, c.again(), prior=True  )

        
#generate exponential service time
class CPU( Resource ):
    def servicetime( self ):
        return rnd.expovariate(1.0/.02) 
      
class Disk( Resource ):
    def servicetime( self ):
        return rnd.expovariate(1.0/.1)
  
class Network ( Resource ):
    def servicetime( self ):
        return rnd.expovariate(1.0/.025)


#run simulation
def run_simulation( totaltime, numberofsimulations ):
    for r in range(numberofsimulations):
        CPUBank = CPU( capacity=2, monitored=True, monitorType=Monitor ) #make CPU MM2

        initialize()
        src = CPUGenerator()
        activate( src, src.produce( CPUBank ))
    
        startCollection(when=totaltime)
        simulate(until=2*totaltime)
               
        result = Parameters.vMcpu.count(), Parameters.vMcpu.mean()
        Parameters.seed+= 25
        print "Average wait for %3d completions was %5.3f seconds."% result


run_simulation( 100, 1)
