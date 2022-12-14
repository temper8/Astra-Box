import os 
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog as fd
from matplotlib import cm
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import ( FigureCanvasTkAgg, NavigationToolbar2Tk)
from AstraBox.Views.SpectrumPlot import Plot2D
from AstraBox.Views.SpectrumPlot import SpectrumPlot

class OptionsPanel(tk.Frame):
    def __init__(self, master, options) -> None:
        super().__init__(master)
        self.options = options
        for key, value in options.items():
            var = tk.DoubleVar(master= self, name = key, value=value)
            label = tk.Label(master=self, text=key)
            label.pack(side = tk.LEFT, ipadx=10)		
            entry = tk.Entry(self, width=10, textvariable= var)
            entry.pack(side = tk.LEFT)

    def update(self):
        for key in self.options.keys():
            var = tk.DoubleVar(master= self, name = key)
            self.options[key] = var.get()


class GaussianSpectrumView(tk.LabelFrame):
    def __init__(self, master, model=None) -> None:
        super().__init__(master, text='Gaussian Spectrum')        

        self.header_content = { "title": 'title', "buttons":[('Save', None), ('Delete', None), ('Clone', None)]}
        self.model = model
        self.label = ttk.Label(self,  text=f'Spectrum View')
        self.label.grid(row=0, column=0, padx=5, pady=5,sticky=tk.N + tk.S + tk.E + tk.W)  

        self.options_box = OptionsPanel(self, self.model.setting['options'])
        self.options_box.grid(row=0, column=0, padx=5, pady=5,sticky=tk.N + tk.S + tk.E + tk.W) 
        btn = ttk.Button(self, text= 'Generate', command=self.generate)
        btn.grid(row=0, column=1, padx=5, pady=5,sticky=tk.N + tk.S + tk.E + tk.W)  
        self.columnconfigure(0, weight=1)        
        #self.rowconfigure(0, weight=1)    
        self.generate()

    def generate(self):
        self.options_box.update()
        self.model.generate()
        self.spectrum_plot = SpectrumPlot(self, self.model.spectrum_data['Ntor'], self.model.spectrum_data['Amp']  )
        self.spectrum_plot.grid(row=1, column=0, padx=5, pady=5,sticky=tk.N + tk.S + tk.E + tk.W)  


class ControlPanel(tk.Frame):
    def __init__(self, master, path, load_file_cb = None) -> None:
        super().__init__(master)
        self.load_file_cb = load_file_cb
        self.path_var = tk.StringVar(master= self, value=path)
        label = tk.Label(master=self, text='Source:')
        label.pack(side = tk.LEFT, ipadx=10)		
        entry = tk.Entry(self, width=55, textvariable= self.path_var)
        entry.pack(side = tk.LEFT, ipadx=10)
        btn1 = ttk.Button(self, text= 'Select file', command=self.select_file)
        btn1.pack(side = tk.LEFT, ipadx=10)   
        #btn2 = ttk.Button(self, text= 'Load', command=self.load_file)
        #btn2.pack(side = tk.LEFT, ipadx=10)

    def load_file(self):
        if self.load_file_cb:
            self.load_file_cb(self.path_var.get())

    def select_file(self):
        filename = fd.askopenfilename()
        self.path_var.set(filename)
        if self.load_file_cb:
            self.load_file_cb(filename)



class Spectrum1DView(tk.LabelFrame):
    def __init__(self, master, model=None) -> None:
        super().__init__(master, text='Spectrum 1D')        

        self.header_content = { "title": 'title', "buttons":[('Save', None), ('Delete', None), ('Clone', None)]}
        self.model = model

        self.control_panel = ControlPanel(self, self.model.setting['source'], self.on_load_file)
        self.control_panel.grid(row=0, column=0, padx=5, pady=5,sticky=tk.N + tk.S + tk.E + tk.W) 
        self.columnconfigure(0, weight=1)        
        #self.rowconfigure(0, weight=1)    
        self.make_plot()

    def on_load_file(self, filename):
        print(filename)
        self.model.setting['source'] = filename
        self.make_plot()

    def make_plot(self):
        self.model.read_spcp1D()
        self.spectrum_plot = SpectrumPlot(self, self.model.spectrum_data['Ntor'], self.model.spectrum_data['Amp']  )
        self.spectrum_plot.grid(row=1, column=0, padx=5, pady=5,sticky=tk.N + tk.S + tk.E + tk.W) 


class Spectrum2DView(tk.LabelFrame):
    def __init__(self, master, model=None) -> None:
        super().__init__(master, text='Spectrum 2D')        

        self.header_content = { "title": 'title', "buttons":[('Save', None), ('Delete', None), ('Clone', None)]}
        self.model = model

        self.control_panel = ControlPanel(self, self.model.setting['source'], self.on_load_file)
        self.control_panel.grid(row=0, column=0, padx=5, pady=5,sticky=tk.N + tk.S + tk.E + tk.W) 
        self.columnconfigure(0, weight=1)        
        #self.rowconfigure(0, weight=1)    
        self.make_plot()

    def on_load_file(self, filename):
        print(filename)
        self.model.setting['source'] = filename
        self.make_plot()

    def make_plot(self):
        self.model.read_spcp2D()
            
        if self.model.spectrum_data == None:
            label = ttk.Label(self, text="Spectrum None", width=20)
            label.grid(row=1, column=0, padx=5, pady=5,sticky=tk.N + tk.S + tk.E + tk.W)       
        else:
            self.spectrum_plot = Plot2D(self, self.model.spectrum_data)
            self.spectrum_plot.grid(row=1, column=0, padx=5, pady=5,sticky=tk.N + tk.S + tk.E + tk.W)  
        #self.model.read_spcp1D()
        #self.spectrum_plot = SpectrumPlot(self, self.model.spectrum_data['Ntor'], self.model.spectrum_data['Amp']  )
        #self.spectrum_plot.grid(row=1, column=0, padx=5, pady=5,sticky=tk.N + tk.S + tk.E + tk.W) 

