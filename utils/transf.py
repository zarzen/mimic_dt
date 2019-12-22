import sys
from os.path import expanduser, join
from os import listdir
import json
from collections import defaultdict
from torchvision import models


class Formatter:

    def __init__(self, log_folder) -> None:
        self.log_folder = expanduser(log_folder)

    def get_backward_ts(self):
        """ get time started of backward event
        """
        # focus on rank0 log
        log_files = listdir(self.log_folder)
        for f in log_files:
            if f.startswith("model-") and f.endswith("rank0.log"):
                backward_ts = []
                with open(join(self.log_folder, f)) as ifile:
                    for line in ifile:
                        tobj = json.loads(line)
                        if tobj['name'] == "backward":
                            # translate into microseconds
                            backward_ts.append(tobj['ts'] * 1e6)
                backward_ts.sort()
                return backward_ts
        print("No model log")
        return []

    def get_grad_complete(self):
        """"""
        log_files = listdir(self.log_folder)
        for f in log_files:
            if f.startswith("hook-") and f.endswith("rank0.log"):
                grad_comp_events = defaultdict(list)
                with open(join(self.log_folder, f)) as ifile:
                    for line in ifile:
                        # ts already in microsecond
                        _, layer_name, ts = line.strip('\n').split(',')
                        grad_comp_events[layer_name].append(float(ts))
                for lname in grad_comp_events:
                    grad_comp_events[lname].sort()
                return grad_comp_events
        print("No hook log found")
        return {}
    
    def get_model(self):
        model_names = {
            'resnet50': models.resnet50,
            'resnet101': models.resnet101,
            'vgg16': models.vgg16_bn
        }
        with open(join(self.log_folder, "config.json")) as ifile:
            config = json.load(ifile)
            for name in model_names:
                if name in config['script_path']:
                    return model_names[name]()
        print('no matching model')
        return
    
    def get_layer_size(self):
        model = self.get_model()
        layers = model.state_dict()
        ans = {}
        for lname in layers:
            n = 1
            for s in layers[lname].size():
                n *= s
            # assume float32 here, 4 bytes for 1 float
            ans[lname] = n * 4
        return ans
    
    def do(self):
        # backward timestamp, started time
        backward_ts = self.get_backward_ts()
        grad_comp_ts = self.get_grad_complete()
        layer_size = self.get_layer_size()
        n_batch = len(backward_ts)
        n_layer = len(grad_comp_ts) # not all layers have gradient

        formatted = []
        # import pdb;pdb.set_trace()
        for bidx, b_ts in enumerate(backward_ts):
            b_layer_comp_ts = []
            for lname, lsize in layer_size.items():
                try:
                    b_layer_comp_ts.append([grad_comp_ts[lname][bidx], lsize])
                except:
                    print('no gradient for', lname)

            b_layer_comp_ts.sort(key=lambda x:x[0])
            
            # transform into time intervals
            pre_ts = b_ts
            for item in b_layer_comp_ts:
                t = item[0]
                item[0] -= pre_ts
                pre_ts = t
            formatted.extend(b_layer_comp_ts)
        
        # write out
        with open(join(self.log_folder, "log_for_dt_mimic.txt"), 'w') as ofile:
            ofile.write("# first line is for explaination; "\
                "second line: number of batches; third line: number of layers; "\
                    "the rest of content are logs for mimicing distributed training\n")
            ofile.write("{}\n".format(n_batch))
            ofile.write("{}\n".format(n_layer))

            for item in formatted:
                ofile.write("{},{}\n".format(item[0], item[1]))


def main():
    """"""
    if len(sys.argv) < 2:
        print("please specify the folder, which contians horovod logs")
        return 

    transf = Formatter(sys.argv[1])
    transf.do()


if __name__ == "__main__":
    main()