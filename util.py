import math


def fmtTime(tim):
	hr = math.floor(tim/3600) if tim >= 3600 else 0
	min = math.floor((tim%3600)/60) if tim >= 60 else 0
	sec = math.floor(tim%60)
	
	smin = '0'+str(min) if min<10 else str(min)
	ssec = '0'+str(sec) if sec<10 else str(sec)
	return (str(hr) + ':' if hr>0 else '') + smin + ':' + ssec