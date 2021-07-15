#imports
from .utilities import get_replaced_configs, get_next_message
from ..utilities.config_file_parser import ConfigFileParser
from ..utilities.logging import Logger
from confluent_kafka import Consumer, DeserializingConsumer
import uuid, copy

class MyConsumer(Consumer) :
    """
    Class to extend Kafka Consumers for specific scenarios
    """

    def __init__(self,config_dict,logger) :
        if logger is not None :
            self.__logger = logger
        else :
            self.__logger = Logger(self.__class__)
        super().__init__(config_dict)

    @classmethod
    def from_file(cls,config_file_path,**kwargs) :
        """
        config_file_path = path to the config file to use in defining this consumer

        Possible keyword arguments:
        logger = the logger object to use
        !!!!! any other keyword arguments will be added to the configuration (with underscores replaced with dots) !!!!!
        """
        parser = ConfigFileParser(config_file_path,**kwargs)
        configs = parser.get_config_dict_for_groups(['cluster','consumer'])
        for argname,arg in kwargs.items() :
            if argname=='logger' :
                continue
            configs[argname.replace('_','.')]=arg
        #if the group.id has been set as "new" generate a new group ID
        if 'group.id' in configs.keys() and configs['group.id'].lower()=='new' :
            configs['group.id']=str(uuid.uuid1())
        return cls(configs,kwargs.get('logger'))
    
    def get_next_message(self,*poll_args,**poll_kwargs) :
        return get_next_message(self,self.__logger,*poll_args,**poll_kwargs)

class MyDeserializingConsumer(DeserializingConsumer) :
    """
    Class to extend Kafka Consumers for specific scenarios
    """

    def __init__(self,config_dict,logger) :
        if logger is not None :
            self.__logger = logger
        else :
            self.__logger = Logger(self.__class__)
        super().__init__(config_dict)

    @classmethod
    def from_file(cls,config_file_path,**kwargs) :
        """
        config_file_path = path to the config file to use in defining this consumer

        Possible keyword arguments:
        logger = the logger object to use
        !!!!! any other keyword arguments will be added to the configuration (with underscores replaced with dots) !!!!!
        """
        parser = ConfigFileParser(config_file_path,**kwargs)
        configs = parser.get_config_dict_for_groups(['cluster','consumer'])
        for argname,arg in kwargs.items() :
            if argname=='logger' :
                continue
            configs[argname.replace('_','.')]=arg
        #if the group.id has been set as "new" generate a new group ID
        if 'group.id' in configs.keys() and configs['group.id'].lower()=='new' :
            configs['group.id']=str(uuid.uuid1())
        #if one of several recognized deserializers have been given as config paramenters for the key/value deserializer, replace them with the actual class
        configs = copy.copy(get_replaced_configs(configs,'deserialization'))
        return cls(configs,kwargs.get('logger'))

    def get_next_message(self,*poll_args,**poll_kwargs) :
        return get_next_message(self,self.__logger,*poll_args,**poll_kwargs) 
