##########################################################
#
#  Energy Harvesting Node Simulation
#  By Earvin Caceres, ec2946 & Marina Fahim, mf2895 
#  ELENE 6951 - Wireless & Mobile Networking II 
#  Columbia University
# 
##########################################################


import random
import time
import datetime
import threading


############################################
#
# Energy Harvesting Node Class Definition
#
############################################


class EHN(object):

	# initialize energy harvesting node
	def __init__(self, node_id, storage_capacity, energy_consumption):
		self.node_id = node_id
		self.storage_capacity = storage_capacity
		self.current_energy = storage_capacity
		self.energy_consumption = energy_consumption


	# spend energy to transmit
	def spend_tx(self):
		total_energy_spent = 0  # will keep track of total energy spent
		
		for dev, joules in energy_consumption.iteritems():  # sum all items that will spend energy
			if dev == "tx":  # energy required to 
				total_energy_spent += joules

		self.current_energy -= total_energy_spent  # update current energy level
		print "TX Consumes: " + str(total_energy_spent)
		print "New Energy: " + str(self.current_energy)


	# spend energy to sense
	def spend_sense(self):
		total_energy_spent = 0  # will keep track of total energy spent
		
		for dev, joules in energy_consumption.iteritems():  # sum all items that will spend energy
			if dev == "sense":  # energy required to sense 
				total_energy_spent += joules

		self.current_energy -= total_energy_spent  # update current energy level
		print "Sense Consumes: " + str(total_energy_spent)
		print "New Energy: " + str(self.current_energy)


	# spend energy to receive
	def spend_rx(self):
		total_energy_spent = 0  # will keep track of total energy spent
		
		for dev, joules in energy_consumption.iteritems():  # sum all items that will spend energy
			if dev == "rx":  # only spend what's required for receiving
				total_energy_spent += joules

		self.current_energy -= total_energy_spent  # update current energy level
		print "RX Consumes: " + str(total_energy_spent)
		print "New Energy: " + str(self.current_energy)


	# spend energy when idle
	def spend_idle(self):
		self.current_energy -= self.energy_consumption["idle"]
		print "Idle Consumes: " + str(self.energy_consumption["idle"])
		print "New Energy: " + str(self.current_energy)



############################################
#
# Program threads
#
############################################

threadLock = threading.Lock()

class IdleThread (threading.Thread):
	IDLE_UPDATE_INTERVAL = 1.0

	def __init__(self, threadID, name, node):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.node = node

	def run(self):
		time.sleep(self.IDLE_UPDATE_INTERVAL)

		for i in range(10):

			threadLock.acquire()
			############ Lock Acquired ############
			self.node.spend_idle()
			threadLock.release()
			############ Lock Released ############
			time.sleep(self.IDLE_UPDATE_INTERVAL)

		print "exiting Idle thread"


class TxThread (threading.Thread):
	TX_UPDATE_INTERVAL = 2.0

	def __init__(self, threadID, name, node):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.node = node

	def run(self):
		time.sleep(self.TX_UPDATE_INTERVAL)

		for i in range(5):

			threadLock.acquire()
			############ Lock Acquired ############
			self.node.spend_tx()
			threadLock.release()
			############ Lock Released ############
			time.sleep(self.TX_UPDATE_INTERVAL)

		print "exiting TX thread"


class SenseThread (threading.Thread):
	SENSE_UPDATE_INTERVAL = 3.0

	def __init__(self, threadID, name, node):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.node = node

	def run(self):
		time.sleep(self.SENSE_UPDATE_INTERVAL)

		for i in range(5):

			threadLock.acquire()
			############ Lock Acquired ############
			self.node.spend_sense()
			threadLock.release()
			############ Lock Released ############
			time.sleep(self.SENSE_UPDATE_INTERVAL)

		print "exiting Sense thread"


class SinkThread(threading.Thread):
	SINK_UPDATE_INTERVAL = 5.0

	def __init__(self, threadID, name, node_list):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.node_list = node_list

	def run(self):
		time.sleep(self.SINK_UPDATE_INTERVAL)

		for i in range (5):

			threadLock.acquire()
			############ Lock Acquired ############
			for nodes in self.node_list:
				nodes.spend_rx()

			threadLock.release()
			############ Lock Released ############
			time.sleep(self.SINK_UPDATE_INTERVAL)

		print "exiting SINK thread"





############################################
#
# Start of Main script
#
############################################



# list of devices that cnosume energy and how much energy they consume
energy_consumption = {'tx': 10, 'rx': 5, 'idle': 1, 'sense': 100} 

# list containing nodes in the network
network = []

# create new node
window_node = EHN(1, 1000, energy_consumption)

network.append(window_node)

print "--- Starting Simulation ----"
print window_node.storage_capacity
print window_node.current_energy
print window_node.energy_consumption
print 

# create new threads
thread1 = IdleThread(1, "idle", window_node)
thread2 = TxThread(2, "tx", window_node)
thread3 = SinkThread(3, "sink", network)
thread4 = SenseThread(4, "sense", window_node)

# start thread
thread1.start()
thread2.start()
thread3.start()
thread4.start()

time.sleep(60)

print "------test out of class-------"
print window_node.current_energy

