from django.shortcuts import render
from commonssite.miscellaneous import VerisMonitor

def update_time_tuple(m):
	update_dict = m.get_new_data()
	telapse = 0.0
	if 'Time' in update_dict:
		telapse = update_dict.pop('Time')
	return update_dict, telapse

# Create your views here.
def initial(request):
	# create monitor object fresh. stored in session for updates.
	m = VerisMonitor()
	update_dict, telapse = update_time_tuple(m)
	request.session['monitor'] = m.serialize()
	settings = m.get_settings()
	return render(request, 'live_updates/monitor_wrapper.html', {'monitor' : update_dict, 'settings' : settings, 'telapse' : telapse})

def refresh(request):
	# get monitor from session
	m = request.session.get('monitor', None)
	if not m:
		m = VerisMonitor()
	else:
		m = VerisMonitor.deserialize(m)
	# update threshold values
	print "getting threshold values"
	for k, (t, e) in m.get_settings().items():
		try:
			new_thresh = float(request.GET.get(k, t))
		except:
			print request.GET.get(k), "could not be parsed as a float"
		new_en = request.GET.get("%s-en" % k) or str(e)
		print k, new_thresh, new_en, (new_en.lower() == "true")
		m.update_setting(k, (new_thresh, (new_en.lower() == "true")));
	# refresh the data
	update_dict, telapse = update_time_tuple(m)
	# return rendered inner-page (just tables)
	request.session['monitor'] = m.serialize()
	settings = m.get_settings()
	return render(request, 'live_updates/veris_tables.html', {'monitor' : update_dict, 'settings' : settings, 'telapse' : telapse})