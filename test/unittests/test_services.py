#imports
import unittest, platform, shutil, pathlib, logging, time
from subprocess import check_output
from openmsipython.shared.logging import Logger
from openmsipython.services.config import SERVICE_CONST
from openmsipython.services.utilities import run_cmd_in_subprocess
from openmsipython.services.service_manager import WindowsServiceManager, LinuxServiceManager
from config import TEST_CONST

#constants
LOGGER = Logger(pathlib.Path(__file__).name.split('.')[0],logging.ERROR)

class TestServices(unittest.TestCase) :
    """
    Class for testing that Services can be installed/started/stopped/removed without any errors on Linux OS
    """

    def setUp(self) :
        self.dirs_to_delete = [TEST_CONST.TEST_DIR_SERVICES_TEST]
        for dirpath in self.dirs_to_delete :
            if not dirpath.is_dir() :
                dirpath.mkdir(parents=True)
        self.argslists_by_class_name = {
                'UploadDataFile':[TEST_CONST.TEST_DATA_FILE_PATH,],
                'DataFileUploadDirectory':[TEST_CONST.TEST_DIR_SERVICES_TEST,],
                'DataFileDownloadDirectory':[TEST_CONST.TEST_DIR_SERVICES_TEST,],
                'LecroyFileUploadDirectory':[TEST_CONST.TEST_DIR_SERVICES_TEST,
                                             '--config',TEST_CONST.TEST_CONFIG_FILE_PATH,
                                             '--topic_name','test_pdv_plots'],
                'PDVPlotMaker':[TEST_CONST.TEST_DIR_SERVICES_TEST,
                                '--config',TEST_CONST.TEST_CONFIG_FILE_PATH,
                                '--topic_name','test_pdv_plots',
                                '--consumer_group_id','create_new'],
                'OSNStreamProcessor':['phy210127-bucket01',
                                      '--logger_file',TEST_CONST.TEST_DIR_SERVICES_TEST/'test_osn_stream_processor.log',
                                      '--config',TEST_CONST.TEST_CONFIG_FILE_PATH_OSN,
                                      '--topic_name','osn_test',
                                      '--consumer_group_id','create_new'],
            }

    def tearDown(self) :
        for dirpath in self.dirs_to_delete :
            if dirpath.is_dir() :
                shutil.rmtree(dirpath)

    @unittest.skipIf(platform.system()!='Windows','test can only be run on Windows')
    def test_install_start_stop_remove_windows_services(self) :
        """
        Make sure every possible Windows service can be installed, started, checked, stopped, and removed
        """
        self.assertTrue(len(SERVICE_CONST.AVAILABLE_SERVICES)>0)
        for sd in SERVICE_CONST.AVAILABLE_SERVICES :
            try :
                service_class_name = sd['class'].__name__
                if service_class_name not in self.argslists_by_class_name.keys() :
                    raise ValueError(f'ERROR: no arguments to use found for class "{service_class_name}"!')
                service_name = service_class_name+'_test'
                argslist_to_use = []
                for arg in self.argslists_by_class_name[service_class_name] :
                    argslist_to_use.append(str(arg))
                manager = WindowsServiceManager(service_name,
                                                service_class_name=service_class_name,
                                                argslist=argslist_to_use,
                                                interactive=False,
                                                logger=LOGGER)
                manager.install_service()
                for run_mode in ('start','status','stop','remove') :
                    time.sleep(1)
                    manager.run_manage_command(run_mode,False,False)
                time.sleep(1)
            except Exception as e :
                raise e
            finally :
                if (SERVICE_CONST.WORKING_DIR/f'{service_name}_env_vars.txt').exists() :
                   (SERVICE_CONST.WORKING_DIR/f'{service_name}_env_vars.txt').unlink() 
    
    @unittest.skipIf(platform.system()!='Linux' or 
                     check_output(['ps','--no-headers','-o','comm','1']).decode().strip()!='systemd',
                     'test requires systemd running on Linux')
    def test_install_start_stop_remove_linux_services(self) :
        """
        Make sure every possible Linux service can be installed, started, checked, stopped, and removed
        """
        self.assertTrue(len(SERVICE_CONST.AVAILABLE_SERVICES)>0)
        for sd in SERVICE_CONST.AVAILABLE_SERVICES :
            try :
                service_class_name = sd['class'].__name__
                if service_class_name not in self.argslists_by_class_name.keys() :
                    raise ValueError(f'ERROR: no arguments to use found for class "{service_class_name}"!')
                service_name = service_class_name+'_test'
                argslist_to_use = []
                for arg in self.argslists_by_class_name[service_class_name] :
                    argslist_to_use.append(str(arg))
                manager = LinuxServiceManager(service_name,
                                                service_class_name=service_class_name,
                                                argslist=argslist_to_use,
                                                interactive=False,
                                                logger=LOGGER)
                manager.install_service()
                for run_mode in ('start','status','stop','remove') :
                    time.sleep(1)
                    manager.run_manage_command(run_mode,False,False)
                time.sleep(1)
                self.assertFalse((SERVICE_CONST.DAEMON_SERVICE_DIR/f'{service_name}.service').exists())
            except Exception as e :
                raise e
            finally :
                if (SERVICE_CONST.DAEMON_SERVICE_DIR/f'{service_name}.service').exists() :
                    run_cmd_in_subprocess(['sudo',
                                           'rm',
                                           str((SERVICE_CONST.DAEMON_SERVICE_DIR/f'{service_name}.service'))],
                                           logger=LOGGER)
                if (SERVICE_CONST.WORKING_DIR/f'{service_name}_env_vars.txt').exists() :
                   (SERVICE_CONST.WORKING_DIR/f'{service_name}_env_vars.txt').unlink() 
                if (SERVICE_CONST.WORKING_DIR/f'{self.service_name}.service').exists() :
                   (SERVICE_CONST.WORKING_DIR/f'{self.service_name}.service').unlink() 