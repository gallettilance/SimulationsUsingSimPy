from SimPy.Simulation import *
import random as rnd
import numpy.random as rnp
import argparse
import matplotlib.pyplot as plt

#global parameters with fixed values for assignment - could easily extend to a more flexible program that takes input from
#user to determine what these quantities should be (for later maybe?)
class Parameters:
    
    arrmin = 1.5
    arrmax = 3.5                      
    intmin = 2.5
    intmax = 6.5
    wM = Monitor()
    interarrival_time = 10.0
    service_time = 8.0
    packageArrivalCounter = 0
    x = []
    y = []
    bankservicetime = 0
    seed = 123


#generates Packets with a uniform interarrival rate
class PacketGeneratorU( Process ):
    def produce( self, b ):
        while True:
            c = PacketU( b, Parameters.packageArrivalCounter )
            c.start( c.doit() )
            Parameters.packageArrivalCounter +=1
            yield hold, self, rnp.uniform(Parameters.arrmin, Parameters.arrmax)

#generates a queue where packets that arrive from PacketGeneratorU() are serviced with a uniform service time (or queued)
class PacketU( Process ):
    def __init__( self, resource, i ):
        Process.__init__( self )
        self.i = i
        self.banku = resource

    def doit( self ):
        arrive = now()
        print "Time %f : %d arrived and about to join the queue  "%(now(), self.i)
        yield request, self, self.banku 
        wait = now() - arrive
        Parameters.wM.observe(wait) #monitor waiting times
        print "Time %f : %d is about to get its service initiated "%(now(), self.i)
        yield hold, self, self.banku.servicetime() #uniform service time
        yield release, self, self.banku
        print "Time %f : %d service terminated and exits " %(now(), self.i)
#generates a uniform service time unless service time is varying (in which case use property that service time will eventually be constant)
class BankU( Resource ):
    def servicetime( self ):
        if arg.generateRawResults == False:
            return rnp.uniform(Parameters.intmin, Parameters.intmax)
        if arg.generateRawResults == True:
            return Parameters.service_time


#generate packets with poisson arrival rate (so exponential interarrival time) 
class PacketGenerator( Process ):
    def produce( self, b ):
        while True:
            c = Packet( b, Parameters.packageArrivalCounter )
            c.start( c.doit() )
            Parameters.packageArrivalCounter +=1
            yield hold, self, rnd.expovariate(1.0/Parameters.interarrival_time)

#generate queue with an exponential service time
class Packet( Process ):
    def __init__( self, resource, i ):
        Process.__init__( self )
        self.i = i
        self.bank = resource

    def doit( self ):
        arrive = now()
        print "Time %f : %d arrived and about to join the queue  "%(now(), self.i)
        yield request, self, self.bank
        wait = now() - arrive
        Parameters.wM.observe(wait)
        print "Time %f : %d is about to get its service initiated "%(now(), self.i)
        yield hold, self, self.bank.servicetime()
        yield release, self, self.bank
        print "Time %f : %d service terminated and exits " %(now(), self.i)
#generates an exponential service time
class Bank( Resource ):
    def servicetime( self ):
        return rnd.expovariate(1.0/Parameters.service_time) #service time should vary with specific simulations (see below)


#either we run the simulation once with a specified seed to verify validity of simulation or we run multiple simultaions
#each simulation should repeat 10 times while varying the service time and then plot service time against mean waiting time
def run_simulation(bankservicetime, totaltime, numberofsimulations):
    if arg.type == 'UU1':
        for r in range(numberofsimulations):
            rnp.seed(Parameters.seed)
            initialize()
    
            banku = BankU( capacity=1, monitored=True, monitorType=Monitor )
            Parameters.wM = Monitor() 
            src = PacketGeneratorU()
            activate( src, src.produce( banku ), at=rnp.uniform(Parameters.arrmin, Parameters.arrmax))
            startCollection(when=totaltime/2)
            simulate(until=totaltime)
            Parameters.x.append(bankservicetime)
            Parameters.y.append(banku.waitMon.timeAverage())

            print Parameters.y
            result = Parameters.wM.count(), Parameters.wM.mean()
            Parameters.seed+= 25
            print "Average wait for %3d completions was %5.3f seconds."% result
            
    if arg.type == 'MM1':
        for r in range(numberofsimulations):
            rnp.seed(Parameters.seed)
            initialize()
   
            bank = Bank( capacity=1, monitored=True, monitorType=Monitor )
            Parameters.wM = Monitor() 
            src = PacketGenerator()
            activate( src, src.produce( bank ), at = rnd.expovariate(1.0/Parameters.interarrival_time))
            startCollection(when=totaltime/2)
            simulate(until=totaltime)
            Parameters.x.append(bankservicetime)
            Parameters.y.append(bank.waitMon.timeAverage())
            
            print Parameters.y
            result = Parameters.wM.count(), Parameters.wM.mean()
            Parameters.seed+= 25
            print "Average wait for %3d completions was %5.3f seconds."% result
            
    if arg.type == 'MM2':
        for r in range(numberofsimulations):
            rnp.seed(Parameters.seed)
            initialize()

            bank = Bank( capacity=2, monitored=True, monitorType=Monitor )

            src = PacketGenerator()
            activate( src, src.produce( bank ))
            startCollection(when=totaltime/2)
            simulate(until=totaltime)
            Parameters.x.append(bankservicetime)
            Parameters.y.append(bank.waitMon.timeAverage())
            
            print Parameters.y
            Parameters.seed+= 25


#use parser to input command line arguments to generate different queues based on input
parser = argparse.ArgumentParser()
parser.add_argument('-generateRawResults', '-generateRawResults', action='store_true', default = False)
parser.add_argument('--type', '--type', required=True)
arg = parser.parse_args()


#how to run simulation based on command line user input
if arg.generateRawResults == True:
    Parameters.service_time = 0.5
    while Parameters.service_time <= 11.0:
        Parameters.service_time +=.5
        run_simulation(Parameters.service_time, 120, 10)
    
    print Parameters.x
    print Parameters.y
    plt.scatter(Parameters.x, Parameters.y) #resulting plot
    plt.show()

if arg.generateRawResults == False:
    run_simulation(Parameters.service_time, 120, 1)
        

