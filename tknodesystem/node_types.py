import __main__
from .node import Node
from .node_socket import NodeSocket
from .node_args import Args
import warnings
import tkinter as tk
from tkinter.font import Font

class NodeValue(Node):
    def __init__(self, canvas, width=1000, height=50, value=0, border_color='white', text=None, corner_radius=25,
                 border_width=0, fg_color='#37373D', text_color='white', font=("",10), socket_radius=8, socket_hover=True,
                 socket_color="#FF007F", socket_hover_color="grey50", highlightcolor='#FF007F', hover=True, justify="center",
                 click_command=None, side="right", x=0, y=0, num=None, fixed=False):

        self.text = text
        self.canvas = canvas
        self.font = Font(family=font[0], size=font[1])
        self.args = Args.value_args(locals())
        
        if click_command:
            if click_command!="<lambda>":
                if type(click_command) is str:
                    click_command = getattr(__main__, click_command)
                self.args.update({"click_command": click_command.__name__})
            else:
                click_command = None
                warnings.warn("Warning: currently <lamba function> cannot be saved and loaded, please use any local function instead")
            
        if self.text is None:
            print('I am inputting text')
            self.text = f"Input{self.canvas.input_num}"
            
        self.canvas.input_num +=1
        self.connected_func = set()
        self.type = 'NodeValue'
        self.value = value
        
        if border_width==0:
            border_color = fg_color

        # Dynamic width update
        #width = self.font.measure(self.value) + 100
        value = self.format_value_to_lines()
        text_height, text_width = self.calculate_text_dimensions(self.value)
        height = text_height + 20  # Adding padding to height
        width = text_width + 20  # Adding padding to width

        # Dynamic text update

        super().__init__(canvas=canvas, width=width, height=height, center=(width,height), text=str(self.text),
                         border_width=border_width, border_color=border_color, fg_color=fg_color, corner_radius=corner_radius,
                         text_color=text_color, font=font, highlightcolor=highlightcolor, hover=hover, justify=justify,
                         click_command=click_command)

        if side=="left":
            center = (width-(width/2),height)
        else:
            center = (width+(width/2),height)
            
        self.output_ = NodeSocket(canvas, value=value, radius=socket_radius, center=center,
                                  fg_color=socket_color, hover_color=socket_hover_color, border_width=border_width,
                                  border_color=border_color, hover=socket_hover, socket_num=num)
        
        self.allIDs = self.allIDs + [self.output_.ID]

        self.bind_all_to_movement()
        self.canvas.tag_bind(self.output_.ID, '<Button-1>', self.connect_output)
        if not fixed:
            self.canvas.bind_all("<BackSpace>", lambda e: self.destroy() if self.signal else None, add="+")
        self.socket_nums = self.output_.socket_num
        
        for j in range(self.canvas.gain_in):
            for i in self.allIDs:
                self.canvas.scale(i, 0, 0, 1.1, 1.1)

        for j in range(abs(self.canvas.gain_out)):
            for i in self.allIDs:
                self.canvas.scale(i, 0, 0, 0.9, 0.9)
                
        if x or y:
            super().move(x,y)

        # Ensure font is a Font object
        if isinstance(font, tuple):
            self.font = Font(family=font[0], size=font[1])
        elif isinstance(font, Font):
            self.font = font
        else:
            raise ValueError("Font must be a tuple or a Font object")

    def format_value_to_lines(self):
        words = self.value.split()  # Split the string into a list of words
        # Create a list where each element is a string containing up to 7 words
        lines = [' '.join(words[i:i + 7]) for i in range(0, len(words), 7)]
        # Join the lines with newline characters to create the formatted string
        formatted_value = '\n'.join(lines)
        return formatted_value

    def calculate_text_dimensions(self, text):
        words = text.split()
        max_words_per_line = 7
        lines = [' '.join(words[i:i + max_words_per_line]) for i in range(0, len(words), max_words_per_line)]

        # Calculate total height
        line_height = self.font.metrics("linespace")
        total_height = len(lines) * line_height

        # Calculate the width as the width of the longest line
        max_line_width = 0
        for line in lines:
            line_width = self.font.measure(line)
            if line_width > max_line_width:
                max_line_width = line_width

        print("Height:", total_height, "Width:", max_line_width)
        return total_height, max_line_width

    def get(self):
        """ get the current value of node """
        return self.output_.value
        
    def connect_output(self, event):
        """ connect output socket """
        
        self.canvas.clickcount += 1
        self.canvas.outputcell = self

        if self.canvas.clickcount == 2:
            self.canvas.clickcount = 0
 
        self.output_.connect_wire()
        
    def destroy(self):
        if self.ID not in self.canvas.find_all(): return

        self.output_.value = None
        for i in self.allIDs:
            self.canvas.delete(i)
            
        self.canvas.obj_list.remove(self)
        super().destroy()
        
        for i in self.connected_func:
            i.update()
                
    def exists(self):
        if self.ID in self.canvas.find_all():
            return True
        else:
            return False
        
    def configure(self, **kwargs):
        """ configure options """
        self.args.update(kwargs)
        if "value" in kwargs:
            self.output_.value = kwargs.pop("value")
            if not self.text:
                super().configure(text=kwargs.pop("text"))
            for i in self.connected_func:
                i.update()
        if "text" in kwargs:
            self.text = kwargs.pop("text")
            super().configure(text=self.text)
        if "fg_color" in kwargs:
            super().configure(fg_color=kwargs.pop("fg_color"))
        if "text_color" in kwargs:
            super().configure(text_color=kwargs.pop("text_color"))
        if "font" in kwargs:
            super().configure(font=kwargs.pop("font"))
        if "highlightcolor" in kwargs:
            super().configure(highlightcolor=kwargs.pop("highlightcolor"))
        if "socket_color" in kwargs:
            self.output_.configure(fg_color=kwargs.pop("socket_color"))
        if "socket_hover_color" in kwargs:
            self.output_.configure(hover_color=kwargs.pop("socket_hover_color"))
        if "hover" in kwargs:
            super().configure(hover=kwargs.pop("hover"))
        if "socket_hover" in kwargs:
            self.output_.configure(hover=kwargs.pop("socket_hover"))
                                  
        if len(kwargs)>0:
            raise ValueError("This option is not configurable:" + list(kwargs.keys())[0])



class NodeOperation(Node):
    def __init__(self, canvas, width=100, height=None, inputs=2, border_color='white', text=None, justify="center", hover_text=None,
                 socket_radius=8, corner_radius=25, border_width=0, fg_color='#37373D', text_color='white', font=("",10), multiple_connection=False,
                 highlightcolor='#52d66c', hover=True, socket_color="green", socket_hover_color="grey50", x=0, y=0, none_inputs=False, pass_node_id=False,
                 multiside=False, command=None, output_socket_color="green", click_command=None, socket_hover=True, num=None, fixed=False):

        self.text = text
        self.canvas = canvas
        self.type = 'NodeOperation'
        self.hover_text = {} if hover_text is None else hover_text
        
        if self.text is None:
            self.text = f"Function{self.canvas.operation_num}"
            
        self.canvas.operation_num +=1

        if border_width==0:
            border_color = fg_color

        args = locals()
        args['hover_text'] = self.hover_text
        self.args = Args.func_args(args)

        self.pass_node = pass_node_id
     
            
        if command:
            if command!="<lambda>":
                print('executing lambda')
                if type(command) is str:
                    command = getattr(__main__, command)
                self.args.update({"command": command.__name__})
            else:
                command = None
                warnings.warn("Warning: currently <lamba function> cannot be saved and loaded, please use any local function instead")
        if click_command:
            if click_command!="<lambda>":
                if type(click_command) is str:
                    click_command = getattr(__main__, click_command)
                self.args.update({"click_command": click_command.__name__})
            else:
                click_command = None
                warnings.warn("Warning: currently <lamba function> cannot be saved and loaded, please use any local function instead")
                
        self.command = command
        
        if height is None:
            height = 50 + (inputs*10)
            
        super().__init__(canvas=canvas, width=width, height=height, center=(width,height), justify=justify,
                         border_width=border_width, fg_color=fg_color, border_color=border_color,
                         text_color=text_color, font=font, click_command=click_command, corner_radius=corner_radius,
                         highlightcolor=highlightcolor, text=str(self.text), hover=hover)

        self.line1 = None
        self.line2 = None
        self.line3 = None
        self.line4 = None
        self.line5 = None
        self.socket_colors = []
        self.connected_node = set()
        self.connected_node_first = None
        self.none_values = none_inputs
        
        x_pos = x
        y_pos = y
            
        if type(socket_color) is list:
            self.socket_colors = socket_color
        else:
            for i in range(5):
                self.socket_colors.append(socket_color)

        self.inputs = inputs
    
        if self.inputs>3 and self.height<=80:
            multiside=True
            
        if multiside:
            z = self.inputs-1
        else:
            z = self.inputs+1

        if z==0:
            z = 2
            
        y = height/z
        x = 1
        if self.inputs==2 and multiside:
            x = 1/2

        self.cellinput1 = None
        self.cellinput2 = None
        self.cellinput3 = None
        self.cellinput4 = None
        self.cellinput5 = None
        self.celloutput = None
        self.socket_nums = []
        self.values_args = []
        self.multiple = multiple_connection
        
        self.connected_inputs1 = list()
        self.connected_inputs2 = list()
        self.connected_inputs3 = list()
        self.connected_inputs4 = list()
        self.connected_inputs5 = list()
        
        self.output_ = NodeSocket(canvas, radius=socket_radius, center=(width+(width/2),height),
                                  fg_color=output_socket_color, hover_color=socket_hover_color, socket_num=num[0] if num else None,
                                  border_width=border_width, border_color=border_color, hover=socket_hover)
        self.canvas.tag_bind(self.output_.ID, '<Button-1>', self.connect_output)
        self.socket_nums.append(self.output_.socket_num)
        
        center = (width/2, y * x + height/2)     
        self.input_1 = NodeSocket(canvas, radius=socket_radius, center=center, fg_color=self.socket_colors[0],
                                  hover_color=socket_hover_color, border_width=border_width, hover=socket_hover,
                                  border_color=border_color, socket_num=num[1] if num else None)
        
        id_list = [self.output_.ID, self.input_1.ID]
        self.canvas.tag_bind(self.input_1.ID, '<Button-1>', lambda e: self.connect_input(self.line1,'input1'))
        self.socket_nums.append(self.input_1.socket_num)
        
        if self.inputs>=2:
            if not multiside:
                x+=1
                center = (width/2,y * x +height/2)
            else:
                center = (width, height/2)
                
            self.input_2 = NodeSocket(canvas, radius=socket_radius, center=center, fg_color=self.socket_colors[1],
                                      hover_color=socket_hover_color, border_width=border_width, hover=socket_hover,
                                      border_color=border_color, socket_num=num[2] if num else None)
            id_list.append(self.input_2.ID)
            self.canvas.tag_bind(self.input_2.ID, '<Button-1>', lambda e: self.connect_input(self.line2,'input2'))
            self.socket_nums.append(self.input_2.socket_num)
            
        if self.inputs>=3:
            if not multiside:
                x+=1
                center = (width/2,y * x +height/2)
            else:
                center = (width, height*1.5)
            self.input_3 = NodeSocket(canvas, radius=socket_radius, center=center, fg_color=self.socket_colors[2],
                                      hover_color=socket_hover_color, border_width=border_width, hover=socket_hover,
                                      border_color=border_color, socket_num=num[3] if num else None)
            self.canvas.tag_bind(self.input_3.ID, '<Button-1>', lambda e: self.connect_input(self.line3,'input3'))
            id_list.append(self.input_3.ID)
            self.socket_nums.append(self.input_3.socket_num)
            
        if self.inputs>=4:
            x+=1
            center = (width/2,y * x +height/2)
            self.input_4 = NodeSocket(canvas, radius=socket_radius, center=center, fg_color=self.socket_colors[3],
                                      hover_color=socket_hover_color, border_width=border_width, hover=socket_hover,
                                      border_color=border_color, socket_num=num[4] if num else None)
            self.canvas.tag_bind(self.input_4.ID, '<Button-1>', lambda e: self.connect_input(self.line4,'input4'))
            id_list.append(self.input_4.ID)
            self.socket_nums.append(self.input_4.socket_num)
            
        if self.inputs>=5:
            x+=1
            center = (width/2,y * x +height/2)
            self.input_5 = NodeSocket(canvas, radius=socket_radius, center=center, fg_color=self.socket_colors[4],
                                      hover_color=socket_hover_color, border_width=border_width, hover=socket_hover,
                                      border_color=border_color, socket_num=num[5] if num else None)
            self.canvas.tag_bind(self.input_5.ID, '<Button-1>', lambda e: self.connect_input(self.line5, 'input5'))
            id_list.append(self.input_5.ID)
            self.socket_nums.append(self.input_5.socket_num)
            
        self.allIDs = self.allIDs + id_list
        self.bind_all_to_movement()
        self.id_list = id_list
        if not fixed:
            self.canvas.bind_all("<BackSpace>", lambda e: self.destroy() if self.signal else None, add="+")

        for i in self.hover_text:
            self.config_socket(**self.hover_text[i])
       
        for j in range(self.canvas.gain_in):
            for i in self.allIDs:
                self.canvas.scale(i, 0, 0, 1.1, 1.1)

        for j in range(abs(self.canvas.gain_out)):
            for i in self.allIDs:
                self.canvas.scale(i, 0, 0, 0.9, 0.9)
                
        if x_pos or y_pos:
            super().move(x_pos,y_pos)
            
        self.canvas.obj_list.add(self)
        
    def connect_output(self, event):
        """ connect output socket """

        self.canvas.clickcount += 1
        self.canvas.outputcell = self

        if self.canvas.clickcount == 2:
            self.canvas.clickcount = 0
            
        self.output_.connect_wire()
 
    def connect_input(self, line_id, input_id):
        """ connect input sockets """
        if self.canvas.outputcell is None:
            return
        if self.canvas.outputcell in self.connected_node:
            return
        if self.canvas.outputcell==self:
            return
 
        m = self.connected_node_first

        for i in range(self.canvas.operation_num):
            if m is None:
                break
            if m.type=="NodeOperation":
                if self.canvas.outputcell in m.connected_node:
                    return
            m = m.connected_node_first

        if not self.multiple:
            try: self.canvas.delete(line_id.ID)
            except: None
                    
        self.canvas.clickcount += 1
        self.canvas.IDc = input_id
        self.canvas.inputcell = self
        
        if self.canvas.clickcount == 2:
            self.canvas.clickcount = 0
            self.canvas.conectcells()
            if self.canvas.outputcell.type=="NodeValue":
                self.canvas.outputcell.connected_func.add(self)
            elif self.canvas.outputcell.type=="NodeOperation":
                self.canvas.outputcell.connected_node.add(self)
                self.canvas.outputcell.connected_node_first = self
            try:
                if input_id=="input1":
                    if not self.multiple:
                        for x in self.canvas.line_list:
                            if x[1]==self.input_1.socket_num:
                                self.canvas.line_list.remove(x)
                                break
                    else:
                        if self.canvas.outputcell not in self.connected_inputs1:
                            self.connected_inputs1.append(self.canvas.outputcell)
                    l = (self.canvas.outputcell.output_.socket_num, self.canvas.inputcell.input_1.socket_num)
                    self.canvas.line_list.add(l)
                if input_id=="input2":
                    if not self.multiple:
                        for x in self.canvas.line_list:
                            if x[1]==self.input_2.socket_num:
                                self.canvas.line_list.remove(x)
                                break
                    else:
                        if self.canvas.outputcell not in self.connected_inputs2:
                            self.connected_inputs2.append(self.canvas.outputcell)
                    l = (self.canvas.outputcell.output_.socket_num, self.canvas.inputcell.input_2.socket_num)
                    self.canvas.line_list.add(l)                    
                if input_id=="input3":
                    if not self.multiple:
                        for x in self.canvas.line_list:
                            if x[1]==self.input_3.socket_num:
                                self.canvas.line_list.remove(x)
                                break
                    else:
                        if self.canvas.outputcell not in self.connected_inputs3:
                            self.connected_inputs3.append(self.canvas.outputcell)
                    l = (self.canvas.outputcell.output_.socket_num, self.canvas.inputcell.input_3.socket_num)
                    self.canvas.line_list.add(l)
                if input_id=="input4":
                    if not self.multiple:
                        for x in self.canvas.line_list:
                            if x[1]==self.input_4.socket_num:
                                self.canvas.line_list.remove(x)
                                break
                    else:
                        if self.canvas.outputcell not in self.connected_inputs4:
                            self.connected_inputs4.append(self.canvas.outputcell)
                    l = (self.canvas.outputcell.output_.socket_num, self.canvas.inputcell.input_4.socket_num)
                    self.canvas.line_list.add(l)
                if input_id=="input5":
                    if not self.multiple:
                        for x in self.canvas.line_list:
                            if x[1]==self.input_5.socket_num:
                                self.canvas.line_list.remove(x)
                                break
                    else:
                        if self.canvas.outputcell not in self.connected_inputs5:
                            self.connected_inputs5.append(self.canvas.outputcell)
                    l = (self.canvas.outputcell.output_.socket_num, self.canvas.inputcell.input_5.socket_num)
                    self.canvas.line_list.add(l)
            except AttributeError: None

        else:
            if self.canvas.outputcell.type=="NodeValue":
                try: self.canvas.outputcell.connected_func.remove(self)
                except KeyError: None
            elif self.canvas.outputcell.type=="NodeOperation":
                try:
                    self.canvas.outputcell.connected_node.remove(self)
                    self.canvas.outputcell.connected_node_first = None
                except KeyError: None
            try:
                if input_id=="input1":
                    self.cellinput1 = None
                    self.canvas.line_list.remove((self.canvas.outputcell.output_.socket_num, self.canvas.inputcell.input_1.socket_num))
                    if self.multiple:
                        self.connected_inputs1.remove(self.canvas.outputcell)
                if input_id=="input2":
                    self.cellinput2 = None
                    self.canvas.line_list.remove((self.canvas.outputcell.output_.socket_num, self.canvas.inputcell.input_2.socket_num))
                    if self.multiple:
                        self.connected_inputs2.remove(self.canvas.outputcell)
                if input_id=="input3":
                    self.cellinput3 = None
                    self.canvas.line_list.remove((self.canvas.outputcell.output_.socket_num, self.canvas.inputcell.input_3.socket_num))
                    if self.multiple:
                        self.connected_inputs3.remove(self.canvas.outputcell)
                if input_id=="input4":
                    self.cellinput4 = None
                    self.canvas.line_list.remove((self.canvas.outputcell.output_.socket_num, self.canvas.inputcell.input_4.socket_num))
                    if self.multiple:
                        self.connected_inputs4.remove(self.canvas.outputcell)
                if input_id=="input5":
                    self.cellinput5 = None
                    self.canvas.line_list.remove((self.canvas.outputcell.output_.socket_num, self.canvas.inputcell.input_5.socket_num))
                    if multiple:
                        self.connected_inputs5.remove(self.canvas.outputcell)
            except AttributeError: None
            except KeyError: None
            
            if self.multiple:
                for i in self.canvas.line_ids:
                    if (i.firstcell==self.canvas.outputcell) and (i.secondcell==self) and (i.inputs==input_id):
                        i.delete_line(i.inputs)
                        break
        self.update()
        
    def toggle(self, input_num: int):
        line_num = eval(f"self.line{input_num}")
        input_num = f"input{input_num}"
        self.connect_input(line_num, input_num)
                           
    def update(self):
        """ update the output values """
   
        if self.multiple:
            cells = [self.connected_inputs1,
                     self.connected_inputs2,
                     self.connected_inputs3,
                     self.connected_inputs4,
                     self.connected_inputs5]
            self.values_args = []
          
            if self.command:
                for i in cells[0:self.inputs]:
                    v = []
                    for j in i:
                        if j.output_.value is not None:
                            v.append(j.output_.value)
                    self.values_args.append(v)
        
                if not self.none_values:
                    for i in self.values_args:
                        if len(i)==0:
                            self.output_.value = None
                            break
                        else:
                            self.output_.value = 1
                else:
                    self.output_.value = 1
                    
                if self.output_.value:
                    if self.pass_node:
                        self.output_.value = self.command(self, *self.values_args[0:self.inputs])
                    else:
                        self.output_.value = self.command(*self.values_args[0:self.inputs])
            else:
                self.output_.value = []
 
        else:
            arguments = [self.cellinput1,
                         self.cellinput2,
                         self.cellinput3,
                         self.cellinput4,
                         self.cellinput5]
            self.values_args = []
            if self.command:
                for i in arguments[0:self.inputs]:
                    if i is None:
                        self.values_args.append(None)
                    else:
                        self.values_args.append(i.output_.value)
                
                if not self.none_values:
                    for i in self.values_args:
                        if i is None:
                            self.output_.value = None
                            break
                        else:
                            self.output_.value = 1
                else:
                    self.output_.value = 1
                    
                if self.output_.value:
                    if self.pass_node:
                        self.output_.value = self.command(self, *self.values_args[0:self.inputs])
                    else:
                        self.output_.value = self.command(*self.values_args[0:self.inputs])
            else:
                self.output_.value = None

        if len(self.connected_node)>0:
            for i in self.connected_node:
                i.update()
        
    def get(self):
        """ get the current value of node """
        return self.output_.value
    
    def get_inputs(self):
        return self.values_args
    
    def destroy(self):
        if self.ID not in self.canvas.find_all(): return
        self.output_.value = None
        for i in self.id_list:
            self.canvas.delete(i)

        self.canvas.obj_list.remove(self)
        super().destroy()
        
        if len(self.connected_node)>0:
            for i in self.connected_node:
                i.update()
                
    def exists(self):
        if self.ID in self.canvas.find_all():
            return True
        else:
            return False

    def config_socket(self, index: int, hover_text: str=None, hover_text_color=None, hover_bg=None, **kwargs):
        if index==1:
            socket = self.input_1
        elif index==2:
            socket = self.input_2
        elif index==3:
            socket = self.input_3
        elif index==4:
            socket = self.input_4
        elif index==5:
            socket = self.input_5
        else:
            return

        kwarg_args = {}
        for i in kwargs:
            kwarg_args  = {i: kwargs[i]}
            
        self.hover_text[str(index)] = {'index': index, 'hover_text': hover_text, 'hover_text_color': hover_text_color, 'hover_bg': hover_bg, **kwarg_args}

        if hover_text:
            socket.hover_message = True
            socket.msg.set(hover_text)
        else:
            socket.hover_message = False
            
        if hover_text_color:
            socket.hover_text.configure(fg=hover_text_color)
            
        if hover_bg:
            socket.hover_text.configure(bg=hover_bg)
            
        if "socket_color" in kwargs:
            socket.configure(fg_color=kwargs.pop("socket_color"))

        self.configure(**kwargs)
            
    def configure(self, **kwargs):
        """ configure options """
        self.args.update(kwargs)
        if "text" in kwargs:
            self.text = kwargs.pop("text")
            super().configure(text=self.text)
        if "fg_color" in kwargs:
            super().configure(fg_color=kwargs.pop("fg_color"))
        if "text_color" in kwargs:
            super().configure(text_color=kwargs.pop("text_color"))
        if "font" in kwargs:
            super().configure(font=kwargs.pop("font"))
        if "highlightcolor" in kwargs:
            super().configure(highlightcolor=kwargs.pop("highlightcolor"))
        if "socket_color" in kwargs:
            socket_color = kwargs.pop("socket_color")
            if type(socket_color) is list:
                try:
                    self.input_1.configure(fg_color=socket_color[0])
                    self.input_2.configure(fg_color=socket_color[1])
                    self.input_3.configure(fg_color=socket_color[2])
                    self.input_4.configure(fg_color=socket_color[3])
                    self.input_5.configure(fg_color=socket_color[4])
                except: None
            else:
                try:
                    self.input_1.configure(fg_color=socket_color)
                    self.input_2.configure(fg_color=socket_color)
                    self.input_3.configure(fg_color=socket_color)
                    self.input_4.configure(fg_color=socket_color)
                    self.input_5.configure(fg_color=socket_color)
                except: None
            
        if "socket_hover_color" in kwargs:
            socket_hover_color = kwargs.pop("socket_hover_color")
            self.output_.configure(hover_color=socket_hover_color)
            try:
                self.input_1.configure(hover_color=socket_hover_color)
                self.input_2.configure(hover_color=socket_hover_color)
                self.input_3.configure(hover_color=socket_hover_color)
                self.input_4.configure(hover_color=socket_hover_color)
                self.input_5.configure(hover_color=socket_hover_color)
            except: None
            
        if "output_socket_color" in kwargs:
            self.output_.configure(fg_color=kwargs.pop("output_socket_color"))
        if "hover" in kwargs:
            super().configure(hover=kwargs.pop("hover"))
        if "socket_hover" in kwargs:
            hover = kwargs.pop("socket_hover")
            self.output_.configure(hover=hover)
            try:
                self.input_1.configure(hover=hover)
                self.input_2.configure(hover=hover)
                self.input_3.configure(hover=hover)
                self.input_4.configure(hover=hover)
                self.input_5.configure(hover=hover)
            except: None
                                  
        if len(kwargs)>0:
            raise ValueError("This option is not configurable:" + list(kwargs.keys())[0])

        print(self.width)


class NodeCompile(Node):
    def __init__(self, canvas, width=200, height=500, border_color='white', text="Compile", socket_radius=8, corner_radius=25, x=0, y=0, justify="center",
                 border_width=0, fg_color='#37373D',text_color='white', font=("",10), highlightcolor='#00BFFF', hover=True, socket_hover=True, fixed=False,
                 socket_color="#00BFFF", socket_hover_color="grey50", show_value=True, command=None, click_command=None, side="left", num=None,
                 multiple_connection=False, pass_node_id=False):
        self.width = width
        self.height = height
        self.canvas = canvas
        self.text = text
        self.font = tk.font.Font(family="Helvetica", size=10)
        self.type = 'NodeCompile'

        if border_width==0:
            border_color = fg_color

        self.canvas.compile_num +=1
        self.args = Args.compile_args(locals())
        self.pass_node = pass_node_id

        if command:
            if command!="<lambda>":
                if type(command) is str:
                    command = getattr(__main__, command)
                    print('Executing the command...')
                self.args.update({"command": command.__name__})
            else:
                command = None
                warnings.warn("Warning: currently <lamba function> cannot be saved and loaded, please use any local function instead")
        if click_command:
            if click_command!="<lambda>":
                if type(click_command) is str:
                    click_command = getattr(__main__, click_command)
                self.args.update({"click_command": click_command.__name__})
            else:
                click_command = None
                warnings.warn("Warning: currently <lamba function> cannot be saved and loaded, please use any local function instead")

        super().__init__(canvas=canvas, width=self.width, height=self.height, center=(width, height),
                         text=str(text),
                         corner_radius=corner_radius,
                         border_width=border_width, fg_color=fg_color, border_color=border_color, hover=hover,
                         justify=justify,
                         text_color=text_color, font=font, click_command=click_command,
                         highlightcolor=highlightcolor)

        self.line1 = None
        self.cellinput1 = None
        self.celloutput = None
        self.show_value = show_value
        self.previous_value = None
        self.command = command
        self.connected_inputs = list()
        self.multiple = multiple_connection
        self.multilines = {}
        self.add_copy_button()

        if side=="left":
            center = (width-(width/2),height)
        else:
            center = (width+(width/2),height)

        self.input_1 = NodeSocket(canvas, radius=socket_radius, center=center, border_width=border_width,
                                  fg_color=socket_color, hover_color=socket_hover_color, border_color=border_color,
                                  hover=socket_hover, socket_num=num[0] if num else None)

        self.output_ = NodeSocket(canvas, radius=socket_radius, center=(width+(width/2),height),
                                  fg_color=socket_color, hover_color=socket_hover_color, border_width=border_width,
                                  border_color=border_color, hover=socket_hover, socket_num=num[1] if num else None)

        self.socket_nums = [self.input_1.socket_num, self.output_.socket_num]
        self.allIDs = self.allIDs + [self.output_.ID, self.input_1.ID]
        self.fixed = True
        self.bind_all_to_movement()
        self.canvas.tag_bind(self.input_1.ID, '<Button-1>', self.connect_input)

        if not fixed:
            self.canvas.bind_all("<BackSpace>", lambda e: self.destroy() if self.signal else None, add="+")

        self.output_.hide()

        for j in range(self.canvas.gain_in):
            for i in self.allIDs:
                self.canvas.scale(i, 0, 0, 1.1, 1.1)

        for j in range(abs(self.canvas.gain_out)):
            for i in self.allIDs:
                self.canvas.scale(i, 0, 0, 0.9, 0.9)

        if x or y:
            super().move(x,y)

        self.canvas.obj_list.add(self)

    def format_value_to_lines(self):
        words = self.value.split()  # Split the string into a list of words
        # Create a list where each element is a string containing up to 7 words
        lines = [' '.join(words[i:i + 7]) for i in range(0, len(words), 7)]
        # Join the lines with newline characters to create the formatted string
        formatted_value = '\n'.join(lines)
        return formatted_value

    def calculate_text_dimensions(self, text):
        words = text.split()
        max_words_per_line = 7
        lines = [' '.join(words[i:i + max_words_per_line]) for i in range(0, len(words), max_words_per_line)]

        # Calculate total height
        line_height = self.font.metrics("linespace")
        total_height = len(lines) * line_height

        # Calculate the width as the width of the longest line
        max_line_width = 0
        for line in lines:
            line_width = self.font.measure(line)
            if line_width > max_line_width:
                max_line_width = line_width

        print("Height:", total_height, "Width:", max_line_width)
        return total_height, max_line_width

    def add_copy_button(self):
        button_x = self.width - 100
        button_y = self.height / 2
        # Existing button creation code
        self.copy_button_id = self.canvas.create_rectangle(button_x, button_y, button_x + 50, button_y + 50,
                                                           fill="gray", tags=("copyButton",))

        # Calculate the center of the button for the text placement
        text_x = button_x + 25  # Halfway across the width of the button
        text_y = button_y + 25  # Halfway down the height of the button

        # Create text on the button
        self.copy_button_text_id = self.canvas.create_text(text_x, text_y, text="Copy Me!", fill="white",
                                                           tags=("copyButton",))

        # Bind the click event to the button (and now text as well)
        self.canvas.tag_bind("copyButton", '<Button-1>', self.copy_text_to_clipboard)

    def copy_text_to_clipboard(self, event=None):
        root = self.canvas.winfo_toplevel()
        root.clipboard_clear()
        root.clipboard_append(self.output_.value)
        print(f"Copied '{self.output_.value}' to clipboard.")  # For debugging

    def connect_output(self, event):
        """ connect output socket """
        
        self.canvas.clickcount += 1
        self.canvas.outputcell = self

        if self.canvas.clickcount == 2:
            self.canvas.clickcount = 0
 
        self.output_.connect_wire()
        
    def connect_input(self, event):
        """ connect input sockets """
        print("Attempting to connect input...")
        if not self.multiple:
            print("The input is NOT a multiple...")
            try: self.canvas.delete(self.line1.ID)
            except: None
        else:
            print("The input IS a multiple...")
            if self.canvas.outputcell in list(self.multilines.keys()):
                if self.multilines[self.canvas.outputcell] is not None:
                    self.canvas.delete(self.multilines[self.canvas.outputcell])
                    del self.multilines[self.canvas.outputcell]
                    
        self.canvas.clickcount += 1
        self.canvas.IDc = 'input1'
        self.canvas.inputcell = self

        if self.canvas.clickcount == 2:
            self.canvas.clickcount = 0
            self.canvas.conectcells()
            self.fixed = False
            try:
                if self.canvas.outputcell.type=="NodeValue":
                    self.canvas.outputcell.connected_func.add(self)
                if not self.multiple:
                    for x in self.canvas.line_list:
                        if x[1]==self.input_1.socket_num:
                            self.canvas.line_list.remove(x)
                            break
                else:
                    if self.canvas.outputcell not in self.connected_inputs:
                        self.connected_inputs.append(self.canvas.outputcell)
                self.canvas.line_list.add((self.canvas.outputcell.output_.socket_num, self.canvas.inputcell.input_1.socket_num))
            except AttributeError: None
        else:
            self.fixed = True
            try:
                if self.canvas.outputcell.type=="NodeValue":
                    try: self.canvas.outputcell.connected_func.remove(self)
                    except KeyError: None
                self.canvas.line_list.remove((self.canvas.outputcell.output_.socket_num, self.canvas.inputcell.input_1.socket_num))
                if self.multiple:
                    self.connected_inputs.remove(self.canvas.outputcell)
                    self.canvas.delete(self.line1.ID)
            except AttributeError: None
            except KeyError: None
        if self.multiple:
            try:
                self.multilines.update({self.canvas.outputcell:self.line1.ID})
            except:
                self.multilines.update({self.canvas.outputcell:None})
        print(self.multilines)
        print(self.canvas.line_list)

    def get(self):
        """ get the current value of node """
        return self.output_.value
    
    def toggle(self):
        self.connect_input(0)

    def update(self):
        """ update the output values """
        if self.ID not in self.canvas.find_all():
            return
        if self.multiple:
            print('I am in self multiple')
            output = []
            for i in self.connected_inputs:
                if i.output_.value is not None:
                    # Check if the output value is a string and prepend 'hi'
                    if isinstance(i.output_.value, str):
                        output.append('hi ' + i.output_.value)
                    else:
                        output.append(i.output_.value)
        else:
            output = self.cellinput1.output_.value if not self.fixed else None
            print(output)

        self.output_.value = output

        if self.previous_value != self.output_.value:
            if self.show_value:
                self.canvas.itemconfigure(self.IDtext, text=str(self.output_.value))

            if self.output_.value is not None:
                if self.command:
                    if self.pass_node:
                        self.command(self, self.output_.value)
                    else:
                        self.command(self.output_.value)
        self.previous_value = self.output_.value
        # Define the new width and calculate the bounding box of the polygon
        new_width = 300
        coords = self.canvas.coords(self.ID)
        x_coords = coords[0::2]  # Extract x-coordinates
        y_coords = coords[1::2]  # Extract y-coordinates
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        new_x1 = center_x - new_width / 2
        new_x2 = center_x + new_width / 2

        # Calculate new polygon coordinates for a rounded rectangle
        new_coords = [
            new_x1 + self.corner_radius, min_y, new_x1 + self.corner_radius, min_y,
            new_x2 - self.corner_radius, min_y, new_x2 - self.corner_radius, min_y,
            new_x2, min_y, new_x2, min_y + self.corner_radius,
            new_x2, max_y - self.corner_radius, new_x2, max_y - self.corner_radius,
            new_x2, max_y, new_x2 - self.corner_radius, max_y,
            new_x2 - self.corner_radius, max_y, new_x1 + self.corner_radius, max_y,
            new_x1 + self.corner_radius, max_y, new_x1, max_y,
            new_x1, max_y - self.corner_radius, new_x1, min_y + self.corner_radius,
            new_x1, min_y + self.corner_radius, new_x1, min_y
        ]

        # Update the polygon's coordinates
        self.canvas.coords(self.ID, new_coords)
        self.canvas.after(1000, self.update)
        #self.canvas.itemconfigure(self.ID, width=500)


    def destroy(self):
        if self.ID not in self.canvas.find_all(): return
        self.output_.value = None
    
        for i in self.allIDs:
            self.canvas.delete(i)
            
        self.canvas.obj_list.remove(self)
        super().destroy()
     
    def exists(self):
        if self.ID in self.canvas.find_all():
            return True
        else:
            return False

    def configure(self, **kwargs):
        """ configure options """
        self.args.update(kwargs)
        if "text" in kwargs:
            self.text = kwargs.pop("text")
            super().configure(text=self.text)
            print('I am the configured text')
            print(self.text)
        if "fg_color" in kwargs:
            super().configure(fg_color=kwargs.pop("fg_color"))
        if "text_color" in kwargs:
            super().configure(text_color=kwargs.pop("text_color"))
        if "font" in kwargs:
            super().configure(font=kwargs.pop("font"))
        if "highlightcolor" in kwargs:
            super().configure(highlightcolor=kwargs.pop("highlightcolor"))
        if "socket_color" in kwargs:
            self.input_1.configure(fg_color=kwargs.pop("socket_color"))
        if "socket_hover_color" in kwargs:
            self.input_1.configure(hover_color=kwargs.pop("socket_hover_color"))
        if "hover" in kwargs:
            super().configure(hover=kwargs.pop("hover"))
        if "socket_hover" in kwargs:
            self.input_1.configure(hover=kwargs.pop("socket_hover"))
        if "show_value" in kwargs:
            self.show_value = kwargs.pop("show_value")
            
        if len(kwargs)>0:
            raise ValueError("This option is not configurable:" + list(kwargs.keys())[0])
