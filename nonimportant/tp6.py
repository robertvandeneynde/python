def my_range(a,b):
	liste=[]
	while a<b:
		liste.append(a)
		a+=1
	return liste
	
def my_range_step(a,b,step):
	liste=[]
	while a<b:
		liste.append(a)
		a+=step
	return liste

def linspace(begin,end,n):
	liste=[]
	x=0
	step=(end-begin)/(n-1)
	while begin<end:
		liste.append(begin+x*step)
		x+=1
	return liste
	
import math
EPS=1E-6
BORNE=10000

def Euler():
	somme=0
	terme=1
	n=1
	while n<BORNE and terme>=EPS:
		terme=6*(1.0/n**2)
		somme+=terme
		n+=1
	return math.sqrt(somme)

def approchePi():
	n=1
	terme=1/3.0
	somme=terme
	while terme>=EPS and n<BORNE:
		n+=1
		terme=1.0/(4*n-3)/(4*n-1)
		somme+=terme
	return 8*somme

def Leibniz():
	n=1
	signe=1
	terme=1
	somme=terme
	while terme>=EPS and n<BORNE:
		n+=1
		signe=-signe
		terme=signe*1.0/(2*n+1)
		somme+=terme
	return 4*somme
	
def arctan(x):
	n = 1
	c = 1
	c1 = 1
	terme0 = x / (1.0 + x**2)
	terme1 = terme0 * x
	somme = 1
	while c>=EPS and n<BORNE:
		c *= 2*n / (2*n + 1)
		n += 1
		c1 *= terme1
		somme += c*c1
	return terme0 * somme

def pi_approche():
	a=arctan(1.0/5)
	b=arctan(1.0/239)
	return 16*a-4*b

def rac2():
	(x,y) = (1,2)
	n=1
	while n<BORNE and y-x>=EPS:
		n+=1
		x=2.0/(y)
		y=(x+y)/2.0
	return (x,y)

def newton2(r):
	x=1
	old=0
	while n<BORNE and abs(x-old):
		old=x
		x=0.5*(x+r/x)
	return x






