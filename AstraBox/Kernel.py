from re import T
import tkinter as tk
from asyncio.windows_events import NULL
import os
import logging
import subprocess
import asyncio
import shutil
import platform

import AstraBox.WorkSpace as WorkSpace
from AstraBox.Models.RunModel import RunModel
import AstraBox.Astra as Astra

proc = NULL

current_working_directory = ''

async def run(cmd, logger, stdinput = None):
    global proc
    proc = await asyncio.create_subprocess_exec(
        cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    if stdinput !=None:
        proc.stdin.write(stdinput)    
    #proc.stdin.write(b"1\n1\n1\n1\n1\n")

    while proc.returncode == None:
        data = await proc.stdout.readline()
        line = data.decode('ascii').rstrip()
        if line == '':
            break
        logger.info(line)
        print(proc.returncode)


    # Wait for the subprocess exit.
    await proc.wait()


async def run_shell(cmd, logger):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()


    if stdout:
        logger.info(f'[stdout]\n{stdout.decode("cp866")}')
    if stderr:
        #for line in iter(stderr.readline(),''):
        #    logger.error(line.rstrip())
        logger.error(f'[stderr]\n{stderr.decode("cp866")}')
    print(f'[{cmd!r} exited with {proc.returncode}]')

def log_subprocess_output(pipe, logger):
    for line in iter(pipe.readline, b''): # b'\n'-separated lines
        logger.info('got line from subprocess: %r', line)

async def test_logger(logger):
        logger.info('before sleep')
        await asyncio.sleep(5)
        logger.info('after sleep')
        print('hello')

def isBlank(myString):
    return not (myString and myString.strip())

def isNotBlank(myString):
    return bool(myString and myString.strip())

class Worker:

    def get_logger(self, logger_name):
        logger = logging.getLogger(logger_name)
        while logger.hasHandlers():
            logger.removeHandler(logger.handlers[0])
        logger.setLevel(logging.DEBUG) 
        log_file = os.path.join(self.work_folder, f'{logger_name}.log')
        formatter = logging.Formatter('%(asctime)s: %(message)s', datefmt='%H:%M:%S')
        file_handler = logging.FileHandler(log_file, mode='w')
        file_handler.setFormatter(formatter)        
        logger.addHandler(file_handler)
        # with this pattern, it's rarely necessary to propagate the error up to parent
        logger.propagate = False
        return logger

    on_progress = None

    def __init__(self, model: RunModel) -> None:
        self.error_flag = False
        self.stdinput = None
        self.run_model = model
        self.work_folder = self.run_model.get_work_folder()
        self.logger = self.get_logger('kernel')
        self.logger.info( type(self)) 
        self.logger.log(logging.INFO, 'folder: ' + self.work_folder) 

    def set_model_status(self, status):
        self.run_model.data['status'] = status
        if self.on_progress:
            self.on_progress(2)

    async def run(self, cmd, shell = False):
        self.error_flag = False
        self.logger.log(logging.INFO, f"run_cmd: {cmd}")
        #os.chdir(self.work_folder)
        #self.logger.log(logging.INFO, f"CWD: {os.getcwd()}")
        if shell:
            self.proc = await asyncio.create_subprocess_shell(
                cmd,
                bufsize=0,
                #universal_newlines= True,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)
        else:                        
            self.proc = await asyncio.create_subprocess_exec(
                cmd,
                #universal_newlines= True,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)

        if self.stdinput !=None:
            self.proc.stdin.write(self.stdinput)    
        #self.proc.stdin.write(b"1\n1\n1\n1\n1\n")

        while self.proc.returncode == None:
            data = await self.proc.stdout.readline()
            line = data.decode('ascii').rstrip()

            if self.proc.stdout.at_eof(): break
            if self.on_progress:
                self.on_progress(2)
                
            if line.startswith(' done'):
                progress = float(line[10:])
                if self.on_progress:
                    self.on_progress(progress)
                continue
            if 'FATAL ERROR' in line:
                self.error_flag = True
            self.logger.info(line)

        stdout, stderr = await self.proc.communicate()
        lines = stdout.decode('ascii').split("\r\n")
        for line in lines:
            if isNotBlank(line):
                self.logger.info(line)

        lines = stderr.decode('ascii').split("\r\n")
        for line in lines:
            if isNotBlank(line):
                self.logger.error(line)

 

    def terminate(self):
        self.proc.terminate()
        self.logger.info(f'Termitate')
        self.set_model_status('term')

def copy_file(src, dst):
    try:
        shutil.copyfile(src, dst)
        print(f" copy {src} to {dst}")
 
    except shutil.SameFileError:
        print("Source and destination represents the same file.")
 
    except IsADirectoryError:
        print("Destination is a directory.")
 
    except PermissionError:
        print("Permission denied.")
 
    except:
        print(f"Error occurred while copying file: {src} to {dst}")


def copy_file_to_folder(src, dst):
    try:
        shutil.copy(src, dst)
        print(f" copy {src} to {dst}")
 
    except shutil.SameFileError:
        print("Source and destination represents the same file.")
 
    except IsADirectoryError:
        print("Destination is a directory.")
 
    except PermissionError:
        print("Permission denied.")
 
    except:
        print(f"Error occurred while copying file: {src} to {dst}")

   

class AstraWorker(Worker):
    def __init__(self, model: RunModel, astra_profile) -> None:
        super().__init__(model)
        self.astra_profile = astra_profile

    def WSL_Run(self, work_folder, command):
            ps_cmd = f'wsl --cd {work_folder} {command}'
            print(ps_cmd)
            #self.logger.info(f'run: {command}')
            with asyncio.Runner() as runner:
                runner.run(self.run(ps_cmd, shell=True))
            if self.on_progress:
                self.on_progress(0)

    def clear_work_folders(self):
        for key, folder in Astra.data_folder.items():
            clear_cmd = f'rm -f {self.astra_profile["profile"]}/{folder}*.*'  
            self.WSL_Run(self.astra_profile["home"], clear_cmd)

    def copy_data(self):
        zip_file = self.run_model.prepare_run_data()
        self.logger.info(f'copy : {zip_file}')
        dest = f'{self.astra_profile["dest"]}/{self.astra_profile["profile"]}'
        self.logger.info(f'to: {dest}')
        copy_file_to_folder(zip_file, dest)
        #unpack_cmd = f'unzip -o race_data.zip -d {self.astra_profile["profile"]}'
        unpack_cmd = f'unzip -o race_data.zip'
        wd = f'{self.astra_profile["home"]}/{self.astra_profile["profile"]}'
        self.WSL_Run(wd, unpack_cmd)

    def pack_data(self):
        self.logger.info('pack data')
        wd = f'{self.astra_profile["home"]}/{self.astra_profile["profile"]}'
        pack_cmd = f'zip -r race_data.zip dat'
        self.WSL_Run(wd, pack_cmd)
        pack_cmd = f'zip -r race_data.zip lhcd'
        self.WSL_Run(wd, pack_cmd)
        #asyncio.run(self.run(pack_cmd, shell=True))

    def start(self):
        #if self.test_folder(): return
        #self.initialization()
        self.logger.info(f'start {self.run_model.name}')

        self.clear_work_folders()
        self.copy_data()

        self.set_model_status('run')
        
        astra_cmd = f'./run10.sh {self.astra_profile["profile"]} {self.run_model.exp_model.path.name} {self.run_model.equ_model.path.name}'

        run_cmd = f'start wsl  --cd {self.astra_profile["home"]} {astra_cmd}'
        asyncio.run(self.run(run_cmd, shell=True))
        #self.WSL_Run(self.astra_profile["home"], astra_cmd)
 
        self.logger.info('finish')

        self.pack_data()

        #race_zip_file = f'Data/races/race_{self.run_model.name}.zip'
        zip_path = WorkSpace.getDataSource('races').destpath.joinpath(f'race_{self.run_model.name}.zip')
        race_zip_file = str(zip_path)
        src = f'{self.astra_profile["dest"]}/{self.astra_profile["profile"]}/race_data.zip'
        copy_file(src, race_zip_file)
        self.run_model.race_zip_file = race_zip_file

        self.logger.info('the end')