#!/usr/bin/env python
'''
Created on Mar 2, 2012

@author: Arif Widi Nugroho <arif@sainsmograf.com>

Thorn -- A Windrose Creator
'''

import sys
from cStringIO import StringIO


from PyQt4.QtCore import *
from PyQt4.QtGui import *

import numpy as np
from numpy.random import random, random_integers

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.artist import setp


from windrose import WindroseAxes


class Qt4MplCanvas(FigureCanvas):
    '''Class to represent the FigureCanvas widget'''
    
    def __init__(self, parent):
        
        # windrose test plot
        self.fig = Figure(facecolor='w', edgecolor='w')
        rect = [0, 0.15, 1, 0.7]
        self.axes = self.fig.add_axes(WindroseAxes(self.fig, rect, axisbg='w'))
        
        # initialize the canvas where the Figure renders into
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        
        # we define the widget as expandable
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # notify the system of updated policy
        FigureCanvas.updateGeometry(self)
    
    def plot(self, windir, windspeed, windfrequency):
        self.windir = []
        self.windspeed = []
        
        for i, frequency in enumerate(windfrequency):
            for n in range(frequency):
                self.windir.append(windir[i])
                self.windspeed.append(windspeed[i])
        
        self.axes.clear()
        self.axes.bar(self.windir, self.windspeed, normed=True, opening=0.8, edgecolor='white')
        l = self.axes.legend(borderaxespad=-3.8)
        setp(l.get_texts(), fontsize=8)
        
        # force redraw the canvas
        self.fig.canvas.draw()
        

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle('Thorn - A Windrose Generator')
        self.main_widget = QWidget(self)
        
        vbl = QGridLayout(self.main_widget)
        
        # instantiate our Matplotlib canvas widget
        self.mplcanvas = Qt4MplCanvas(self.main_widget)
        
        # instantiate the navigation toolbar
        self.mpltoolbar = NavigationToolbar(self.mplcanvas, self.main_widget)
        
        # instantiate text area
        self.data_editor = QTextEdit(self.main_widget)
        
        # render button
        self.render_button = QPushButton(self.main_widget)
        self.render_button.setText('Render')
        
        # create sample plot
        windir = random(10)*360
        windspeed = random(10)*6
        windfrequency = random_integers(1, 25, 10)
        self.mplcanvas.plot(windir, windspeed, windfrequency)
        
        # put sample data in the text editor
        self.data_editor.setPlainText(construct_text_data(windir, windspeed, windfrequency))
        
        # pack these widget into the vertical box
        vbl.addWidget(self.mplcanvas, 0, 0)
        vbl.addWidget(self.mpltoolbar, 1, 0)
        vbl.addWidget(self.data_editor, 0, 1)
        vbl.addWidget(self.render_button, 1, 1)
        
        # set the focus on the main widget
        self.main_widget.setFocus()
        
        # set the central widget of MainWindow to main_widget
        self.setCentralWidget(self.main_widget)
        
        self.connect(self.render_button, SIGNAL('clicked()'), self.render)
    
    def render(self):
        windir, windspeed, frequency = parse_text_data(str(self.data_editor.toPlainText()))
        self.mplcanvas.plot(windir, windspeed, frequency)


def construct_text_data(windir, windspeed, windfrequency):
    buff = StringIO()
    buff.write('# windir windspeed frequency\n')
    
    wind_data = zip(windir, windspeed, windfrequency)
    
    for direction, speed, frequency in wind_data:
        buff.write('%.2f %.2f %d\n' % (direction, speed, frequency))

    return buff.getvalue()


def parse_text_data(data):
    lines = data.splitlines()
    windir = []
    windspeed = []
    windfrequency = []
    
    for line in lines:
        line_ = line.strip()
        if len(line) < 1:
            continue
        if line[0] == '#':
            continue
        wind = line.split()
        if len(wind) != 3:
            continue
        try:
            direction = float(wind[0])
            speed = float(wind[1])
            frequency = int(wind[2])
        except ValueError:
            continue
        
        windir.append(direction)
        windspeed.append(speed)
        windfrequency.append(frequency)
    
    return windir, windspeed, windfrequency


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    app.exec_()
    