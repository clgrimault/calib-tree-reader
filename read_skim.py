import argparse
import re
import ROOT

from detector import TrackerDetector, layers, sub_detectors
from dict_layers import layers_with_rings, partitions

#from collections import namedtuple
#import collections

# Options
parser = argparse.ArgumentParser()
parser.add_argument('-m', '--max_events', type=int, default=1000,
                    help ='maximum events')
parser.add_argument('-l', '--log_freq', type=int, default=100,
                    help ='log frequency')
parser.add_argument('-r', '--run', type=int, default=316113,
                    help ='')
parser.add_argument('-f', '--file', type=str,
                    help ='')
parser.add_argument('--pu_min', type=float, default=10,
                    help ='')
parser.add_argument('--pu_max', type=float, default=60,
                    help ='')
parser.add_argument('--pu_step', type=float, default=1,
                    help ='')
args = parser.parse_args()



        

class Layer:
    def __init__(self, raw_id):
        self.raw_id = raw_id
        self.partition = (raw_id>>25)&0x7

        if self.partition == 4: # TID
            #self.layer = (raw_id>>11)&0x3 # wheel
            self.layer = (raw_id>>9)&0x3 # ring
        elif self.partition == 6: # TEC
            #self.layer = (raw_id>>14)&0xF # wheel
            self.layer = (raw_id>>5)&0x7 #ring
        else:
            self.layer = (raw_id>>14)&0x7

        self.id_tuple = (self.partition, self.layer)
        self.name = ''
        for layer_id_tuple, layer_name in layers_with_rings.items():
            if self.id_tuple == layer_id_tuple:
                self.name = layer_name



#in_file = ROOT.TFile.Open('../test/skimCalibTree_Fill_7252_Aug_04_2019.root')
in_file = ROOT.TFile.Open(str(args.file))

match = re.search('_Run_([\d]*)_Oct_2[\d]_2019_(s[\d]*)', args.file)

print(str(match.group(0)))

out_file_hist = ROOT.TFile('test.root'.format(str(match.group(1)) , str(match.group(2))),
                           'recreate')


def create_ROOT_dir(out_file, dir_name):
    return out_file.mkdir(dir_name)

#def create_ROOT_dir_dict(out_file, dir_names):
    #return {dir_name: create_ROOT_dir(out_file, dir_name) for dir_name in dir_names} 
    

def convert_Camel_case_to_snake_case(string):
    string = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
    print(string)
    print(re.sub('([a-z0-9])([A-Z])', r'\1_\2', string).lower())
    #return re.sub(r'(?<!^)(?=[A-Z])', '_', string).lower()
    #return re.sub(r'(?=[A-Z])', '_', string).lower()


dir_names = [
'chargeOverPath',
'chargeOverPathOverG2',
'chargeOverPathforCW1',
'chargeOverPathOverG2forCW1',
'clusterWidth'
]

for dir_name in dir_names:
    print dir_name
#print {dir_name: create_ROOT_dir(out_file_hist, dir_name) for dir_name in dir_names}


#convert_Camel_case_to_snake_case('chargeOverPath')
#convert_Camel_case_to_snake_case('chargeOverPathOver12G21ForCW1')

#ROOT_dir_dict = create_ROOT_dir_dict(out_file, dir_names)

#print ROOT_dir_dict

out_dir_charge_over_path = out_file_hist.mkdir('chargeOverPath')
out_dir_charge_over_path_over_g2 = out_file_hist.mkdir('chargeOverPathOverG2')

out_dir_charge_over_path_cw1 = out_file_hist.mkdir('chargeOverPathforCW1')
out_dir_charge_over_path_over_g2_cw1 = out_file_hist.mkdir('chargeOverPathOverG2forCW1')

out_dir_cluster_width = out_file_hist.mkdir('clusterWidth')


PU_MIN = args.pu_min
PU_MAX = args.pu_max
PU_STEP = args.pu_step

print(PU_MIN)
print(PU_MAX)

#plot1D_charge_over_path_by_layer = {}
#plot1D_charge_over_path_by_partition = {}
#plot1D_charge_over_path_over_g2_by_layer = {}
#plot1D_charge_over_path_over_g2_by_partition = {}


#plot1D_charge_over_path_cw1_by_layer = {}
#plot1D_charge_over_path_cw1_by_partition = {}
#plot1D_charge_over_path_over_g2_cw1_by_layer = {}
#plot1D_charge_over_path_over_g2_cw1_by_partition = {}


#plot1D_cluster_width_by_layer = {}
#plot1D_cluster_width_by_partition = {}

# partitions (TIB,TOC,TEC,TID)


def frange(start, stop, increment):
    x = start if isinstance(increment, int) else float(start)
    while x <= stop:
        yield x 
        x += increment
    
def float_to_str(number):
    if isinstance(number, int): 
        return str(number)
    elif isinstance(number, float):
        return re.sub('[.,]','p',str(number))
    else:
        raise TypeError('This number is not an int or a float')

class TrackerRootTH1:
    def __init__(self, var_name, var_nbins, var_min, var_max, per_pile_up):
        self.var_name = var_name
        self.var_nbins = var_nbins
        self.var_min = var_min 
        self.var_max = var_max
        self.per_pile_up = per_pile_up  

    def check_compliance_bool_nargs(self, kwargs):
        if (len(kwargs)==0 and self.per_pile_up):
            raise TypeError('Need a pile-up value according to the boolean')
        if (len(kwargs)==1 and not self.per_pile_up):
            raise TypeError('No need for pile-up value according to the boolean')
        if len(kwargs) > 1:
            raise TypeError('Too many optional arguments: only the pile-up value')

    def create_TH1_name(self, layer_name, **kwargs):
        self.check_compliance_bool_nargs(kwargs)
        if self.per_pile_up:
            return self.var_name + '_' + layer_name + '_PU_' + float_to_str(kwargs['pile_up'])
        else: 
            return self.var_name + '_' + layer_name

    def create_ROOT_TH1(self, layer_name, **kwargs):
        self.check_compliance_bool_nargs(kwargs)
        if self.per_pile_up:
            return ROOT.TH1F(self.create_TH1_name(layer_name, pile_up=kwargs['pile_up']), '', self.var_nbins, self.var_min, self.var_max)
        else:
            return ROOT.TH1F(self.create_TH1_name(layer_name), '', self.var_nbins, self.var_min, self.var_max)

    def create_ROOT_TH1_dict_per_layer(self):
        dict_per_layer = {(layer_tuple,pile_up): self.create_ROOT_TH1(layer_name, pile_up=pile_up) for (layer_tuple,layer_name) in layers.items() for pile_up in frange(PU_MIN, PU_MAX, PU_STEP)} if self.per_pile_up else {layer_tuple: self.create_ROOT_TH1(layer_name) for (layer_tuple,layer_name) in layers.items()}
        return dict_per_layer

    def create_ROOT_TH1_dict_per_sub_detector(self):
        dict_per_sub_detector = {(sub_detector.sub_detector_id, pile_up): self.create_ROOT_TH1(sub_detector.name, pile_up=pile_up) for sub_detector in sub_detectors for pile_up in frange(PU_MIN, PU_MAX, PU_STEP)} if self.per_pile_up else {sub_detector.sub_detector_id: self.create_ROOT_TH1(sub_detector.name) for sub_detector in sub_detectors}
        return dict_per_sub_detector




#test = TrackerRootTH1('charge', 1000,0,1000,False) 
#print test.create_ROOT_TH1_dict()
#print test.create_TH1_name('TOB_L2',10)
#print test.var_nbins
#print test.create_TH1_name('TOB_L2', pile_up=10)
#print test.create_ROOT_TH1_dict_per_layer()
#print test.create_ROOT_TH1_dict_per_sub_detector()

#print [(test_det.name , test_det.sub_detector_id) for test_det in sub_detectors]


'''
def create_ROOT_TH1_dict(var_name, var_min, var_max, var_bins):
    
    test = {(layer_tuple,pile_up): create_ROOT_TH1(var_name, layer_name, pile_up, min_value, max_value, bins)
            for (layer_tuple,layer_name) in layers.items() for pile_up in frange(PU_MIN, PU_MAX, PU_STEP)}
    print test 
'''
#create_ROOT_TH1_dict('string',0,1000,1000)
#print create_TH1_name('charge','TOB_L2',5)
#print float_to_str(6.55)

'''
for partition_id, partition_name in partitions.items():
    for pu in range(PU_MIN, PU_MAX + 1):
        out_dir_charge_over_path.cd()
        plot1D_charge_over_path_by_partition[(partition_id, pu)] = ROOT.TH1F(
            'chargeOverPath_' + partition_name + '_PU_' + str(pu),
            '', 1000, 0, 1000)
        out_dir_charge_over_path_over_g2.cd()
        plot1D_charge_over_path_over_g2_by_partition[(partition_id, pu)] = ROOT.TH1F(
            'chargeOverPathOverG2_' + partition_name + '_PU_' + str(pu),
            '', 1000, 0, 1000)
        out_dir_charge_over_path_cw1.cd()
        plot1D_charge_over_path_cw1_by_partition[(partition_id, pu)] = ROOT.TH1F(
            'chargeOverPathforCW1_' + partition_name + '_PU_' + str(pu),
            '', 1000, 0, 1000)
        out_dir_charge_over_path_over_g2_cw1.cd()
        plot1D_charge_over_path_over_g2_cw1_by_partition[(partition_id, pu)] = ROOT.TH1F(
            'chargeOverPathOverG2forCW1_' + partition_name + '_PU_' + str(pu),
            '', 1000, 0, 1000)
    out_dir_cluster_width.cd()
    plot1D_cluster_width_by_partition[partition_id] = ROOT.TH1F(
            'clusterWidth_' + partition_name, '', 40, 0, 40)
''' 

'''
# layers
for layer_id_tuple, layer_name in layers_with_rings.items():
    for pu in range(PU_MIN, PU_MAX + 1):
        out_dir_charge_over_path.cd()
        plot1D_charge_over_path_by_layer[(layer_id_tuple, pu)] = ROOT.TH1F(
            'chargeOverPath_' + layer_name + '_PU_' + str(pu),
            '', 1000, 0, 1000)
        out_dir_charge_over_path_over_g2.cd()
        plot1D_charge_over_path_over_g2_by_layer[(layer_id_tuple, pu)] = ROOT.TH1F(
            'chargeOverPathOverG2_' + layer_name + '_PU_' + str(pu),
            '', 1000, 0, 1000)
        out_dir_charge_over_path_cw1.cd()
        plot1D_charge_over_path_cw1_by_layer[(layer_id_tuple, pu)] = ROOT.TH1F(
            'chargeOverPathforCW1_' + layer_name + '_PU_' + str(pu),
            '', 1000, 0, 1000)
        out_dir_charge_over_path_over_g2_cw1.cd()
        plot1D_charge_over_path_over_g2_cw1_by_layer[(layer_id_tuple, pu)] = ROOT.TH1F(
            'chargeOverPathOverG2forCW1_' + layer_name + '_PU_' + str(pu),
            '', 1000, 0, 1000)
    out_dir_cluster_width.cd()
    plot1D_cluster_width_by_layer[layer_id_tuple] = ROOT.TH1F(
            'clusterWidth_' + layer_name, '', 40, 0, 40)
'''

out_dir_charge_over_path.cd()
plot1D_charge_over_path_by_layer = TrackerRootTH1('chargeOverPath', 1000, 0, 1000, True).create_ROOT_TH1_dict_per_layer()
plot1D_charge_over_path_by_partition = TrackerRootTH1('chargeOverPath', 1000, 0, 1000, True).create_ROOT_TH1_dict_per_sub_detector()

out_dir_charge_over_path_over_g2.cd()
plot1D_charge_over_path_over_g2_by_layer = TrackerRootTH1('chargeOverPathOverG2', 1000, 0, 1000, True).create_ROOT_TH1_dict_per_layer()
plot1D_charge_over_path_over_g2_by_partition = TrackerRootTH1('chargeOverPathOverG2', 1000, 0, 1000, True).create_ROOT_TH1_dict_per_sub_detector()

out_dir_charge_over_path_cw1.cd()
plot1D_charge_over_path_cw1_by_layer = TrackerRootTH1('chargeOverPathforCW1', 1000, 0, 1000, True).create_ROOT_TH1_dict_per_layer()
plot1D_charge_over_path_cw1_by_partition = TrackerRootTH1('chargeOverPathforCW1', 1000, 0, 1000, True).create_ROOT_TH1_dict_per_sub_detector()

out_dir_charge_over_path_over_g2_cw1.cd()
plot1D_charge_over_path_over_g2_cw1_by_layer = TrackerRootTH1('chargeOverPathOverG2forCW1', 1000, 0, 1000, True).create_ROOT_TH1_dict_per_layer()
plot1D_charge_over_path_over_g2_cw1_by_partition = TrackerRootTH1('chargeOverPathOverG2forCW1', 1000, 0, 1000, True).create_ROOT_TH1_dict_per_sub_detector()

out_dir_cluster_width.cd()
plot1D_cluster_width_by_layer = TrackerRootTH1('clusterWidth', 40, 0, 40, False).create_ROOT_TH1_dict_per_layer()
plot1D_cluster_width_by_partition = TrackerRootTH1('clusterWidth', 40, 0, 40, False).create_ROOT_TH1_dict_per_sub_detector()







max_events = args.max_events if args.max_events >= 0 else in_file.GainCalibration.GetEntries()
#max_events = 5000

"""
gainused     : G2 gain applied on the cluster charge
gainusedTick : G1 gain applied on the cluster charge
"""


tree_variables = {
    'charge':'GainCalibrationcharge', 
    'path':'GainCalibrationpath', 
    'gain_used':'GainCalibrationgainused',
    'raw_id':'GainCalibrationrawid',
    'nstrips':'GainCalibrationnstrips'
}


def round_float_nearest(number, base):
    return round(number / base) * base

#def normalise_variable(var, *args):

#exec("test_{0} = 4".format('charge'))
#print test_charge
print tree_variables.keys()
print tree_variables.values()

for n_event, event in enumerate(in_file.GainCalibration):
    if n_event%args.log_freq==0:
        print('events processed : {0} / {1}'.format(n_event, max_events))
    if n_event > max_events: break
    #for charge, path, gain_used, raw_id, cluster_width in zip(
        #event.GainCalibrationcharge,
        #event.GainCalibrationpath,
        #event.GainCalibrationgainused,
	#event.GainCalibrationrawid,
	#event.GainCalibrationnstrips,
	#):
    for charge, path, gain_used, raw_id, cluster_width in zip(
        event.GainCalibrationcharge,
        event.GainCalibrationpath,
        event.GainCalibrationgainused,
	event.GainCalibrationrawid,
	event.GainCalibrationnstrips,
	):   
        #
        #rint(TrackerDetector(raw_id).detector_id)
        #print(raw_id>>28)&0xF
        layer = Layer(raw_id)
        layer_test = TrackerDetector(raw_id)
        #if layer.id_tuple == layer_test.layer_tuple: 
        #print layer.id_tuple , layer_test.layer_tuple
        #print layer_test
        #print "###################"
        #if layer.partition != layer_test.sub_detector_id: 
            #print layer.partition , layer_test.sub_detector_id
            #print "###################"
        for layer_id_tuple in layers_with_rings.keys():
            if (layer_id_tuple == layer.id_tuple and
                PU_MIN <= event.PU <= PU_MAX):
                #
                plot1D_charge_over_path_by_layer[(layer.id_tuple,
                    round_float_nearest(event.PU, PU_STEP))].Fill(charge / path)
                plot1D_charge_over_path_by_partition[(layer.partition,
                    round_float_nearest(event.PU, PU_STEP))].Fill(charge / path)
                plot1D_charge_over_path_over_g2_by_layer[(layer.id_tuple,
                    round_float_nearest(event.PU, PU_STEP))].Fill(charge / path / gain_used)
                plot1D_charge_over_path_over_g2_by_partition[(layer.partition,
                    round_float_nearest(event.PU, PU_STEP))].Fill(charge / path / gain_used)
                plot1D_cluster_width_by_layer[layer.id_tuple].Fill(cluster_width)
                plot1D_cluster_width_by_partition[layer.partition].Fill(cluster_width)
            if cluster_width == 1:
                for layer_id_tuple in layers_with_rings.keys():
                    if (layer_id_tuple == layer.id_tuple and
                        PU_MIN <= event.PU <= PU_MAX):
                        #
                        plot1D_charge_over_path_cw1_by_layer[(layer.id_tuple,
                            round_float_nearest(event.PU, PU_STEP))].Fill(charge / path)
                        plot1D_charge_over_path_cw1_by_partition[(layer.partition,
                            round_float_nearest(event.PU, PU_STEP))].Fill(charge / path)
                        plot1D_charge_over_path_over_g2_cw1_by_layer[(layer.id_tuple,
                            round_float_nearest(event.PU, PU_STEP))].Fill(charge / path / gain_used)
                        plot1D_charge_over_path_over_g2_cw1_by_partition[(layer.partition,
                            round_float_nearest(event.PU, PU_STEP))].Fill(charge / path / gain_used)
    

out_file_hist.Write()
out_file_hist.Close()
