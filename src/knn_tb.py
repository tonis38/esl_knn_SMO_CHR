from myhdl import *

import os
import random

from knn import distance, assignLabel
from clk_stim import clk_stim

random.seed(5)
randrange = random.randrange

distance_list = []

@block
def knn_tb(vhdl_output_path = None):
    train_vector, test_vector, distance_vector = [Signal(intbv(0)[32:0]) for i in range(3)]

    distance_1 = distance(train_vector, test_vector, distance_vector)

    @instance
    def stimulus():
        for i in range(12):
            train_vector.next = ConcatSignal(Signal(intbv(randrange(3))[2:0]), Signal(intbv(randrange(10))[15:0]), Signal(intbv(randrange(10))[15:0]))
            test_vector.next = ConcatSignal(Signal(intbv(0)[2:0]), Signal(intbv(2)[15:0]), Signal(intbv(1)[15:0]))
            yield delay(10)
            print('Train: [' + str(int(train_vector[30:15])) + ',' + str(int(train_vector[15:0])) + '] Label: ' + str(int(train_vector[32:30])))
            print('Test: [' + str(int(test_vector[30:15])) + ',' + str(int(test_vector[15:0])) +  ']')
            print('Calc. distance: ' + str(float(distance_vector[30:0]) * 0.001) + ' Label: ' + str(int(distance_vector[32:30])) + '\n')
            distance_list.append(int(distance_vector))

    if vhdl_output_path is not None:
        distance_1.convert(hdl='VHDL', path=vhdl_output_path)

    return instances()

@block
def neighbor_label_tb(vhdl_output_path = None):

    reset = ResetSignal(0, active=0, async=False)
    clk = Signal(bool(0))

    distance_list = [[110, 2], [123, 1], [220, 2], [246, 0]]
    #distance_vector_list = [Signal(intbv(0)[32:0]) for i in range(len(distance_list))]
    distance_vector_list = [ConcatSignal(Signal(intbv(distance_list[i][1])[2:0]), Signal(intbv(distance_list[i][0])[30:0])) for i in range(len(distance_list))]

    test_vector = Signal(intbv(0)[32:0])

    assignLabel_1 = assignLabel(distance_vector_list, test_vector, 4, clk, reset)

    @always(delay(10))
    def clkgen():
        clk.next = not clk

    @instance
    def stimulus():
        #distance_vector_list = [ConcatSignal(Signal(intbv(distance_list[i][1])[2:0]), Signal(intbv(distance_list[i][0])[30:0])) for i in range(len(distance_list))]
        reset.next = 0
        yield clk.negedge
        reset.next = 1
        test_vector.next = ConcatSignal(Signal(intbv(0)[2:0]), Signal(intbv(2)[15:0]), Signal(intbv(1)[15:0]))
        yield clk.negedge
        raise StopSimulation()

    @instance
    def monitor():
        yield clk.posedge
        while 1:
            yield clk.posedge
            yield delay(1)
            print('Test: [' + str(int(test_vector[30:15])) + ',' + str(int(test_vector[15:0])) + '] Label:' + str(test_vector[32:30]))

    if vhdl_output_path is not None:
        assignLabel_1.convert(hdl='VHDL', path=vhdl_output_path)

    return instances()


#tb_1 = knn_tb()
#tb_2 = neighbor_label_tb()
#tb_1.run_sim()
#tb_2.run_sim()

if __name__ == '__main__':
    trace_save_path = 'out/testbench/'
    vhdl_output_path = 'out/vhdl/'
    os.makedirs(os.path.dirname(trace_save_path), exist_ok=True)
    os.makedirs(os.path.dirname(vhdl_output_path), exist_ok=True)

    for the_file in os.listdir(trace_save_path):
        file_path = os.path.join(trace_save_path, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)

    tb_1 = knn_tb()
    tb_2 = neighbor_label_tb()
    tb_1.config_sim(trace=True, directory=trace_save_path, name='knn_tb')
    tb_1.run_sim(500)
    tb_2.config_sim(trace=True, directory=trace_save_path, name='neighbor_label_tb')
    tb_2.run_sim(500)