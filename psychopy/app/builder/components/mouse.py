# Part of the PsychoPy library
# Copyright (C) 2011 Jonathan Peirce
# Distributed under the terms of the GNU General Public License (GPL).

from _base import *
from os import path
from psychopy.app.builder.experiment import Param

thisFolder = path.abspath(path.dirname(__file__))#the absolute path to the folder containing this path
iconFile = path.join(thisFolder,'mouse.png')

class MouseComponent(BaseComponent):
    """An event class for checking the mouse location and buttons at given timepoints"""
    def __init__(self, exp, parentName, name='mouse', startTime=0.0, duration='', save='final', 
            forceEndTrialOnPress=True, timeRelativeTo='routine'):
        self.type='Mouse'
        self.url="http://www.psychopy.org/builder/components/mouse.html"
        self.exp=exp#so we can access the experiment if necess
        self.exp.requirePsychopyLibs(['event'])
        #params
        self.order = ['name', 'startTime','duration']#make sure that 'name' is at top of dlg
        self.params={}
        self.params['name']=Param(name, valType='code', allowedTypes=[],
            hint="Even mice have names!")
        self.params['startTime']=Param(startTime, valType='code', allowedTypes=[],
            updates='constant', allowedUpdates=[],
            hint="The time that the mouse starts being checked")
        self.params['duration']=Param(duration, valType='code', allowedTypes=[],
            updates='constant', allowedUpdates=[],
            hint="The duration during which the mouse is checked")
        self.params['saveMouseState']=Param(save, valType='str',
            allowedVals=['final','on click', 'every frame', 'never'],
            hint="How often should the mouse state (x,y,buttons) be stored? On every video frame, every click or just at the end of the Routine?")
        self.params['forceEndTrialOnPress']=Param(forceEndTrialOnPress, valType='bool', allowedTypes=[],
            updates='constant', allowedUpdates=[],
            hint="Should a button press force the end of the routine (e.g end the trial)?")
        self.params['timeRelativeTo']=Param(timeRelativeTo, valType='str',
            allowedVals=['experiment','routine'],
            updates='constant', allowedUpdates=[],
            hint="What should the values of mouse.time should be relative to?")
    def writeInitCode(self,buff):
        buff.writeIndented("%(name)s=event.Mouse(win=win)\n" %(self.params))
        buff.writeIndented("x,y=[None,None]\n" %(self.params))
    def writeRoutineStartCode(self,buff):
        """Write the code that will be called at the start of the routine
        """
        #create some lists to store recorded values positions and events if we need more than one
        buff.writeIndented("#setup some python lists for storing info about the %(name)s\n" %(self.params))
        if self.params['saveMouseState'].val in ['every frame', 'on click']:
            buff.writeIndented("%(name)s.x = []\n" %(self.params))
            buff.writeIndented("%(name)s.y = []\n" %(self.params))
            buff.writeIndented("%(name)s.leftButton= []\n" %(self.params))
            buff.writeIndented("%(name)s.midButton= []\n" %(self.params))
            buff.writeIndented("%(name)s.rightButton= []\n" %(self.params))
            buff.writeIndented("%(name)s.time = []\n" %(self.params))
    def writeFrameCode(self,buff):
        """Write the code that will be called every frame
        """
        forceEnd = self.params['forceEndTrialOnPress'].val
        routineClockName = self.exp.flow._currentRoutine._clockName
        
        #only write code for cases where we are storing data as we go (each frame or each click)
        if self.params['saveMouseState'] not in ['every frame', 'on click'] and not forceEnd:
            return
        
        self.writeTimeTestCode(buff)#writes an if statement to determine whether to draw etc
        buff.setIndentLevel(1, relative=True)#because of the 'if' statement of the time test
        self.writeParamUpdates(buff, 'frame')
        
        #get a clock for timing
        if self.params['timeRelativeTo'].val=='experiment':clockStr = 'globalClock'
        elif self.params['timeRelativeTo'].val=='routine':clockStr = routineClockName
        
        #write param checking code
        if self.params['saveMouseState'].val == 'on click' or forceEnd:
            buff.writeIndented("buttons = %(name)s.getPressed()\n" %(self.params))
            buff.writeIndented("if sum(buttons)>0:#ie if any button is pressed\n")
            buff.setIndentLevel(1, relative=True)
        if self.params['saveMouseState'].val == 'on click':
            buff.writeIndented("x,y=%(name)s.getPos()\n" %(self.params))
            buff.writeIndented("%(name)s.x.append(x)\n" %(self.params))
            buff.writeIndented("%(name)s.y.append(y)\n" %(self.params))
            buff.writeIndented("%(name)s.leftButton.append(buttons[0])\n" %(self.params))
            buff.writeIndented("%(name)s.midButton.append(buttons[1])\n" %(self.params))
            buff.writeIndented("%(name)s.rightButton.append(buttons[2])\n" %(self.params))
            buff.writeIndented("%s.time.append(%s.getTime())\n" %(self.params['name'], clockStr))
            
        #does the response end the trial?
        if forceEnd==True:
            buff.writeIndented("#abort routine on response\n" %self.params)
            buff.writeIndented("continueRoutine=False\n")
            
        #dedent
        if self.params['saveMouseState'] == 'on click' or forceEnd:
            buff.setIndentLevel(-2, relative=True)#'if' statement of the time test and button check
        else: buff.setIndentLevel(-1, relative=True)#because of the 'if' statement of the time test
    def writeRoutineEndCode(self,buff):
        #some shortcuts
        name = self.params['name']
        store = self.params['saveMouseState'].val#do this because the param itself is not a string!
        #check if we're in a loop (so saving is possible)
        if len(self.exp.flow._loopList):
            currLoop=self.exp.flow._loopList[-1]#last (outer-most) loop
        else: currLoop=None
        if store!='nothing' and currLoop and currLoop.type=='StairHandler':
            buff.writeIndented("#NB PsychoPy doesn't handle a 'correct answer' for mouse events so doesn't know how to handle mouse with StairHandler")
        if store == 'final' and currLoop!=None:
            buff.writeIndented("#get info about the %(name)s\n" %(self.params))
            buff.writeIndented("x,y=%(name)s.getPos()\n" %(self.params))
            buff.writeIndented("buttons = %(name)s.getPressed()\n" %(self.params))
            if currLoop.type!='StairHandler':
                buff.writeIndented("%s.addData('%s.x',x)\n" %(currLoop.params['name'], name))
                buff.writeIndented("%s.addData('%s.y',y)\n" %(currLoop.params['name'], name))
                buff.writeIndented("%s.addData('%s.leftButton',buttons[0])\n" %(currLoop.params['name'], name))
                buff.writeIndented("%s.addData('%s.midButton',buttons[1])\n" %(currLoop.params['name'], name))
                buff.writeIndented("%s.addData('%s.rightButton',buttons[2])\n" %(currLoop.params['name'], name))
        elif store != 'never' and currLoop!=None:
            buff.writeIndented("#save %(name)s data\n" %(self.params))
            for property in ['x','y','leftButton','midButton','rightButton','time']:
                buff.writeIndented("%s.addData('%s.%s',%s.%s)\n" %(currLoop.params['name'], name,property,name,property))