import tkinter
from tkinter.messagebox import showerror
import numpy as np
from random import randint
import time


def TestValidLocation(x,y,r):
    if ((x-300)**2+(y-300)**2)**0.5<250-1.5*r:
        return True
    else:
        return False


def CalculateInterSpotForce(locations):
    q = 1
    DistanceAngle = []
    #calculate the distance and the angle

    for i in range(len(locations)):
        IndividualDistanceAngle = []
        for j in range(len(locations)):
            if i!=j:
                x1,x2= locations[i][0],locations[j][0]
                y1,y2= -locations[i][1],-locations[j][1]
                
                distance = ((y2-y1)**2+(x2-x1)**2)**0.5
                try:
                    #calculating angle for ith particle
                    angle = abs(np.arctan(-(y2-y1)/(x2-x1)))   
                except ZeroDivisionError:
                    angle = np.pi/2
                if x1<x2:
                        angle = np.pi-angle
                if y1<y2:
                        angle = -angle #changing the sign
                IndividualDistanceAngle.append([distance,angle])
        DistanceAngle.append(IndividualDistanceAngle)    
    
    
    Force = []
    for i in range(len(DistanceAngle)):
        Fx = 0
        Fy = 0
        for j in range(len(DistanceAngle[i])):
            theta = DistanceAngle[i][j][1]
            r = DistanceAngle[i][j][0]
            if r!=0:
                Fx += np.cos(theta)*q**2/r**2
                Fy  += np.sin(theta)*q**2/r**2
            else: #if distance is zero to keep the dots moving
                Fx += randint(-10,10)/100
                Fx += randint(-10,10)/100
        Force.append([Fx,Fy])
    return Force


def CalculateWallForce(location,q_den):
    q = 1
    steps = 1000
    stepsize = 2*np.pi/steps
    R = 250
    Rs = ((300-location[0])**2+(300-location[1])**2)**0.5
    
    DeltaX = location[0]-300
    DeltaY = -(location[1]-300)
    if DeltaX != 0:
        theta0 = abs(np.arctan(DeltaY/DeltaX)) #angle made with the center
    else:
        theta0 = np.pi/2
    
    #accumulators of force
    Fx = 0
    Fy = 0
    for i in range(steps):
        theta = i*2*np.pi/steps
        Denominator = (R**2+Rs**2-2*R*Rs*np.cos(theta))
        if Denominator==0:
            F = 0
        else:
            F = -(q*q_den)/(R**2+Rs**2-2*R*Rs*np.cos(theta))*stepsize
        
        if location[0]>300 and location[1]<300:
            Quadrant = 1
            Angle = theta0+theta 
        elif location[0]<300 and location[1]<300:
            Quadrant = 2
            Angle = np.pi-theta0+theta
    
        elif location[0]<300 and location[1]>300:
            Quadrant = 3
            Angle = np.pi+theta0+theta
        else:
            Quadrant = 4
            Angle = 2*np.pi-theta0+theta
        Fx += F*np.cos(Angle)
        Fy += F*np.sin(Angle)
    return [Fx,Fy]


def RunSimulation(NumberSpots,SpotRadius):
    global canvas, SimulateButton, locations, WallCharge, Perturb
    try:
        q_den = float(WallCharge.get())/(2*np.pi)
    except:
        showerror(root, "Invalid entry for charge density. Using default value of 2*pi")
        q_den = 2*np.pi
    SimulateButton.config(state=tkinter.DISABLED)
    Rs = SpotRadius #radius of the spot
    q = 1 #making charge 1 
    locations = [] #for storing the location of spots
    for i in range(NumberSpots):
        valid = False
        while(not(valid)):
            tempLocation = [randint(50,550),randint(50,550)]
            valid = TestValidLocation(tempLocation[0], tempLocation[1], Rs)
        locations.append(tempLocation)
        
    #drawing the spots
    for i in range(NumberSpots):
        canvas.create_oval(locations[i][0]-Rs,locations[i][1]-Rs,locations[i][0]+Rs,locations[i][1]+Rs,outline="blue",fill="blue",tags="spot%s" %(str(i+1)))
    
    #Calculating direction of force and performing the animation
    
    Force = CalculateInterSpotForce(locations)
    ThresholdNoise = 0
    
    #for adding perturbation
    
    Perturb = False
    
    for count in range(500000):
       # time.sleep(0.080)
        

        for i in range(len(Force)):
            WallForce = CalculateWallForce(locations[i],q_den)
            Fx = WallForce[0]+Force[i][0]
            Fy = WallForce[1]+Force[i][1]
            value = 20/(1.05**count)
            RateX = int(value*abs(Fx)/(Fx**2+Fy**2)**0.5)
            RateY = int(value*abs(Fy)/(Fx**2+Fy**2)**0.5)
            if RateX<1:
                RateX = 1
            if RateY<1:
                RateY = 1
            if Fx>ThresholdNoise:
                canvas.move("spot%s" %str(i+1), RateX, 0)
                locations[i][0]+=RateX
            elif Fx<-ThresholdNoise:
                canvas.move("spot%s" %str(i+1), -RateX, 0)
                locations[i][0]-=RateX
            if Fy>ThresholdNoise:
                canvas.move("spot%s" %str(i+1), 0, -RateY)   #need to check the sign
                locations[i][1]-=RateY
            elif Fy<-ThresholdNoise:
                canvas.move("spot%s" %str(i+1), 0, +RateY)
                locations[i][1]+=RateY
                
            root.update()
            
        if(Perturb):
            print("value::", value, "  RateX::", RateX)
            for i in range(len(locations)):
                valuex = randint(-10,10)
                valuey = randint(-10,10)
                locations[i][0]+=valuex
                locations[i][1]+=valuey
                canvas.move("spot%s" %str(i+1), valuex, valuey) #redrawing the spots
            Perturb = False
            print(locations)
            
        #test if the location is valid and exit until all locations are invalid in when changing both in x and y makes difference
        Force = CalculateInterSpotForce(locations)
    
def BaseSimulation(frame):
    global canvas
    try:
        canvas.destroy()
        SimulateButton.config(state=tkinter.ACTIVE)
    except:
        pass
    canvas = tkinter.Canvas(frame,width=600, height=600,bg="#191919")
    canvas.pack()
    canvas.create_oval(50,50,550,550,outline="white")
    
def PerturbFunc():
    global Perturb
    Perturb = True

def SetParameters(frame, sideframe):
    global SimulateButton, WallCharge #to activate it and deactivate it from other functions
    #number of spots to be selected by the user
    NumberofSpots = tkinter.Label(frame,text="Number of Spots")
    NumberofSpots.grid(row=0,column=0,padx=10,pady=10)
    SpotNum = tkinter.IntVar(frame)
    SpotNum.set(1)
    NumSpotlist = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]
    SpotOption = tkinter.OptionMenu(frame,SpotNum,*NumSpotlist)
    SpotOption.grid(row=0, column = 1)
    
    #Spot radius
    SpotRadiusText = tkinter.Label(frame,text="Radius Size (pixels):")
    SpotRadiusText.grid(row=1,column=0,padx=10,pady=10)
    
    SpotRadius = tkinter.IntVar(frame)
    SpotRadius.set(10)
    SpotRadiuslist = [5,10,15,20,25,30,35,40]
    SpotRadiusOption = tkinter.OptionMenu(frame,SpotRadius,*SpotRadiuslist)
    SpotRadiusOption.grid(row=1, column = 1,padx= 10, pady=10)
    
    
    
    #ChargeRatio
    WallChargeRatioLabel = tkinter.Label(frame,text="Charge Ratio") 
    WallChargeRatioLabel.grid(row=2, column=0)
    WallCharge = tkinter.StringVar()
    WallChargeEntry = tkinter.Entry(frame,width=8,textvariable=WallCharge)
    WallCharge.set(str(2*np.pi))
    WallChargeEntry.grid(row=2, column=1)

    #feature to add later
    #Colorlist = ["Only Borders", "With Color", "Color at the end"]
    #SpotOption = tkinter.OptionMenu(frame,SpotNum,*list)
    
    
    SimulateButton = tkinter.Button(frame,text="Simulate",command=lambda:RunSimulation(SpotNum.get(),SpotRadius.get()))
    SimulateButton.grid(row=3, column=0,padx=10,pady=20)
    
    PerturbButton = tkinter.Button(frame,text="Perturb",command=lambda:PerturbFunc())
    PerturbButton.grid(row=3, column=1,padx=10,pady=20)
    
    ClearButton = tkinter.Button(frame,text="Clear",command=lambda:BaseSimulation(sideframe))
    ClearButton.grid(row=4, column=0,padx=10)

    QuitButton = tkinter.Button(frame,text="Quit",command=lambda:root.destroy())
    QuitButton.grid(row=4, column=1)

root = tkinter.Tk()
root.title("Simulation")
root.geometry("900x600")
root.resizable(width=False,height=False)
FrameParam = tkinter.Frame(root,width=200, height=600)
FrameParam.grid(row=0,column=1)
FrameDiagram = tkinter.Frame(root, width =600, height=600)
FrameDiagram.grid(row=0,column=0)


SetParameters(FrameParam, FrameDiagram)
BaseSimulation(FrameDiagram)


root.mainloop()
