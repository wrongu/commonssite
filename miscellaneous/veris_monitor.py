# veris-monitor
#
# monitors the page and prints out when things change
import time, re, datetime
from commonssite.scrapers import veris2

INTERVAL = 5.0 # seconds
unit_parser = re.compile(r'[^(]+\((\w*)\)')	

class Monitor:

	thresholds = {
		'kW' : 1.0,
		'kWh' : 1.0,
		'Volts' : 1.0,
		'Amps' : 1.0,
		'' : .1,
		'Hz': 0.5,
		'Default' : 0.0
	}
	ignore = ['Hz', '', 'Default']

	last2 = {}
	last3 = {}
	last4 = {}
	nupdates = 0
	last_update = {}

	def get_new_data(self):
		update_dict = {
			'Device 2' : [],
			'Device 3' : [],
			'Device 4' : []
		}
		print "getting update #%d" % self.nupdates, datetime.datetime.now()
		# get latest
		d2, d3, d4 = veris2.get_data()
		# compare to last_data
		if self.nupdates != 0:
			for header, value in d2.iteritems():
				if self.changed(header, self.last2.get(header), value):
					print "Device 2,", header.ljust(30, ' '), self.last2.get(header,'').ljust(6,' '), " ==> ", d2.get(header)
					update_dict['Device 2'].append((header, self.last2.get(header), d2.get(header)))
			for header, value in d3.iteritems():
				if self.changed(header, self.last3.get(header), value):
					print "Device 3,", header.ljust(30, ' '), self.last3.get(header,'').ljust(6,' '), " ==> ", d3.get(header)
					update_dict['Device 3'].append((header, self.last3.get(header), d3.get(header)))
			for header, value in d4.iteritems():
				if self.changed(header, self.last4.get(header), value):
					print "Device 4,", header.ljust(30, ' '), self.last4.get(header,'').ljust(6,' '), " ==> ", d4.get(header)
					update_dict['Device 4'].append((header, self.last4.get(header), d4.get(header)))
		self.last2 = d2
		self.last3 = d3
		self.last4 = d4
		self.nupdates += 1
		self.last_update = update_dict
		return self.last_update 

	def get_old_data(self):
		return self.last_update 

	def serialize(self):
		return (self.nupdates, self.last2, self.last3, self.last4, self.last_update)

	@classmethod
	def deserialize(cls, ser):
		m = Monitor()
		m.nupdates, m.last2, m.last3, m.last4, m.last_update = ser
		return m

	def unit(self, name):
		try:
			return unit_parser.match(name).group(1)
		except:
			return 'Default'

	def thresh(self, name):
		return self.thresholds.get(self.unit(name), 0.0)

	def changed(self, name, val1, val2):
		if name == 'Time' or self.unit(name) in self.ignore:
			return False
		th = self.thresh(name)
		try:
			return abs(float(val2) - float(val1)) > th
		except:
			return val1 != val2

	def set_ignored(self, units):
		self.ignore = units

	def get_ignored(self):
		return dict([(u, u not in self.ignore) for u in self.thresholds.keys()])

	def set_thresh(self, unit, val):
		self.thresholds[unit] = val

	def get_thresholds(self):
		return self.thresholds

if __name__ == '__main__':
	from sys import argv
	sleepstyle = True
	if len(argv) > 1:
		opt = argv[1]
		sleepstyle = (opt != '-e')
	m = Monitor()
	while True:
		try:
			m.get_new_data()
			if sleepstyle:
				print "next update in %f seconds" % INTERVAL
				time.sleep(INTERVAL)
			else:
				print "press Enter for a new reading"
				raw_input()
		except KeyboardInterrupt:
			break
	print "--done--"
