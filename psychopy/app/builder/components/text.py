from _visual import * #to get the template visual component
from os import path

thisFolder = path.abspath(path.dirname(__file__))#the absolute path to the folder containing this path
iconFile = path.join(thisFolder,'text.png')

class TextComponent(VisualComponent):
    """An event class for presenting image-based stimuli"""
    def __init__(self, parentName, name='', text='', font='arial',
        units='window units', colour=[1,1,1], colourSpace='rgb',
        pos=[0,0], letterHeight=1, ori=0, times=[0,1]):
        #initialise main parameters from base stimulus
        VisualComponent.__init__(self, parentName, name=name, units=units, 
                    colour=colour, colourSpace=colourSpace,
                    pos=pos, ori=ori, times=times)
        self.type='Text'
        self.params['text']=Param(text, valType='code', allowedTypes=['str','code'],
            updates="never", allowedUpdates=["never","routine","frame"],
            hint="The text to be displayed")
        self.params['font']=Param(font, valType='str', allowedTypes=['str','code'],
            updates="never", allowedUpdates=["never","routine","frame"],
            hint="The font name, or a list of names, e.g. ['arial','verdana']")
        #change the hint for size
        del self.params['size']#because you can't specify width for text
        self.params['letterHeight']=Param(letterHeight, valType='code', allowedTypes=['num','code'],
            updates="never", allowedUpdates=["never","routine","frame"],
            hint="Specifies the height of the letter (the width is then determined by the font)")
    def writeInitCode(self,buff):
        #do we need units code?
        if self.params['units'].val=='window units': units=""
        else: units="units=%(units)s, " %self.params 
        #do writing of init
        buff.writeIndented("%(name)s=visual.TextStim(win=win, text=%(text)s, ori=%(ori)s\n" %(self.params)) 
        buff.writeIndented("    "+units+"pos=%(pos)s, height=%(letterHeight)s,\n" %(self.params))
        buff.writeIndented("    %(colourSpace)s=%(colour)s)\n" %(self.params))  