from django.http import HttpResponse
from django.shortcuts import render
from data.models import ErvEntry, VrfEntry
import csv, datetime

# Create your views here.
def index(request):
	return render(request, 'data/index.html', {})

def __date_parse(datestring_arg):
	# ISO 8601 specifies a universal datetime format as yyyyMMddTHHmmssZ
	fmt = r'%Y%m%dT%H%M%S'
	return datetime.datetime.strptime(datestring_arg, fmt)

def __hvac_range(cls, request, tstart, tend):
	print "HVAC RANGE for", cls, "from", tstart, "to", tend
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="commonsdata.csv"'
	writer = csv.writer(response)

	headers = cls.all_headers()
	writer.writerow(headers)

	q = cls.objects.filter(Time__gte=tstart, Time__lt=tend)

	# loop over all rows of queried data and write them
	for vrf_obj in q:
		csv_row = map(lambda h: vrf_obj.__dict__.get(h, ''), headers)
		writer.writerow(csv_row)
	return response

def vrf_csv(request):
	try:
		tstart = __date_parse(request.GET.get('tstart'))
	except:
		tstart = datetime.datetime.fromtimestamp(0)
	try:
		tend = __date_parse(request.GET.get('tend'))
	except:
		tend = datetime.datetime.now()
	return __hvac_range(VrfEntry, request, tstart, tend)
	

def erv_csv(request):
	try:
		tstart = __date_parse(request.GET.get('tstart'))
	except:
		tstart = datetime.datetime.fromtimestamp(0)
	try:
		tend = __date_parse(request.GET.get('tend'))
	except:
		tend = datetime.datetime.now()
	return __hvac_range(ErvEntry, request, tstart, tend)