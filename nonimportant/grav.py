#coding: utf-8
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

dtms = 10 # ms/frame
dt = dtms / 1000.0 #s/frame
slow = 1
def data_gen():
    import sys
    m1,m2 = 50,1 #kg
    v0 = 50 # m/s
    d0 = 20 # m
    
    G = 1000
    
    # MCU : a = v² / R
    # F = m v² / R
    # G M / R² = v² / R
    # G M / R = v²
    # G M / v² = R
    # 1000 * 50 / (50 * 50) = 20
    if len(sys.argv) >= 5:
        m1,m2 = sys.argv[1],sys.argv[2] #kg
        v0 = sys.argv[3] # m/s
        d0 = sys.argv[4] # m
    
    M = np.array([float(m1), float(m2)])
    X = np.array([[0.0,0.0], [0.0,float(d0)]]) # m
    V = np.array([[0.0,0.0], [float(v0),0.0]]) # m/s
    t = 0
    while t < 20:
        D = X[1] - X[0]
        f = G * M[0] * M[1] / D.dot(D)
        direction = D / np.linalg.norm(D)
        F = np.array([f * direction, -f * direction])
        A = np.array([f/m for f,m in zip(F,M)]) # F / M doesnt work
        
        yield t, X, V, A, F
        
        V += A * dt
        X += V * dt
        
        t += dt
    
    return 
    cnt = 0
    while cnt < 1000:
        cnt += 1
        t += 0.05
        yield t, np.sin(2*np.pi*t) * np.exp(-t/10.)

AXES = 50

fig, ax = plt.subplots()
#point_b,point_r,vec_green = ax.plot([],[],'bo', [],[],'ro', [],[],'g', lw=2)
ax.set_ylim(-AXES, AXES)
ax.set_xlim(-AXES, AXES)
ax.grid()
#xdata, ydata = [], []

SCALEV = 0.1
SCALEA = 0.020
def run(data):
    # update the data
    t,X,V,A,F = data
    #xdata.append(X[0][0])
    #ydata.append(X[0][1])
    #xmin, xmax = ax.get_xlim()

    #if t >= xmax:
        #ax.set_xlim(xmin, 2*xmax)
        #ax.figure.canvas.draw()
    (x1,y1),(x2,y2) = X
    (vx1,vy1),(vx2,vy2) = V
    (ax1,ay1),(ax2,ay2) = A
    (fx1,fy1),(fx2,fy2) = F
    
    ax.lines = []
    ax.plot([x1],[y1],'ro')
    ax.plot([x2],[y2],'bo')
    for c,T,scale in zip('gy', (V,A), (SCALEV,SCALEA)):
        for x,t in zip(X,T):
            #x = (5,2)
            #t = (1,2) #vitesse
            points = [x, x + scale * t]
            ax.plot(*np.array(points).transpose(), color=c, lw=2)

ani = animation.FuncAnimation(fig, run, data_gen, blit=False, interval=dtms*slow, #ms/frame
    repeat=False)
plt.show()
