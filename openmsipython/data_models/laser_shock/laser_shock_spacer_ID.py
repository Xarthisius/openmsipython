#imports
from gemd.entity.value import NominalCategorical, NominalReal
from .attribute_templates import ATTR_TEMPL
from .object_templates import OBJ_TEMPL
from .spec_from_filemaker_record import MaterialSpecFromFileMakerRecord

class LaserShockSpacerID(MaterialSpecFromFileMakerRecord) :
    """
    GEMD representation of a type of Spacer used in the Laser Shock Lab as a Material Spec
    """

    template = OBJ_TEMPL['Spacer ID']
    process_template = OBJ_TEMPL['Purchasing Spacer']
    name_key = 'Spacer Name'
    notes_key = 'Description'
    
    @property
    def tags_keys(self) :
        return [*super().tags_keys,'Spacer ID']

    @property
    def property_dict(self) :
        return {'Spacer Thickness':{'valuetype':NominalReal,
                                   'datatype':float,
                                   'template':ATTR_TEMPL['Spacer Thickness']},
                'Spacer Material':{'valuetype':NominalCategorical,
                                   'datatype':str,
                                   'template':ATTR_TEMPL['Spacer Material']},
                'Spacer Adhesive':{'valuetype':NominalCategorical,
                                   'datatype':str,
                                   'template':ATTR_TEMPL['Spacer Adhesive Sides']},
                'Adhesive Type':{'valuetype':NominalCategorical,
                                   'datatype':str,
                                   'template':ATTR_TEMPL['Adhesive Type']},
            }

    @property
    def process_parameter_dict(self) :
        return {'Spacer Supplier':{'valuetype':NominalCategorical,
                                  'template':ATTR_TEMPL['Spacer Supplier']},
                'Spacer Part Number':{'valuetype':NominalCategorical,
                                     'template':ATTR_TEMPL['Spacer Part Number']},
            }

    @property
    def unique_values(self):
        return {**super().unique_values,'Spacer ID':self.get_tag_value('SpacerID')}

    def ignore_key(self,key) :
        if key in ['Spacer Picture'] :
            return True
        return super().ignore_key(key)
