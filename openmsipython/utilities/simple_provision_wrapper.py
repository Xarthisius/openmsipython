#imports
import pathlib, shutil, logging, urllib.request, kafkacrypto
from argparse import ArgumentParser
from ..shared.logging import Logger
from ..shared.config_file_parser import ConfigFileParser
from .misc import cd

#constants
LOGGER = Logger('ProvisionNode',logging.INFO)
KC_PATH = kafkacrypto.__path__
SP_NAME = 'simple-provision.py'
GITHUB_URL = f'https://raw.githubusercontent.com/tmcqueen-materials/kafkacrypto/master/tools/{SP_NAME}'
TEMP_DIR_PATH = pathlib.Path(__file__).parent.parent/'my_kafka'/'config_files'/'temp_kafkacrypto_dir'

def main() :
    #command line arguments
    parser = ArgumentParser()
    parser.add_argument('--script-path', type=pathlib.Path, default='.',
                        help=f'Path to the {SP_NAME} script available from the KafkaCrypto Github')
    args = parser.parse_args()
    #make sure the temp directory doesn't exist
    if TEMP_DIR_PATH.is_dir() :
        LOGGER.error(f'ERROR: the {TEMP_DIR_PATH} directory should not exist!',RuntimeError)
    #get the location of the simple-provision script
    kcsp_code = None
    kcsp_loc = None
    if args.script_path is not None: 
        #path to the script itself was given
        if args.script_path.is_file() :
            kcsp_loc = args.script_path
            kcsp_code = open(args.script_path).read()
        #directory containing the script was given
        elif args.script_path.is_dir() :
            if (args.script_path/SP_NAME).is_file() :
                kcsp_loc = args.script_path/SP_NAME
                kcsp_code = open(args.script_path/SP_NAME).read()
    if kcsp_code is None :
        #if not set yet, try getting from the kafkacrypto install location (works if installed with --editable)
        if len(KC_PATH)==1 :
            to_try = pathlib.Path(KC_PATH[0]).parent/'tools'/SP_NAME
            if to_try.is_file() :
                kcsp_loc = to_try
                kcsp_code = open(to_try).read()
    if kcsp_code is None :
        #if all else fails, try getting from the Github webpage
        try :
            kcsp_code = urllib.request.urlopen(GITHUB_URL).read()
            kcsp_loc = GITHUB_URL
        except :
            pass
    if kcsp_loc is None or kcsp_code is None :
        LOGGER.error(f'ERROR: failed to find the {SP_NAME} script!',RuntimeError)
    #run simple-provision
    try :
        if not TEMP_DIR_PATH.is_dir() :
            TEMP_DIR_PATH.mkdir(parents=True)
        with cd(TEMP_DIR_PATH) :
            exec(kcsp_code)
    except Exception as e :
        LOGGER.error(f'ERROR: failed to run {SP_NAME} from {kcsp_loc}! Exception: {e}',RuntimeError)
    #make sure required files exist and move them into a new directory named for the node_ID
    try :
        new_files = {}
        exts = ['.config','.seed','.crypto']
        for ext in exts :
            n_files = 0
            for fp in TEMP_DIR_PATH.glob(f'*{ext}') :
                n_files+=1
                new_files[ext] = fp.resolve()
            if n_files!=1 :
                LOGGER.error(f'ERROR: found {n_files} new {ext} files in {TEMP_DIR_PATH}',RuntimeError)
        node_id = None
        for ext in exts :
            filename = new_files[ext].name
            this_node_id = ((filename).split(ext))[0]
            if node_id is None :
                node_id = this_node_id
            elif node_id!=this_node_id :
                LOGGER.error(f'ERROR: found a file called {filename} that conflicts with node_id {node_id}!',RuntimeError)
        cfp = ConfigFileParser(new_files['.config'],logger=LOGGER)
        default_dict = cfp.get_config_dict_for_groups('DEFAULT')
        if 'node_id' not in default_dict.keys() :
            LOGGER.error(f"ERROR: node_id not listed in {new_files['.config']}!")
        elif default_dict['node_id']!=node_id :
            LOGGER.error(f"ERROR: node_id listed in {new_files['.config']} mismatched to filenames ({node_id})!")
        new_dirpath = TEMP_DIR_PATH.parent/node_id
        if new_dirpath.is_dir() :
            LOGGER.error(f'ERROR: directory at {new_dirpath} already exists!')
        TEMP_DIR_PATH.rename(new_dirpath)
        LOGGER.info(f'Successfuly set up new KafkaCrypto node called "{node_id}"')
    except Exception as e :
        errmsg = f'ERROR: Running {kcsp_loc} did not produce the expected output! Temporary directories '
        errmsg+= f'will be removed and you will need to try again. Exception: {e}'
        LOGGER.error(errmsg)
    finally :
        if TEMP_DIR_PATH.is_dir() :
            shutil.rmtree(TEMP_DIR_PATH)

if __name__=='__main__' :
    main()