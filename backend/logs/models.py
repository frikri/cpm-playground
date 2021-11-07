from math import log
import os 
from django.db import models
import pandas as pd 
from pm4py.objects.conversion.log import variants
from pm4py.objects.log.importer import xes
from pm4py.objects.log.importer.xes import importer as xes_importer_factory
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.conversion.log.variants import to_data_frame as log_to_data_frame
from pm4py.algo.filtering.dfg import dfg_filtering
from pm4py.utils import get_properties
from pm4py.statistics.traces.log import case_statistics
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py import discover_directly_follows_graph
from pm4py import get_event_attribute_values
from helpers.dfg_helper import convert_dfg_to_dict
from helpers.g6_helpers import dfg_dict_to_g6
from django.forms.models import model_to_dict

class Log(models.Model):
    log_file = models.FileField(upload_to='uploaded_logs')
    log_name = models.CharField(max_length=500)
    def filename(self):
        return os.path.basename(self.log_file.name)
    def pm4py_log(self):
        _, file_extension = os.path.splitext(self.log_file.path)

        if file_extension == '.csv':
            log = pd.read_csv(self.log_file.path, sep=',')
            log = dataframe_utils.convert_timestamp_columns_in_df(log)
            log = log_converter.apply(log)

        else:
            log = xes_importer_factory.apply(self.log_file.path)
        return log








class LogObjectHandler():
    log_object = None 
    log = None
    def __init__(self, log_object):
        self.log_object = log_object
        self.log = log_object.pm4py_log()

    def pm4py_log(self):
        return self.log 

    def pk(self):
        return self.log.pk

    def to_df(self):
        return log_to_data_frame.apply(self.log)

    def get_properties(self):
        log_df = self.to_df()
        results = {}
        for columnName, columnValues in log_df.iteritems():
            values_without_na = columnValues.dropna()
            results[columnName] = list(set(values_without_na.tolist()))
        return results

    def generate_dfg(self, percentage_most_freq_edges=100, type=dfg_discovery.Variants.FREQUENCY):
        log = self.pm4py_log()
        dfg, sa, ea = discover_directly_follows_graph(log)
        activities_count = get_event_attribute_values(log, "concept:name")
        dfg, sa, ea, activities_count = dfg_filtering.filter_dfg_on_paths_percentage(dfg, sa, ea, activities_count, percentage_most_freq_edges)
        return dfg
    def g6(self):
        return dfg_dict_to_g6(convert_dfg_to_dict(self.generate_dfg()))
    
    def to_dict(self):
        ret = model_to_dict(self.log_object)
        ret['g6'] = self.g6()
        ret['properties'] = self.get_properties()
        return ret