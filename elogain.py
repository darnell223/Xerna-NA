def getaddelo(elo):
	if elo <= 100:
		return(15)
	elif elo <= 300:
		return(20)
	elif elo <= 600:
		return(30)
	else:
		return(10)

def getloseelo(elo):
	if elo <= 100:
		return(5)
	elif elo <= 300:
		return(10)
	elif elo <= 600:
		return(15)
	else:
		return(10)