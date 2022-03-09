#imports
import pathlib, uuid
from confluent_kafka.serialization import DoubleSerializer, IntegerSerializer, StringSerializer
from confluent_kafka.serialization import DoubleDeserializer, IntegerDeserializer, StringDeserializer
from ..shared.config import UTIL_CONST
from ..shared.config_file_parser import ConfigFileParser
from .serialization import DataFileChunkSerializer, DataFileChunkDeserializer

class MyKafkaConfigFileParser(ConfigFileParser) :
    """
    A class to parse configurations from files
    """

    #################### CONSTANTS ####################

    SERIALIZERS = [
        StringSerializer,
        IntegerSerializer,
        DoubleSerializer,
        DataFileChunkSerializer,
    ]

    DESERIALIZERS = [
        StringDeserializer,
        IntegerDeserializer,
        DoubleDeserializer,
        DataFileChunkDeserializer,
    ]

    #################### PROPERTIES ####################

    @property
    def cluster_configs(self) :
        if self.__cluster_configs is None :
            self.__cluster_configs = self.__get_config_dict('cluster')
        return self.__cluster_configs
    @property
    def producer_configs(self) :
        if self.__producer_configs is None :
            pcs = self.__get_config_dict('producer')
            self.__producer_configs = MyKafkaConfigFileParser.get_replaced_configs(pcs,'serialization')
        return self.__producer_configs
    @property
    def consumer_configs(self) :
        if self.__consumer_configs is None :
            ccs = self.__get_config_dict('consumer')
            #if the group.id has been set as "new" generate a new group ID
            if 'group.id' in ccs.keys() and ccs['group.id'].lower()=='create_new' :
                ccs['group.id']=str(uuid.uuid1())
            #if the auto.offset.reset was given as "none" then remove it from the ccs
            if 'auto.offset.reset' in ccs.keys() and ccs['auto.offset.reset']=='none' :
                del ccs['auto.offset.reset']
            self.__consumer_configs = MyKafkaConfigFileParser.get_replaced_configs(ccs,'deserialization')
        return self.__consumer_configs

    #################### PUBLIC FUNCTIONS ####################

    def __init__(self,*args,**kwargs) :
        super().__init__(*args,**kwargs)
        self.__cluster_configs = None
        self.__producer_configs = None
        self.__consumer_configs = None
        self.kc_config_file_str = self.__get_kc_config_file_str()

    @staticmethod
    def get_replaced_configs(configs,replacement_type) :
        """
        Returns a configuration dictionary with (de)serialization parameters replaced by instances of corresponding classes

        configs = the configurations dictionary to alter and return
        replacement_type = a string indicating the type of replacement that should be performed
        """
        if replacement_type=='serialization' :
            classes = MyKafkaConfigFileParser.SERIALIZERS
        elif replacement_type=='deserialization' :
            classes = MyKafkaConfigFileParser.DESERIALIZERS
        else :
            raise ValueError(f'ERROR: unrecognized replacement_type "{replacement_type}" in get_replaced_configs!')
        for cfg_name,cfg_value in configs.items() :
            for c in classes :
                if cfg_value==c.__name__ :
                    configs[cfg_name] = c()
                    break
        return configs

    #################### PRIVATE HELPER FUNCTIONS ####################

    def __get_config_dict(self,group_name) :
        to_return = {}
        if group_name in self.available_group_names :
            to_return = self.get_config_dict_for_groups(group_name)
        return to_return

    def __get_kc_config_file_str(self) :
        """
        Returns the path to the config file that KafkaCrypto needs based on the current configs.
        Return value is a string as expected by KafkaCrypto.
        If no config file is found according to the conventions listed below, this function returns None 
        and it will be assumed that no configuration for KafkaCrypto exists

        Options are:
        1) The regular config file has a "kafkacrypto" section with a "config_file" parameter that is the 
        path to the KafkaCrypo config file
        2) The regular config file has a "kafkacrypto" section with a "node_id" parameter corresponding to 
        a named subdirectory in openmsipython/my_kafka/config_files that was created when the node was provisioned
        """
        if 'kafkacrypto' in self.available_group_names :
            kc_configs = self.get_config_dict_for_groups('kafkacrypto')
            #option 1 above
            if 'config_file' in kc_configs.keys() :
                path_as_str = (kc_configs['config_file']).lstrip('file#')
                if not pathlib.Path(path_as_str).is_file() :
                    errmsg = f'ERROR: KafkaCrypto config file {path_as_str} (from config file {self.filepath}) not found!'
                    self.logger.error(errmsg,FileNotFoundError)
                return path_as_str
            #option 2 above
            elif 'node_id' in kc_configs.keys() :
                node_id = kc_configs['node_id']
                dirpath = UTIL_CONST.CONFIG_FILE_DIR / node_id
                filepath = dirpath / f'{node_id}.config'
                if (not dirpath.is_dir()) or (not filepath.is_file()) :
                    errmsg = f'ERROR: no KafkaCrypto config file found in the default location ({filepath}) '
                    errmsg+= f'for node ID = {node_id}'
                    self.logger.error(errmsg,FileNotFoundError)
                return str(filepath)
        #no config file found
        return None