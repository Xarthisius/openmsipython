#imports
from config import TEST_CONST
from openmsipython.data_file_io.data_file_directory import DataFileUploadDirectory
from openmsipython.utilities.logging import Logger
import unittest, pathlib, logging, shutil

#constants
LOGGER = Logger(pathlib.Path(__file__).name.split('.')[0],logging.ERROR)
UPDATE_SECS = 5
TIMEOUT_SECS = 60

class TestDataFileDirectory(unittest.TestCase) :
    """
    Class for testing DataFileDirectory functions (without interacting with the Kafka cluster)
    """

    def test_filepath_should_be_uploaded(self) :
        dfd = DataFileUploadDirectory(TEST_CONST.TEST_DATA_DIR_PATH,logger=LOGGER)
        LOGGER.set_stream_level(logging.INFO)
        LOGGER.info('\nExpecting three errors below:')
        LOGGER.set_stream_level(logging.ERROR)
        with self.assertRaises(TypeError) :
            dfd._filepath_should_be_uploaded(None)
        with self.assertRaises(TypeError) :
            dfd._filepath_should_be_uploaded(5)
        with self.assertRaises(TypeError) :
            dfd._filepath_should_be_uploaded('this is a string not a path!')
        self.assertFalse(dfd._filepath_should_be_uploaded(TEST_CONST.TEST_DATA_DIR_PATH/'.this_file_is_hidden'))
        self.assertFalse(dfd._filepath_should_be_uploaded(TEST_CONST.TEST_DATA_DIR_PATH/'this_file_is_a_log_file.log'))
        for fp in TEST_CONST.TEST_DATA_DIR_PATH.glob('*') :
            if fp.name.startswith('.') or fp.name.endswith('.log') :
                self.assertFalse(dfd._filepath_should_be_uploaded(fp.resolve()))
            else :
                self.assertTrue(dfd._filepath_should_be_uploaded(fp.resolve()))
        subdir_path = TEST_CONST.TEST_DATA_DIR_PATH / 'this_subdirectory_should_not_be_uploaded'
        subdir_path.mkdir()
        try :
            self.assertFalse(dfd._filepath_should_be_uploaded(subdir_path))
        except Exception as e :
            raise e
        finally : 
            shutil.rmtree(subdir_path)
