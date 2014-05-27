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
import linecache


############################################
#
# output files for logging
#
############################################
eventlog = open('eventlog.txt', 'w')  # output file to log events


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
		temp = self.current_energy - self.energy_consumption["tx"]
		if temp < 0:
			self.current_energy = 0
		else:
			self.current_energy = temp



	# spend energy to sense
	def spend_sense(self):
		temp = self.current_energy - self.energy_consumption["sense"]
		if temp < 0:
			self.current_energy = 0
		else:
			self.current_energy = temp


	# spend energy to receive
	def spend_rx(self):
		temp = self.current_energy - self.energy_consumption["rx"]
		if temp < 0:
			self.current_energy = 0
		else:
			self.current_energy = temp


	# spend energy when idle
	def spend_idle(self):
		temp = self.current_energy - self.energy_consumption["idle"]
		if temp < 0:
			self.current_energy = 0
		else:
			self.current_energy = temp


	def charge(self, energy_harvested):
		if self.current_energy < self.storage_capacity:  # only charge if you still have room in your storage device
			temp = self.current_energy + energy_harvested
			if temp < self.storage_capacity:  # make sure you don't overcharge your battery
				self.current_energy = temp
			else:
				self.current_energy = self.storage_capacity  

		


############################################
#
# Program threads
#
############################################

THRESHOLD = 0  # threshold to stop operation
stop_all = False  # flag to stop operation
threadLock = threading.Lock()  # lock to synchronize threads

class IdleThread (threading.Thread):
	def __init__(self, threadID, name, node):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.node = node

	def run(self):
		global stop_all
		time.sleep(IDLE_UPDATE_INTERVAL)

		while stop_all == False:
			threadLock.acquire()
			############ Lock Acquired ############
			self.node.spend_idle()
			
			if self.node.current_energy <= THRESHOLD:  # check battery level against Threshold
				stop_all = True
			
			threadLock.release()
			############ Lock Released ############

			# log event
			fmt = '{0:30} {1:10} {2:20} -{3:15} {4:15} \n'
			eventlog.write( fmt.format( str(datetime.datetime.now()), 
					    				("%.2f" % (time.time() - starting_point)),
					    				"SPEND_IDLE",
					    				str(self.node.energy_consumption["idle"]), 
					    				str(self.node.current_energy)  )  )  


			time.sleep(IDLE_UPDATE_INTERVAL)  # sleep to wait for next event
			



class TxThread (threading.Thread):
	def __init__(self, threadID, name, node):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.node = node

	def run(self):
		global stop_all
		time.sleep(TX_UPDATE_INTERVAL)

		while stop_all == False:
			threadLock.acquire()
			############ Lock Acquired ############
			self.node.spend_tx()

			if self.node.current_energy <= THRESHOLD:  # check battery level against Threshold
				stop_all = True

			threadLock.release()
			############ Lock Released ############

			# log event
			fmt = '{0:30} {1:10} {2:20} -{3:15} {4:15} \n'
			eventlog.write( fmt.format( str(datetime.datetime.now()), 
					    				("%.2f" % (time.time() - starting_point)),
					    				"SPEND_TRANSMIT",
					    				str(self.node.energy_consumption["tx"]), 
					    				str(self.node.current_energy)  )  ) 

			time.sleep(TX_UPDATE_INTERVAL)



class SenseThread (threading.Thread):
	def __init__(self, threadID, name, node):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.node = node

	def run(self):
		global stop_all
		time.sleep(SENSE_UPDATE_INTERVAL)

		while stop_all == False:
			threadLock.acquire()
			############ Lock Acquired ############
			self.node.spend_sense()

			if self.node.current_energy <= THRESHOLD:  # check battery level against Threshold
				stop_all = True

			threadLock.release()
			############ Lock Released ############

			# log event
			fmt = '{0:30} {1:10} {2:20} -{3:15} {4:15} \n'
			eventlog.write( fmt.format( str(datetime.datetime.now()), 
					    				("%.2f" % (time.time() - starting_point)),
					    				"SPEND_SENSE",
					    				str(self.node.energy_consumption["sense"]), 
					    				str(self.node.current_energy)  )  ) 

			time.sleep(SENSE_UPDATE_INTERVAL)


class SinkThread(threading.Thread):
	def __init__(self, threadID, name, node_list):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.node_list = node_list

	def run(self):
		global stop_all
		time.sleep(SINK_UPDATE_INTERVAL)

		while stop_all == False:
			threadLock.acquire()
			############ Lock Acquired ############
			for nodes in self.node_list:
				nodes.spend_rx()

				# log rx event
				fmt = '{0:30} {1:10} {2:20} -{3:15} {4:15} \n'
				eventlog.write( fmt.format( str(datetime.datetime.now()), 
						    				("%.2f" % (time.time() - starting_point)),
						    				"SPEND_RECEIVE",
						    				str(nodes.energy_consumption["rx"]), 
						    				str(nodes.current_energy)  )  ) 

				if nodes.current_energy <= THRESHOLD:  # check battery level against Threshold
					stop_all = True
					break  # as soon as one node has hit the minimum energy threshold, break

			threadLock.release()
			############ Lock Released ############


			time.sleep(SINK_UPDATE_INTERVAL)


class HarvestEnergy(threading.Thread):
	PANEL_AREA = 1
	PANEL_EFFICIENCY = 1

	def __init__(self, threadID, name, node, filename, start_time):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.node = node
		self.filename = filename
		self.start_time = start_time

	def run(self):
		time.sleep(HARVEST_INTERVAL)
		t2 = self.start_time
		t1 = self.start_time - 30

		while stop_all == False:
			line_num = (t1 / 30) + 2

			# grab the lines we want
			line1 = (linecache.getline(self.filename, line_num)).split()
			line2 = (linecache.getline(self.filename, line_num + 1)).split()
			linecache.clearcache()

			# get the irradiance values
			irr1 = line1[1]
			irr2 = line2[1]
			
			# calculate energy harvested
			energy_harvested = self.calc_energy_harvested(float(irr1), float(irr2), float(t1), float(t2))

			threadLock.acquire()
			############ Lock Acquired ############
			self.node.charge(energy_harvested)  # charge with energy_harvested
			threadLock.release()
			############ Lock Released ############

			# log event
			fmt = '{0:30} {1:10} {2:20} +{3:15} {4:15} \n'
			eventlog.write( fmt.format( str(datetime.datetime.now()), 
					    				("%.2f" % (time.time() - starting_point)),
					    				"HARVEST",
					    				str(energy_harvested), 
					    				str(self.node.current_energy)  )  )

			t2 += 30
			t1 += 30
			time.sleep(HARVEST_INTERVAL)
	

	def calc_energy_harvested(self, irr1, irr2, t1, t2):
		
		###############################################
		#
		#  Here we determine how much energy is
		#  harvested over a period t2 - t1. We 
		#  assume the curve is linear over this
		#  time period so first calculate the
		#  equation for this line. We then integrate
		#  this line over the period [t2, t1]
		#  to determine the energy in joules.
		# 
		###############################################

		# convert irradiance to power
		p1 = irr1 * self.PANEL_AREA * self.PANEL_EFFICIENCY
		p2 = irr2 * self.PANEL_AREA * self.PANEL_EFFICIENCY

		# calculate slope and intercept
		m = (p2 - p1) / (t2 - t1)
		b = p2 - (m * t2)
		
		# now calculate energy by integrating 
		energy = (  ( ((m * t2**2) / 2) + (b * t2) ) -
					( ((m * t1**2) / 2) + (b * t1) )   )

		return energy








############################################
#
# Start of Main script
#
############################################

# event intervals
IDLE_UPDATE_INTERVAL  = 0.25
TX_UPDATE_INTERVAL 	  = 1
SENSE_UPDATE_INTERVAL = 1
SINK_UPDATE_INTERVAL  = 10
HARVEST_INTERVAL      = 30


# list of devices that cnosume energy and how much energy they consume
energy_consumption = {'tx': 100, 'rx': 5, 'idle': 0.5, 'sense': 50} 

# list containing nodes in the network
network = []

# create new node
window_node = EHN(1, 1000, energy_consumption)

network.append(window_node)

# create new threads
thread1 = IdleThread(1, "idle", window_node)
thread2 = TxThread(2, "tx", window_node)
thread3 = SinkThread(3, "sink", network)
thread4 = SenseThread(4, "sense", window_node)
thread5 = HarvestEnergy(5, "harvest", window_node, "irradiance_test.txt", 120)

# log the start in the event log
starting_point = time.time()  # timestamp when you start the simulation
eventlog.write("Starting at " + str(datetime.datetime.now()) + " \n")
eventlog.write("Starting Energy: " + str(window_node.storage_capacity) + "\n")

# start thread
thread1.start()
thread2.start()
thread3.start()
thread4.start()
thread5.start()

