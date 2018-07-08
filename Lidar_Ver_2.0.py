#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 11:35:20 2017

@author: MacArseniy
"""
import sys
import numpy as np

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar


form_class = uic.loadUiType("mainwindow2.ui")[0]

class Window(QMainWindow, form_class):  
    mpl_figure = Figure()
    lines_pic = {}
    lines = {} 
    direct = 1
    hLidar = 0.8
    
    #Angle_Gradusy
    x_Angle_GR = [0]
    
    y_Angle_GR = np.arange(1,2,1)
    
    z_Angle_GR = np.arange(-90,90,30)
    
    
    LidarPosition = np.matrix([0,0,hLidar])
    
    TochkaPosition = [direct,0,0]
    
    V_K = []
    
    LabelAr = []
    def __init__(self):
        super(Window, self).__init__()
        self.setupUi(self)
        self.home() 

    def home(self):
        self.axes = self.mpl_figure.add_subplot(111, projection='3d')

        self.canvas = FigureCanvas(self.mpl_figure)
        self.mplVL.addWidget(self.canvas)
        self.canvas.draw()
        
        
        self.toolbar = NavigationToolbar(self.canvas, self, coordinates = True)
        self.addToolBar(self.toolbar)
        
        self.AddButton.clicked.connect(self.AddButton_OnClick)
        
        self.Y_Angle_Start.setText("1")
        self.Y_Angle_End.setText("3")
        self.Z_Angle_Start.setText("-60")
        self.Z_Angle_End.setText("60")
        self.HLidar.setText("0.4")
        
        self.Y_step.setText("1")
        self.Z_step.setText("30")
        self.show()
        
    def onChanged(self, text):
        self.hLidar = int(text)
        
    def AddButton_OnClick(self): 
        hLidat_text = self.HLidar.text()
        Y_Angle_Start = float(self.Y_Angle_Start.text())
        Y_Angle_End = float(self.Y_Angle_End.text())
        Z_Angle_Start = float(self.Z_Angle_Start.text())
        Z_Angle_End = float(self.Z_Angle_End.text())
        
        Y_step = float(self.Y_step.text())
        Z_step = float(self.Z_step.text())
        
        self.hLidar = float(hLidat_text)
        self.LidarPosition = np.matrix([0,0,self.hLidar])
        self.axes.cla()
        self.y_Angle_GR = np.arange(Y_Angle_Start,Y_Angle_End,Y_step)
        self.z_Angle_GR = np.arange(Z_Angle_Start,Z_Angle_End,Z_step)
        self.Draw()
        self.canvas.draw()
                
    

    
    def translateToRadians(self):
        T_x_Angle = []
        T_y_Angle = []
        T_z_Angle = []
        for i in self.x_Angle_GR:
            T_x_Angle.append(i*np.pi/180)
        for i in self.y_Angle_GR:
            T_y_Angle.append(i*np.pi/180)
        for i in self.z_Angle_GR:
            T_z_Angle.append(i*np.pi/180)    
        return T_x_Angle,T_y_Angle,T_z_Angle

    def peresech(self,x2,y2,z2):
        x1 = 0
        y1 = 0
        t = 0
        z1 = self.hLidar
        if z1 != z2:    
            t = (-z1)/(z2-z1)
            x = t*(x2-x1)+x1
            y = t*(y2-y1)+y1
            z=0
            self.dlina(x,y,z)
        else:
            print("Не пересекается с плоскотью земли")
            for i in self.V_K:
                self.LabelAr.append(0) 
    
    def dlina(self,x,y,z):
        x1 = 0
        y1 = 0
        z1 = self.hLidar
        for i in self.V_K:
            self.LabelAr.append(np.sqrt((x-x1)**2+(y-y1)**2+(z-z1)**2)) 
    
    def MatrixPovorota(self,a,b,c):
        MX = np.matrix([[1,0,0],[0,np.cos(a),-np.sin(a)],[0,np.sin(a),np.cos(a)]])
        MY = np.matrix([[np.cos(b),0,np.sin(b)],[0,1,0],[-np.sin(b),0,np.cos(b)]])
        MZ = np.matrix([[np.cos(c),-np.sin(c),0],[np.sin(c),np.cos(c),0],[0,0,1]])
        MP = np.dot(MZ,MY,MX)
        return MP
    
    def Main(self,x_Angle,y_Angle,z_Angle):
        for i in y_Angle: 
            index_i = 0 #перемещение по массиву V_K
            index_j = 0 #перемещение по массиву V_K[index_i]
            self.V_K.clear()
            self.LabelAr.clear()
            self.V_K.append([])
            index_j = 0
            for j in z_Angle:
                MP = self.MatrixPovorota(0,i,j)
                self.V_K[index_i].append(np.dot(MP,self.TochkaPosition))
                z = self.V_K[index_i][index_j].item(2)
                self.V_K[index_i][index_j] = [self.V_K[index_i][index_j].item(0),self.V_K[index_i][index_j].item(1),self.hLidar + z]
                index_j += 1
            index_i+=1
            L=0
            for PEREM in range(len(self.V_K)):
                for i in range(len(self.V_K[PEREM])):
                    x = self.LidarPosition.item(0)
                    y = self.LidarPosition.item(1)
                    z = self.LidarPosition.item(2)
                    x1 = self.V_K[PEREM][i][0]
                    y1 = self.V_K[PEREM][i][1]
                    z1 = self.V_K[PEREM][i][2]
                    self.peresech(x1,y1,z1)
                    self.axes.plot([x,x1],[y,y1],[z,z1-self.hLidar],label=self.LabelAr[L])
                    self.axes.legend(ncol=1, bbox_to_anchor=(0.1,1),fancybox=True,shadow=False,title='Lenght')
                    L+=1
        
            
    def Draw(self):
        x_Angle,y_Angle,z_Angle = self.translateToRadians()
        self.Main(x_Angle,y_Angle,z_Angle)
        
       
def run():
    app = QApplication(sys.argv)
    
    GUI = Window()
    app.exec_()

if __name__ == "__main__":
    run()
        

