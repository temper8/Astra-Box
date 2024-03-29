from cgitb import enable
import tkinter as tk
import tkinter.ttk as ttk

from matplotlib import cm
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import ( FigureCanvasTkAgg, NavigationToolbar2Tk)

import AstraBox.Models.ModelFactory as ModelFactory

from AstraBox.Views.HeaderPanel import HeaderPanel
from AstraBox.Views.ExtraRaceView import ExtraRaceView


from AstraBox.Models.RaceModel import RaceModel

from AstraBox.ToolBox.ComboBox import ComboBox
from AstraBox.ToolBox.RadialDataPlot import RadialDataPlot
from AstraBox.ToolBox.TimeSeriesPlot import TimeSeriesPlot
from AstraBox.ToolBox.RadialDataPlot import RadialDataPlot
from AstraBox.ToolBox.TrajectoryPlot import TrajectoryPlot
from AstraBox.ToolBox.DistributionPlot import DistributionPlot
from AstraBox.ToolBox.SeriesPlot import SeriesPlot
from AstraBox.ToolBox.RTResultPlot import RTResultPlot
from AstraBox.ToolBox.DrivenCurrentPlot import DrivenCurrentPlot
from AstraBox.ToolBox.MaxwellPlot import MaxwellPlot
from AstraBox.ToolBox.ExecTimePlot import ExecTimePlot

class InfoPanel(tk.Frame):
    def __init__(self, master, model) -> None:
        super().__init__(master) #, text= 'Race info')
        info = {
            'Exp:': model.data['ExpModel']['name'],
            'Equ:': model.data['EquModel']['name'],
            'Ray tracing:': model.data['RTModel']['name']
            }
        for key, value in info.items():
            var = tk.StringVar(master= self, value=value)
            label = tk.Label(master=self, text=key)
            label.pack(side = tk.LEFT, ipadx=10)		
            entry = tk.Entry(self, width=15, textvariable= var, state='disabled')
            entry.pack(side = tk.LEFT)

class RaceView(ttk.Frame):
 
    def __init__(self, master, model) -> None:
        super().__init__(master)        
        self.master = master
        title = f"Race: {model.name}"
        self.header_content = { "title": title, "buttons":[('Delete', self.delete_model), ('New windows', self.open_new_windows), ('Extra', self.open_extra_race_view) ]}
        self.model = model
        self.model.load_model_data()
        self.hp = HeaderPanel(self, self.header_content)
        self.hp.grid(row=0, column=0, columnspan=5, padx=5, sticky=tk.N + tk.S + tk.E + tk.W)
        self.columnconfigure(0, weight=1)        
        self.rowconfigure(3, weight=1)    
        #self.label = ttk.Label(self,  text=f'name: {model.name}')
        #self.label.grid(row=1, column=0, padx=5, pady=5,sticky=tk.N + tk.S + tk.E + tk.W)   

        ip = InfoPanel(self, model)
        ip.grid(row=2, column=0, columnspan=5, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=3, column=0, padx=5, sticky=tk.N + tk.S + tk.E + tk.W)

        #tab_view_basic = TabViewBasic(self.notebook, model= model)
        #self.notebook.add(tab_view_basic, text="tab_view_basic", underline=0, sticky=tk.NE + tk.SW)

        time_series_view = TimeSeriesView(self.notebook, model= model)
        self.notebook.add(time_series_view, text="Time Series", underline=0, sticky=tk.NE + tk.SW)

        radial_data_view = RadialDataView(self.notebook, model= model)
        self.notebook.add(radial_data_view, text="Radial Data", underline=0, sticky=tk.NE + tk.SW)
        
        trajectory_view = TrajectoryView(self.notebook, model= model)
        self.notebook.add(trajectory_view, text="Trajectory", underline=0, sticky=tk.NE + tk.SW)

        distrib_view = DistributionView(self.notebook, model= model)
        self.notebook.add(distrib_view, text="Distribution", underline=0, sticky=tk.NE + tk.SW)

        maxwell_view = MaxwellView(self.notebook, model= model)
        self.notebook.add(maxwell_view, text="Maxwell", underline=0, sticky=tk.NE + tk.SW)

        maxwell_view = DiffusionView(self.notebook, model= model)
        self.notebook.add(maxwell_view, text="Diffusion", underline=0, sticky=tk.NE + tk.SW)        

        spectrum_view = SpectrumView(self.notebook, model= model)
        self.notebook.add(spectrum_view, text="Spectrum View", underline=0, sticky=tk.NE + tk.SW)      

        rt_result_view = RTResultView(self.notebook, model= model)
        self.notebook.add(rt_result_view, text="RT Result", underline=0, sticky=tk.NE + tk.SW)   

        dc_view = DrivenCurrentView(self.notebook, model= model)
        self.notebook.add(dc_view, text="Driven Current", underline=0, sticky=tk.NE + tk.SW)   

        et_view = ExecTimeView(self.notebook, model= model)
        self.notebook.add(et_view, text="Exec time", underline=0, sticky=tk.NE + tk.SW)  

    def delete_model(self):
        if ModelFactory.delete_model(self.model):
            self.master.show_empty_view()
        
    def open_new_windows(self):
        new_window = tk.Toplevel(self.master)
        new_window.title("Race Window")
        new_window.geometry("850x870")                
        model_view = RaceView(new_window, self.model)   
        model_view.grid(row=0, column=0, padx=10, sticky=tk.N + tk.S + tk.E + tk.W)     
        new_window.columnconfigure(0, weight=1)        
        new_window.rowconfigure(0, weight=1)    

    def open_extra_race_view(self):
        new_window = tk.Toplevel(self.master)
        new_window.title("Extra Race View")
        new_window.geometry("1150x700")                
        model_view = ExtraRaceView(new_window, self.model)   
        model_view.grid(row=0, column=0, padx=10, sticky=tk.N + tk.S + tk.E + tk.W)   

    def destroy(self):
        print("RaceView destroy")
        super().destroy()   

class TabViewBasic(ttk.Frame):
    """Базовый класс для вкладок, для перехвата события видимости, что бы потом инициализировать вкладку"""

    def __init__(self, master, model: RaceModel) -> None:
        super().__init__(master)  
        self.race_model = model

        self.first_time = True
        self.bind('<Visibility>', self.visibilityChanged)
    
    def visibilityChanged(self, event):
        if self.first_time:
            self.first_time = False
            self.init_ui()

    def init_ui(self):
        print('init TabViewBasic')
        pass

from statistics import mean 
from statistics import stdev
class ExecTimeView(TabViewBasic):
    def __init__(self, master, model: RaceModel) -> None:
        super().__init__(master, model)  

    def init_ui(self):
        print('init Exec Time View')
        self.data_series = self.race_model.get_exec_time()
        if type(self.data_series) == dict:
            self.make_plot()
        else:
            label = tk.Label(master=self, text=self.data_series)
            label.grid(row=0, column=1, padx=5, sticky=tk.N + tk.S + tk.E + tk.W)	            

    def make_plot(self):
        #keys = [self.combo1.get(), self.combo2.get(), self.combo3.get()]
        self.plot = ExecTimePlot(self, self.data_series )
        self.plot.grid(row=1, column=0,padx=4, sticky=tk.N + tk.S + tk.E + tk.W)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        text_box = tk.Text(self, height = 3, width = 20)
        text_box.grid(row=2, column=0, padx=4, pady=4, sticky=tk.N + tk.S + tk.E + tk.W)
        self.add_text(text_box)
        text_box.config(state='disabled')

    def add_text(self, text_box):
        lines = ['Summary:']
        
        for key, data in self.data_series.items():
            indent = ' ' * 2
            lines.append(indent + key)
            indent = ' ' * 4 
            lines.append(indent + f'  sum time: {sum(data["Y"])} ')
            lines.append(indent + f'mean  time: {mean(data["Y"])} ')
            lines.append(indent + f'stdev time: {stdev(data["Y"])} ')

        text_box.insert(tk.END, '\n'.join(lines))


class DrivenCurrentView(TabViewBasic):
    def __init__(self, master, model: RaceModel) -> None:
        super().__init__(master, model)  

    def init_ui(self):
        print('init Time Series View')
        self.dc_series = self.race_model.get_driven_current()
        if type(self.dc_series) == dict:
            self.make_plot()
        else:
            label = tk.Label(master=self, text=self.dc_series)
            label.grid(row=0, column=1, padx=5, sticky=tk.N + tk.S + tk.E + tk.W)	            

    def make_plot(self):
        #keys = [self.combo1.get(), self.combo2.get(), self.combo3.get()]
        self.plot = DrivenCurrentPlot(self, self.dc_series )
        self.plot.grid(row=1, column=0, columnspan=3, padx=4, sticky=tk.N + tk.S + tk.E + tk.W)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

class TimeSeriesView(TabViewBasic):
    def __init__(self, master, model: RaceModel) -> None:
        super().__init__(master, model)  

    def init_ui(self):
        print('init Time Series View')
        #self.race_model = model
        self.time_series = self.race_model.get_time_series()
        if type(self.time_series) == dict:
            keys = list(self.time_series.keys())
            print(keys)
            self.combo1 = ComboBox(self, 'View 1', keys)
            self.combo2 = ComboBox(self, 'View 2', keys)
            self.combo3 = ComboBox(self, 'View 3', keys)

            self.combo1.grid(row=0, column=0, padx=5, sticky=tk.N + tk.S + tk.E + tk.W)
            self.combo2.grid(row=0, column=1, padx=5, sticky=tk.N + tk.S + tk.E + tk.W)
            self.combo3.grid(row=0, column=2, padx=5, sticky=tk.N + tk.S + tk.E + tk.W)            

            self.combo1.set(keys[3])
            self.combo2.set(keys[4])
            self.combo3.set(keys[5])

            self.combo1.on_combo_selected = self.make_plot
            self.combo2.on_combo_selected = self.make_plot
            self.combo3.on_combo_selected = self.make_plot            

            self.make_plot()
        else:
            label = tk.Label(master=self, text=self.time_series)
            label.grid(row=0, column=1, padx=5, sticky=tk.N + tk.S + tk.E + tk.W)	
        
    def make_plot(self):
        keys = [self.combo1.get(), self.combo2.get(), self.combo3.get()]
        self.plot = TimeSeriesPlot(self, self.time_series, keys )
        self.plot.grid(row=1, column=0, columnspan=3, padx=4, sticky=tk.N + tk.S + tk.E + tk.W)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)


class RTResultView(TabViewBasic):
    def __init__(self, master, model: RaceModel) -> None:
        super().__init__(master, model)  

    def init_ui(self):
        print('init RT result View')
        self.rt_result_file_list = self.race_model.get_file_list('RT_RESULT')
        self.rt_result_dict = {}
        n = len(self.rt_result_file_list)
        if n>0: 
            start_time = 100 
            finish_time = 0
            keys = []

            for f in self.rt_result_file_list:
                time_stamp, rt_result, keys = self.race_model.get_rt_result(f)
                self.rt_result_dict[time_stamp] = rt_result
                if time_stamp>finish_time: finish_time = time_stamp
                if time_stamp<start_time: start_time = time_stamp

            self.combo1 = ComboBox(self, 'View 1', keys)
            self.combo1.grid(row=0, column=0, padx=5, sticky=tk.N + tk.S + tk.E + tk.W)
            self.combo2 = ComboBox(self, 'View 2', keys)
            self.combo2.grid(row=0, column=1, padx=5, sticky=tk.N + tk.S + tk.E + tk.W)            
 
            self.combo1.set(keys[3])
            self.combo2.set(keys[4])

            self.combo1.on_combo_selected = self.show_rt_result
            self.combo2.on_combo_selected = self.show_rt_result
            self.show_rt_result()
        else:
            label = tk.Label(master=self, text='Нет данных')
            label.grid(row=0, column=1, padx=5, sticky=tk.N + tk.S + tk.E + tk.W)	

    def show_rt_result(self):
        keys = [self.combo1.get(), self.combo2.get()]
        print(f'show_rt_result: {keys}')
        self.plot = RTResultPlot(self,self.rt_result_dict, keys)
        self.plot.grid(row=1, column=0, columnspan=3, padx=5, sticky=tk.N + tk.S + tk.E + tk.W)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)


from AstraBox.ToolBox.SpectrumPlot import SpectrumPlot, ScatterPlot2D3D

class SpectrumView(TabViewBasic):
    def __init__(self, master, model: RaceModel) -> None:
        super().__init__(master, model)  

    def init_ui(self):
        print('create SpectrumView')
        self.spectrum_model = self.race_model.get_spectrum()
        print(self.spectrum_model.get_dest_path())
        if type(self.spectrum_model.spectrum_data) is dict:
            print('загрузил спектр')
            print(len(self.spectrum_model.spectrum_data['Ntor']))
            self.make_plot()
        else:
            print(self.spectrum_model.spectrum_data)
            label = tk.Label(master=self, text='Нет данных')
            label.grid(row=0, column=1, padx=5, sticky=tk.N + tk.S + tk.E + tk.W)

    def make_plot(self):
        match self.spectrum_model.spectrum_type:
            case 'gaussian'|'spectrum_1D':
                self.spectrum_plot = SpectrumPlot(self, self.spectrum_model.spectrum_data['Ntor'], self.spectrum_model.spectrum_data['Amp']  )
            case 'scatter_spectrum':
                self.spectrum_plot = ScatterPlot2D3D(self, self.spectrum_model.spectrum_data)
            case 'spectrum_2D':
                pass       
        
        self.spectrum_plot.grid(row=1, column=0, padx=5, pady=5,sticky=tk.N + tk.S + tk.E + tk.W) 


class TrajectoryView(TabViewBasic):
    def __init__(self, master, model: RaceModel) -> None:
        super().__init__(master, model)  

    def init_ui(self): 
        self.trajectory_list = self.race_model.get_file_list('TRAJECTROY')
        self.rays_cache = {}
        n = len(self.trajectory_list)
        if n>0: 
            plasma_bound = self.race_model.read_plasma_bound()

            rays, self.start_time  = self.get_rays(0)
            _, self.finish_time  = self.get_rays(n-1)

            self.n = n

            self.time_var = tk.DoubleVar(master = self, value=self.start_time)
            self.time_var.trace_add('write', self.update_plot)

            self.time_slider = tk.Scale(master=  self, 
                                   variable = self.time_var,
                                   orient = tk.HORIZONTAL,
                                   sliderlength = 20,
                                   width = 10,
                                   label='Time scale',
                                   tickinterval= (self.finish_time-self.start_time)/7,
                                   from_= self.start_time,
                                   to= self.finish_time, 
                                   resolution= (self.finish_time-self.start_time)/n )
            self.time_slider.grid(row=0, column=0, columnspan=2, padx=5, pady=5,sticky=tk.N + tk.S + tk.E + tk.W)   


            self.index_1 = tk.IntVar(master = self, value=0)
            self.index_1.trace_add('write', self.update_plot)
            self.slider_1 = tk.Scale(master=  self, variable = self.index_1, orient = tk.HORIZONTAL, 
                                    sliderlength = 20,
                                    width = 10,            
                                    label='start ray',
                                    tickinterval= len(rays)/4,
                                    from_=0, 
                                    to=len(rays)-1, 
                                    resolution=1 )
            self.slider_1.grid(row=1, column=0, padx=5, pady=5,sticky=tk.N + tk.S + tk.E + tk.W) 

            self.index_2 = tk.IntVar(master = self, value=len(rays)-1)
            self.index_2.trace_add('write', self.update_plot)
            self.slider_2 = tk.Scale(master=  self, variable = self.index_2, orient = tk.HORIZONTAL,
                                    sliderlength = 20,
                                    width = 10,            
                                    label='numbers of ray',
                                    tickinterval= len(rays)/4,
                                    from_=0, 
                                    to=len(rays)-1, 
                                    resolution=1 )
            self.slider_2.grid(row=1, column=1, padx=5, pady=5,sticky=tk.N + tk.S + tk.E + tk.W) 

            self.plot = TrajectoryPlot(self, rays, self.start_time, plasma_bound)
            self.plot.grid(row=2, column=0, columnspan=2, sticky=tk.N + tk.S + tk.E + tk.W, pady=4, padx=8)
            self.columnconfigure(0, weight=1)
            self.columnconfigure(1, weight=1)
            self.rowconfigure(2, weight=1)
            self.len_rays = len(rays)
        else:
            label = tk.Label(master=self, text='Нет данных')
            label.grid(row=0, column=1, padx=5, sticky=tk.N + tk.S + tk.E + tk.W)            

    def get_rays(self, index):
        if not index in self.rays_cache:
            print(f'{index} not in cache')
            self.rays_cache[index] = self.race_model.get_rays(self.trajectory_list[index])
        rays, time_stamp = self.rays_cache[index]        
        return rays, time_stamp

    def update_plot(self, var, indx, mode):
        index = int((self.n-1) * (self.time_var.get()-self.start_time) / (self.finish_time-self.start_time))
        i1 = self.index_1.get()
        i2 = i1 + self.index_2.get()

        rays, time_stamp = self.get_rays(index)

        if self.len_rays != len(rays):
            self.len_rays = len(rays)
            print(f'update sliders {self.len_rays}')
            self.slider_1.configure(tickinterval= self.len_rays/4, to=self.len_rays-1)
            self.slider_2.configure(tickinterval= self.len_rays/4, to=self.len_rays-1)
        if i2>self.len_rays: i2 = self.len_rays
        if i1>self.len_rays: i1 = self.len_rays
        self.plot.update(rays[i1:i2], time_stamp)
        pass


class RadialDataView(TabViewBasic):
    def __init__(self, master, model: RaceModel) -> None:
        super().__init__(master, model)  

    def init_ui(self):   
        self.radial_data_list = self.race_model.get_file_list('RADIAL_DATA')
        n = len(self.radial_data_list)
        if n>0: 
            radial_data = self.get_radial_data(0)
            self.start_time = radial_data["Time"]
            self.finish_time = self.get_radial_data(n-1)["Time"]
            self.n = n

            self.time_var = tk.DoubleVar(master = self, value=self.start_time)
            self.time_var.trace_add('write', self.update_time_var)

            self.time_slider = tk.Scale(master=  self, 
                                   variable = self.time_var,
                                   orient = tk.HORIZONTAL,
                                   label='Time scale',
                                   tickinterval= (self.finish_time-self.start_time)/7,
                                   from_= self.start_time,
                                   to= self.finish_time, 
                                   resolution= (self.finish_time-self.start_time)/n, 
                                   length = 250 )
            self.time_slider.grid(row=1, column=0, padx=5, pady=5,sticky=tk.N + tk.S + tk.E + tk.W)       
            
            self.plot = RadialDataPlot(self, radial_data)
            self.plot.grid(row=2, column=0, sticky=tk.N + tk.S + tk.E + tk.W, pady=4, padx=8)
            self.columnconfigure(0, weight=1)
            self.rowconfigure(2, weight=1)
        else:
            label = tk.Label(master=self, text='Нет данных')
            label.grid(row=0, column=1, padx=5, sticky=tk.N + tk.S + tk.E + tk.W)

    def get_radial_data(self, index):
        file = self.radial_data_list[index]
        print(f'{file} {index}')
        return self.race_model.read_radial_data(file)

    def update_time_var(self, var, indx, mode):
        index = int((self.n-1) * (self.time_var.get()-self.start_time) / (self.finish_time-self.start_time))
        radial_data = self.get_radial_data(index)
        self.plot.update(radial_data)

    def update_var(self, var, indx, mode):
        radial_data = self.get_radial_data(self.index_var.get())
        self.plot.update(radial_data)


class DistributionView(TabViewBasic):
    def __init__(self, master, model: RaceModel) -> None:
        super().__init__(master, model)  

    def init_ui(self):   
        self.distribution_list = self.race_model.get_file_list('DISTRIBUTION') 
        n = len(self.distribution_list)
        if n>0: 
            distribution, self.start_time  =  self.get_distribution(0)
            _, self.finish_time  = self.get_distribution(n-1)
            self.n = n

            self.time_var = tk.DoubleVar(master = self, value=self.start_time)
            self.time_var.trace_add('write', self.update_time_var)

            self.time_slider = tk.Scale(master=  self, 
                                   variable = self.time_var,
                                   orient = tk.HORIZONTAL,
                                   label='Time scale',
                                   tickinterval= (self.finish_time-self.start_time)/7,
                                   from_= self.start_time,
                                   to= self.finish_time, 
                                   resolution= (self.finish_time-self.start_time)/n, 
                                   length = 250 )
            self.time_slider.grid(row=1, column=0, padx=5, pady=5,sticky=tk.N + tk.S + tk.E + tk.W)       
            
            self.plot = DistributionPlot(self, distribution, self.start_time)
            self.plot.grid(row=2, column=0, sticky=tk.N + tk.S + tk.E + tk.W, pady=4, padx=8)
            self.columnconfigure(0, weight=1)
            self.rowconfigure(2, weight=1)            
        else:
            label = tk.Label(master=self, text='Нет данных')
            label.grid(row=0, column=1, padx=5, sticky=tk.N + tk.S + tk.E + tk.W)            

    def get_distribution(self, index):
        file = self.distribution_list[index]
        print(f'{file} {index}')
        return self.race_model.read_distribution(file)

    def update_time_var(self, var, indx, mode):
        index = int((self.n-1) * (self.time_var.get()-self.start_time) / (self.finish_time-self.start_time))
        distribution, time_stamp = self.get_distribution(index)
        self.plot.update(distribution, time_stamp)

    def update_var(self, var, indx, mode):
        distribution, time_stamp  = self.get_distribution(self.index_var.get())
        self.plot.update(distribution)


class MaxwellView(TabViewBasic):
    def __init__(self, master, model: RaceModel) -> None:
        super().__init__(master, model)  

    def init_ui(self): 
        self.maxwell_list = self.race_model.get_file_list('MAXWELL')
        n = len(self.maxwell_list)
        if n>0: 
            distribution, self.start_time  =  self.get_distribution(0)
            _, self.finish_time  = self.get_distribution(n-1)
            self.n = n

            self.time_var = tk.DoubleVar(master = self, value=self.start_time)
            self.time_var.trace_add('write', self.update_time_var)

            self.time_slider = tk.Scale(master=  self, 
                                   variable = self.time_var,
                                   orient = tk.HORIZONTAL,
                                   label='Time scale',
                                   tickinterval= (self.finish_time-self.start_time)/7,
                                   from_= self.start_time,
                                   to= self.finish_time, 
                                   resolution= (self.finish_time-self.start_time)/n, 
                                   length = 250 )
            self.time_slider.grid(row=1, column=0, padx=5, pady=5,sticky=tk.N + tk.S + tk.E + tk.W)       
            
            self.plot = MaxwellPlot(self, distribution, 'Maxwell', self.start_time)
            self.plot.grid(row=2, column=0, sticky=tk.N + tk.S + tk.E + tk.W, pady=4, padx=8)
            self.columnconfigure(0, weight=1)
            self.rowconfigure(2, weight=1)            
        else:
            label = tk.Label(master=self, text='Нет данных')
            label.grid(row=0, column=1, padx=5, sticky=tk.N + tk.S + tk.E + tk.W)            

    def get_distribution(self, index):
        file = self.maxwell_list[index]
        print(f'{file} {index}')
        return self.race_model.read_maxwell_distribution(file)

    def update_time_var(self, var, indx, mode):
        index = int((self.n-1) * (self.time_var.get()-self.start_time) / (self.finish_time-self.start_time))
        distribution, time_stamp = self.get_distribution(index)
        self.plot.update(distribution, time_stamp)

    def update_var(self, var, indx, mode):
        distribution, time_stamp  = self.get_distribution(self.index_var.get())
        self.plot.update(distribution)



class DiffusionView(TabViewBasic):
    def __init__(self, master, model: RaceModel) -> None:
        super().__init__(master, model)  

    def init_ui(self): 
        self.file_list = self.race_model.get_file_list('DIFFUSION')
        n = len(self.file_list)
        if n>0: 
            distribution, self.start_time  =  self.get_distribution(0)
            _, self.finish_time  = self.get_distribution(n-1)
            self.n = n

            self.time_var = tk.DoubleVar(master = self, value=self.start_time)
            self.time_var.trace_add('write', self.update_time_var)

            self.time_slider = tk.Scale(master=  self, 
                                   variable = self.time_var,
                                   orient = tk.HORIZONTAL,
                                   label='Time scale',
                                   tickinterval= (self.finish_time-self.start_time)/7,
                                   from_= self.start_time,
                                   to= self.finish_time, 
                                   resolution= (self.finish_time-self.start_time)/n, 
                                   length = 250 )
            self.time_slider.grid(row=1, column=0, padx=5, pady=5,sticky=tk.N + tk.S + tk.E + tk.W)       
            
            self.plot = SeriesPlot(self, distribution, 'Diffusion', self.start_time, уscale_log=False)
            self.plot.grid(row=2, column=0, sticky=tk.N + tk.S + tk.E + tk.W, pady=4, padx=8)
            self.columnconfigure(0, weight=1)
            self.rowconfigure(2, weight=1)
        else:
            label = tk.Label(master=self, text='Нет данных')
            label.grid(row=0, column=1, padx=5, sticky=tk.N + tk.S + tk.E + tk.W)            

    def get_distribution(self, index):
        file = self.file_list[index]
        print(f'{file} {index}')
        return self.race_model.read_diffusion(file)

    def update_time_var(self, var, indx, mode):
        index = int((self.n-1) * (self.time_var.get()-self.start_time) / (self.finish_time-self.start_time))
        distribution, time_stamp = self.get_distribution(index)
        self.plot.update(distribution, time_stamp)

    def update_var(self, var, indx, mode):
        distribution, time_stamp  = self.get_distribution(self.index_var.get())
        self.plot.update(distribution)        