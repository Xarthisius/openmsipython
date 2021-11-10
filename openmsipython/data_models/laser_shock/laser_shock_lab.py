#imports
import os, json, requests, getpass, fmrest
from gemd.json import GEMDJson
from gemd.entity.util import complete_material_history
from .laser_shock_glass_ID import LaserShockGlassID
from .laser_shock_flyer_stack import LaserShockFlyerStack
from .laser_shock_sample import LaserShockSample
from .laser_shock_launch_package import LaserShockLaunchPackage
from .laser_shock_experiment import LaserShockExperiment

class LaserShockLab :
    """
    Representation of all the information in the Laser Shock Lab's FileMaker database in GEMD language
    """

    #################### CONSTANTS AND PROPERTIES ####################

    FILEMAKER_SERVER_IP_ADDRESS = 'https://10.173.38.223'
    DATABASE_NAME = 'Laser Shock'

    #################### PUBLIC METHODS ####################

    def __init__(self) :
        #get login credentials from the user
        self.username = os.path.expandvars('$JHED_UNAME')
        if self.username=='$JHED_UNAME' :
            self.username = (input('Please enter your JHED username: ')).rstrip()
        self.password = os.path.expandvars('$JHED_PWORD')
        if self.password=='$JHED_PWORD' :
            self.password = getpass.getpass(f'Please enter the JHED password for {self.username}: ')
        #add all the information to the lab object based on entries in the FileMaker DB
        self.specs_from_runs = []
        #"Inventory" pages (create Specs)
        self.glass_IDs = self.__getGlassIDs()
        self.epoxy_IDs = self.__getEpoxyIDs()
        self.foil_IDs = self.__getFoilIDs()
        self.spacer_IDs = self.__getSpacerIDs()
        self.flyer_cutting_programs = self.__getFlyerCuttingPrograms()
        self.spacer_cutting_programs = self.__getSpacerCuttingPrograms()
        #Flyer Stacks
        self.flyer_stacks = self.__getFlyerStacks()
        #Samples
        self.samples = self.__get_samples()
        #Launch packages
        self.launch_packages = self.__getLaunchPackages()
        #Experiments
        self.experiments = self.__get_experiments()

    def dump_to_json_files(self) :
        """
        Write out different parts of the lab as json files
        """
        #create the encoder
        encoder = GEMDJson()
        #dump the different parts of the lab data model to json files
        with open('example_laser_shock_sample_material_history.json', 'w') as fp :
            context_list = complete_material_history(self.samples[0].run) 
            fp.write(json.dumps(context_list, indent=2))
        with open('example_laser_shock_sample_spec.json', 'w') as fp: 
            fp.write(encoder.thin_dumps(self.samples[0].run.spec, indent=2))
        with open('example_laser_shock_sample.json', 'w') as fp: 
            fp.write(encoder.thin_dumps(self.samples[0].run, indent=2))
        with open('example_laser_shock_glass_ID.json', 'w') as fp: 
            fp.write(encoder.thin_dumps(self.glass_IDs[0].spec, indent=2))
        with open('example_laser_shock_experiment_template.json','w') as fp :
            fp.write(encoder.thin_dumps(self.experiments[0].template, indent=2))
        with open('example_laser_shock_experiment_spec.json','w') as fp :
            fp.write(encoder.thin_dumps(self.experiments[0].spec, indent=2))
        with open('example_laser_shock_experiment.json','w') as fp :
            fp.write(encoder.thin_dumps(self.experiments[0], indent=2))

    #################### PRIVATE HELPER FUNCTIONS ####################

    def __get_filemaker_records(self,layout_name,n_max_records=1000) :
        #disable warnings
        requests.packages.urllib3.disable_warnings()
        #create the server
        fms = fmrest.Server(self.FILEMAKER_SERVER_IP_ADDRESS,
                            user=self.username,
                            password=self.password,
                            database=self.DATABASE_NAME,
                            layout=layout_name,
                            verify_ssl=False,
                           )
        #login
        fms.login()
        #return records in the foundset
        return fms.get_records(limit=n_max_records)

    def __getGlassIDs(self) :
        glassIDs = []
        #get records from the FileMaker server
        records = self.__get_filemaker_records('Glass ID')
        for record in records :
            glassIDs.append(LaserShockGlassID(record))
        return glassIDs

    def __getEpoxyIDs(self) :
        return []

    def __getFoilIDs(self) :
        return []

    def __getSpacerIDs(self) :
        return []

    def __getFlyerCuttingPrograms(self) :
        return []

    def __getSpacerCuttingPrograms(self) :
        return []

    def __getFlyerStacks(self) :
        flyerstacks = []
        records = self.__get_filemaker_records('Flyer Stack')
        for record in records :
            flyerstacks.append(LaserShockFlyerStack(record,self.specs_from_runs,
                                                    self.glass_IDs,self.foil_IDs,self.epoxy_IDs,
                                                    self.flyer_cutting_programs))
        return flyerstacks

    def __get_samples(self) :
        samples = []
        records = self.__get_filemaker_records('Sample')
        for record in records :
            samples.append(LaserShockSample(record,self.specs_from_runs))
        return samples

    def __getLaunchPackages(self) :
        launchpackages = []
        records = self.__get_filemaker_records('Launch Package')
        for record in records :
            launchpackages.append(LaserShockLaunchPackage(record,self.specs_from_runs,
                                                          self.flyer_stacks,self.spacer_IDs,
                                                          self.spacer_cutting_programs,self.samples))
        return launchpackages

    def __get_experiments(self) :
        experiments = []
        records = self.__get_filemaker_records('Experiment')
        for record in records :
            experiments.append(LaserShockExperiment(record,self.specs_from_runs))
        return experiments

#################### MAIN FUNCTION ####################

def main() :
    #build the model of the lab
    model = LaserShockLab()
    #dump its pieces to json files
    model.dump_to_json_files()

if __name__=='__main__' :
    main()
