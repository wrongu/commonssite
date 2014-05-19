import time
from timeseries import helpers as h

class ScraperBase(object):
	"""A scraper base class which takes care of shared functionality

	The old scraping method worked by keeping a schedule of tasks and executing a scraper every 20 minutes or so.
	This version works by logging new data as frequently as possible (tagged with temporary=True), and then later
	using compute_average_of_temporaries() to save data points permanently.
	"""

	def __init__(self, model_class, registry_instance):
		self._model = model_class
		self._registry = registry_instance

	def compute_average_of_temporaries(self):
		"""Take an average or median of all measurements (since the last permanent one) and save it.
		"""
		last_permanent = self._model.objects.filter(temporary=False).last()
		data_points = self._model.objects.filter(temporary=True, Time__gt=last_permanent.Time).order_by('Time')
		# first, separate the big queryset of points into multiple smaller lists based on their index
		indexed_objects = h.split_on_indexes(data_points)
		# there will be one new averaged object inserted per index
		for index, objects in indexed_objects.iteritems():
			# numeric types are averaged; all others are plurality vote
			# note that the interval is NOT assumed to be regular; votes and averages are weighted by the span of
			# time between any two measurements
			# running average is computed using the formula for the area of a trapezoid (we assume that a linear fit between points is good enough)
			prev_point = objects[0] # the 'previous' value
			total_span = 0.0
			model_average = {} # map from member => (current average or votes)
			value_fields = self._model.get_field_names()
			for i, curr_point in enumerate(objects[1:]):
				span_seconds = h.timedelta_seconds(curr_point.Time - prev_point.Time)
				total_span += span_seconds
				for f in self._model._meta.fields:
					if f.get_attname() in value_fields: # this ignores 'id', 'temporary', 'Time', and indexes
						# NUMERIC TYPES: running average
						if f.get_internal_type() in h.model_types['numeric']:
							pass
						# ALL OTHER TYPES: plurality vote
						else:
							pass

			tend = objects[-1].Time
			# construct the object from a kwarg dict
			kwargs = {'temporary' : False, 'Time' : tend}

	def status_ok(self):
		self._registry.status = 2

	def status_format_error(self):
		self._registry.status = 1

	def status_comm_error(self):
		self._registry.status = 0

	def get_and_save_single(self):
		try:
			for new_data in self.get_data():
				new_data.temporary = True
				new_data.save(force_insert=True)
			print '=================='
			print '%s done at %s' % (self.__class__.__name__, time.time())
		except Exception as e:
			print "Scraper error that wasn't caught by subclass!"
			print e
			self.status_comm_error()
		finally:
			self._registry.save() # update status in the database

	def get_data(self):
		"""Return a list of TimeseriesBase (subclass) models. get_data must be implemented by subclasses of ScraperBase
		"""
		self.status_comm_error()
		return []
