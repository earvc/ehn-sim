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
eventlog = open('eventlog.txt', 'w')       # output file to log all events
batterylog = open('batterylog.dat', 'w')     # output file to log energy
harvestedlog = open('harvested.dat', 'w')  # output file to log energy harvested


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

			logtime = (time.time() - starting_point) 

			if LOG_EVENTS == True:
				fmt = '{0:30} {1:10} {2:20} -{3:15} {4:15} \n'
				eventlog.write( fmt.format( str(datetime.datetime.now()), 
						    				("%.2f" % (logtime)),
						    				"SPEND_IDLE",
						    				str(self.node.energy_consumption["idle"]), 
						    				str(self.node.current_energy)  )  )  
			if LOG_BATT_STATE == True:
				batterylog.write( ("%.2f" % float(logtime)) + " " +
									("%.5f" % float(self.node.current_energy)) + "\n" )


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

			if LOG_EVENTS == True:
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

			if LOG_EVENTS == True:
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

				if LOG_EVENTS == True:
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
	

	def __init__(self, threadID, name, node, data_list):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.node = node
		self.filename = filename
		self.start_time = start_time
		self.stop_time = stop_time

	def run(self):
		global stop_all

		index = 0
		time.sleep(HARVEST_INTERVAL)

		while stop_all == False:
				
			# calculate energy harvested
			energy_harvested = data_list[index][1]  # index 1 is the energy harvested data

			threadLock.acquire()
			############ Lock Acquired ############
			self.node.charge(energy_harvested)  # charge with energy_harvested
			threadLock.release()
			############ Lock Released ############

			logtime = (time.time() - starting_point) 

			if LOG_EVENTS == True:
				fmt = '{0:30} {1:10} {2:20} {3:20} +{4:15} {5:15} \n'
				eventlog.write( fmt.format( str(datetime.datetime.now()), 
						    				("%.2f" % (logtime)),
						    				"HARVEST",
						    				str(line_num2),
						    				("%.5f" % (energy_harvested)), 
						    				str(self.node.current_energy)  )  )
			if LOG_HARVESTED_ENERGY == True:
				harvestedlog.write( ("%.2f" % float(logtime)) + " " +
									("%.5f" % float(energy_harvested)) + "\n" )

			if LOG_BATT_STATE == True:
				batterylog.write( ("%.2f" % float(logtime)) + " " +
									("%.5f" % float(self.node.current_energy)) + "\n" )

			index += 1

			if index == data_list.length():  # if we've reached the end of the test interval
				stop_all == False  # stop all
				break  # kill thread asap

			time.sleep(HARVEST_INTERVAL)
			


############################################
#
# Peripheral Functions
#
############################################


def get_harvesting_data(filename, data_list, start_time, stop_time):
	
	# first figure out t1 and t2
	t1 = start_time - HARVEST_START
	t2 = start_time
	
	while t1 != stop_time:
		# figure out which line numbers from the file you want
		line_num1 = (t1 / 30) + 2
		line_num2 = (t2 / 30) + 2

		# grab the lines we want
		line1 = (linecache.getline(filename, line_num1)).split()
		line2 = (linecache.getline(filename, line_num2)).split()
		linecache.clearcache()

		# get the irradiance values
		irr1 = line1[1]
		irr2 = line2[1]

		# calculate energy harvested
		energy_harvested = calc_energy_harvested(float(irr1), float(irr2), float(t1), float(t2))

		data_list.append((t2, energy_harvested))  # add energy harvested to data_list

		t1 += HARVEST_START
		t2 += HARVEST_START


def calc_energy_harvested(irr1, irr2, t1, t2):
		
	PANEL_AREA = 5.81 * 5.67  # units cm^2 --> Part is Cymbet CBC-PV01 Solar cell, 58.1mm x 56.7mm area
	PANEL_EFFICIENCY = .01  # assume 1%

	""" max independently confirmed 10%
		Green, Martin A., et al. "Solar cell efficiency tables (version 39)." 
		Progress in photovoltaics: research and applications 20.1 (2012): 12-20."""

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
	p1 = irr1 * PANEL_AREA * PANEL_EFFICIENCY
	p2 = irr2 * PANEL_AREA * PANEL_EFFICIENCY

	# calculate slope and intercept
	m = (p2 - p1) / (t2 - t1)
	b = p2 - (m * t2)

	# now calculate energy by integrating 
	energy = (  ( ((m * t2**2) / 2) + (b * t2) ) -
				( ((m * t1**2) / 2) + (b * t1) )   )

	return (energy / 1000)  # units of mJ



############################################
#
# Start of Main script
#
############################################

# variable for logging
LOG_EVENTS = True
LOG_HARVESTED_ENERGY = False
LOG_BATT_STATE = False

# event intervals in seconds / 1000
IDLE_UPDATE_INTERVAL  = 60  / 1000  # update idle energy consumption every minute
TX_UPDATE_INTERVAL 	  = 180 / 1000  # transmit data every 3 minutes
SENSE_UPDATE_INTERVAL = 180 / 1000  # sense every 3 minutes
SINK_UPDATE_INTERVAL  = 600 / 1000  # receive sink update every 10 minutes
HARVEST_INTERVAL      = 60  / 1000  # update harvested energy every 10 mintues

# start and stop times
HARVEST_START = 60
HARVEST_END = 300

# list containing list of energy harvested data points
harvesting_data = []

# Node capacity
START_CAPCITY = 1368  # 1368 mJ based on 100 uAH capacity battery

# list of devices that cnosume energy and how much energy they consume
energy_consumption = {'tx': 1, 'rx':1 , 'idle': 0.18612, 'sense': 1} 

# list containing nodes in the network
network = []

# create new node
window_node = EHN(1, START_CAPCITY, energy_consumption)

network.append(window_node)

get_harvesting_data("SetupB_merged_2010_11_3_2010_11_24.txt", harvesting_data, HARVEST_START, HARVEST_END)

for items in harvesting_data:
	print items

# create new threads
#thread1 = IdleThread(1, "idle", window_node)
#thread2 = TxThread(2, "tx", window_node)
#thread3 = SinkThread(3, "sink", network)
#thread4 = SenseThread(4, "sense", window_node)
#thread5 = HarvestEnergy(5, "harvest", window_node, "SetupB_merged_2010_11_3_2010_11_24.txt", HARVEST_START, HARVEST_END)

# log the start in the event log
#starting_point = time.time()  # timestamp when you start the simulation
#eventlog.write("Starting at " + str(datetime.datetime.now()) + " \n")
#eventlog.write("Starting Energy: " + str(window_node.storage_capacity) + "\n")

# start thread
#thread1.start()  # idle thread
#thread2.start()
#thread3.start()
#thread4.start()
#thread5.start()  # harvesting thread

#while stop_all == False:
	#print window_node.current_energy