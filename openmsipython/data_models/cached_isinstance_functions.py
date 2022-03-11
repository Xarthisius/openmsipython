#imports
from gemd.entity.template import PropertyTemplate, ParameterTemplate, ConditionTemplate
from gemd.entity.template import MaterialTemplate, ProcessTemplate, MeasurementTemplate
from gemd.entity.object import MaterialSpec, ProcessSpec, IngredientSpec, MeasurementSpec
from gemd.entity.object import MaterialRun, ProcessRun, IngredientRun, MeasurementRun
from .utilities import cached_isinstance_generator

#Some cached isinstance functions to reduce overhead
isinstance_template = cached_isinstance_generator((PropertyTemplate, ParameterTemplate, ConditionTemplate,
                                                   MaterialTemplate, ProcessTemplate, MeasurementTemplate))
isinstance_spec = cached_isinstance_generator((MaterialSpec,ProcessSpec,IngredientSpec,MeasurementSpec))
isinstance_run = cached_isinstance_generator((MaterialRun,ProcessRun,IngredientRun,MeasurementRun))
isinstance_process_spec = cached_isinstance_generator(ProcessSpec)
isinstance_material_ingredient_spec = cached_isinstance_generator((MaterialSpec,IngredientSpec))
isinstance_ingredient_spec = cached_isinstance_generator(IngredientSpec)
isinstance_ingredient_run = cached_isinstance_generator(IngredientRun)
