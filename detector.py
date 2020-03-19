import collections 
# From DataFormats/DetId/interface/DetId.h
# From Geometry/TrackerNumberingBuilder/README.md


DetectorId = collections.namedtuple('DetectorId', ['name', 'detector_id'])
tracker = DetectorId('Tracker', 1)
muon = DetectorId('Muon', 2)
ecal = DetectorId('Ecal', 3)
hcal = DetectorId('Hcal', 4)
calo = DetectorId('Calo', 5)
forward = DetectorId('Forward', 6)
very_forward = DetectorId('VeryForward', 7)
hg_cal_ee = DetectorId('HGCalEE', 8)
hg_cal_hsi = DetectorId('HGCalHSi', 9)
hg_cal_hsc = DetectorId('HGCalHSc', 10)
hg_cal_trigger = DetectorId('HGCalTrigger', 11)

SubDetectorId = collections.namedtuple('SubDetectorId', ['name', 'sub_detector_id', 'start_bit', 'hex_mask'])
tib = SubDetectorId('TIB', 3, 14, 0x7) 
tid = SubDetectorId('TID', 4, 9, 0x3)
tob = SubDetectorId('TOB', 5, 14, 0x7)
tec = SubDetectorId('TEC', 6, 5, 0x7)

sub_detectors = [tib,tid,tob,tec]

layers = {
(3,1):'TIB_L1' ,
(3,2):'TIB_L2' ,
(3,3):'TIB_L3' ,
(3,4):'TIB_L4' ,
(4,1):'TID_R1' ,
(4,2):'TID_R2' ,
(4,3):'TID_R3' ,
(5,1):'TOB_L1' ,
(5,2):'TOB_L2' ,
(5,3):'TOB_L3' ,
(5,4):'TOB_L4' , 
(5,5):'TOB_L5' ,
(5,6):'TOB_L6' ,
(6,1):'TEC_R1' ,
(6,2):'TEC_R2' ,
(6,3):'TEC_R3' ,
(6,4):'TEC_R4' ,
(6,5):'TEC_R5' ,
(6,6):'TEC_R6' ,
(6,7):'TEC_R7'
}



def read_id(id, start_bit , hex_mask):
    return (id>>start_bit)&hex_mask

class TrackerDetector:
    _detector_mask = 0xF
    _sub_detector_mask = 0x7
    _detector_offset = 28
    _sub_detector_offset = 25

    def __init__(self, raw_id):
        self.raw_id = raw_id
        self.detector_id = read_id(raw_id, self._detector_offset, self._detector_mask) 
        if self.detector_id != tracker.detector_id: 
            raise ValueError('Detector ID should be equal to 1 for the Tracker. Here {}'.format(self.detector_id)) 
        self.sub_detector_id = read_id(raw_id, self._sub_detector_offset, self._sub_detector_mask)
        for sub_detector in sub_detectors:
            if self.sub_detector_id == sub_detector.sub_detector_id:
                self.layer_number = read_id(raw_id, sub_detector.start_bit, sub_detector.hex_mask)
                self.layer_tuple = self.sub_detector_id, self.layer_number 
                try: 
                    self.layer_name = layers[(self.layer_tuple)] 
                except KeyError:
                    print('Tuple not matched with any of the tracker layers. Here {}'.format(self.layer_tuple))
                break
        else:
            self.layer_number = None
            self.layer_tuple = self.sub_detector_id, None
            self.layer_name = None
    

    def __repr__(self):
        return 'TrackerDetector(sub detector ID:{0}, layer number:{1})'.format(*self.layer_tuple)
