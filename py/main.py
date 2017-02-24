import sys

class GamePadSwButton(object):
    hw_btn_attr_names = ['kind', 'add', 'data']

    def __init__(self, abbreviation, name, hw_btn, trigger_data):
        self.hw_btn = hw_btn
        self.trigger_data = tuple(trigger_data)
        self._state = False
        self.name = name
        self.abbr = abbreviation
     
    @property
    def state(self):
        self.update_state()
        return self._state

    #def kind(self):
    #    return self.hw_btn.kind

    def __getattr__(self, name):
        if name in self.hw_btn_attr_names:
            return self.hw_btn.__dict__[name]
        elif name == 'state':
            print('NAME IS STATE')
            self.update_state()
            return self.state
        else:
            return self.__dict__[name]

    def update_state(self):
        if self.trigger_data == self.hw_btn.data:
            self._state = True
        else:
            self._state = False

    def __str__(self):
        return ''.join([str(word) for word in ['type=', self.kind,
                        ', add= ',self.add,
                        ', name="',self.name,
                        '", state= ', self.state,
                        ', hwdata=', self.data,
                        ', trigger_data=', self.trigger_data]])
           
class GamePadSwStick():
    def __init__(self, abbreviation, name, hw_btn1, hw_btn2):
        self.abbr = abbreviation
        self.name = name
        self.hw1 = hw_btn1
        self.hw2 = hw_btn2
        self._dir = [0,0]

    @property
    def dir(self):
        self._dir = [self.hw1.data, self.hw2.data]
        return self._dir

    def __str__(self):
        return ''.join([str(word) for word in [
                        self.abbr,' = ',self.name, ' = ', self.dir
                        ]])


class GamePadHwButton():
    
    def __init__(self, address, kind, abbreviation, name):
        self.abbr = abbreviation
        self.name = name
        self.add = address
        self.kind = kind
        self.state = False
        self.data = None

    def update(self, data):
        self.data = data
        self.state = sum(data) > 0

    def __repr__(self):
        return ''.join([str(word) for word in ['type=', self.kind,
                        ', add= ',self.add,
                        ', name="',self.name,
                        '", state= ', self.state,
                        ', data=', self.data]])
           
class GamePadControler():
    def __init__(self):
        self.open()
        actions = \
"""
1,0:b:A:A button
1,1:b:B:B button
1,3:b:X:X button
1,4:b:Y:Y button
1,6:b:L1:L1 button
1,7:b:R1:R1 button
1,10:b:select:SELECT button
1,11:b:start:START button

2,0:s:LHstick:Left horizontal stick
2,1:s:LVstick:Left vertical stick
2,2:s:RHstick:Right horizontal stick
2,3:s:RVstick:Right vertical stick

2,4:b:R2:R2 button
2,5:b:L2:L2 button

2,6:a:leftright:Horizontal arrows
2,7:a:updown:Vertical arrows
"""

        
        minimal_line = '1,1:b:A'
        x = [line for line in actions.split('\n')]
        x = [line.split(':') for line in x if len(line)>=len(minimal_line)]
        self.states = {tuple([int(add) for add in address.split(',')]):list(data) 
                            for address, *data in x}
        print(self.states)

        self.hw_btns = {key : GamePadHwButton(key, *value) 
                for key, value in self.states.items()}

        self.btns = {btn.abbr : btn for btn in self.hw_btns.values()}
        sw_btns = \
"""up:UP arrow:updown:1,128
down:DOWN arrow:updown:255,127
left:LEFT arrow:leftright:1,128
right:RIGHT arrow:leftright:255,127"""

        x = [line.split(':') for line in sw_btns.split('\n')]
        self.btns.update({abbr : GamePadSwButton(
                                abbr, name, self.btns[hw_btn], 
                                [int(trig) for trig in trigger.split(',')]
                                )
                            for abbr, name, hw_btn, trigger in x})

        sw_sticks = \
"""leftstick:Left stick:LVstick:LHstick
rightstick:Right stick:RVstick:RHstick"""

        x = [line.split(':') for line in sw_sticks.split('\n')]
        self.sticks = {}
        self.sticks.update({abbr : GamePadSwStick(
                                    abbr, name, self.btns[hw1], self.btns[hw2]
                                    ) 
                                for abbr, name, hw1, hw2 in x})

#       self.up = GamePadSwButton('up','UP arrow', self.btns['updown'], [1,128])
#        print(self.hw_btns)
#        print(self.btns)
        [print(str(btn)) for btn in self.btns.values()]
        [print(str(stc)) for stc in self.sticks.values()]
    def open(self):
        self.pipe = open('/dev/input/js0', 'rb') #open joystick 
        action = []
    
    def update(self):
        self.readData()
        print('>>>>> GOT NEW ACTION ', self.state)
        add = tuple(self.state[6:8])
        data = tuple(self.state[4:6])
        print('data', data)
        print('address', add)
        
        if self.hw_btns.get(add) is not None:
            self.hw_btns[add].update(data)
            print(self.hw_btns[add])

        #print(self.btns['up'])
        print(self.btns['up'])
        print(self.btns['down'])
        print(self.btns['left'])
        print(self.btns['right'])

        print(self.sticks['leftstick'])
        print(self.sticks['rightstick'])
        
    def readData(self):
        action = []
        stop = 1
        while stop == 1:
            for character in self.pipe.read(1):
                action += [int(character)]
                if len(action) == 8:
                    self.state = action
                    action = []
                    stop = 2
                    ##when joystick is stationary code hangs here.


if __name__ == '__main__':
    gpc = GamePadControler()
    while(1):
        gpc.update()
