from django.shortcuts import render
from commonssite.miscellaneous import VerisMonitor

# Create your views here.
def updates(request):
	m = request.session.get('monitor', None)
	if not m:
		m = VerisMonitor()
	else:
		m = VerisMonitor.deserialize(m)
	updates = m.get_new_data()
	request.session['monitor'] = m.serialize()
	return render(request, 'live_updates/veris_tables.html', {'monitor' : updates})
