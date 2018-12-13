from myhdl import *


#train and test vector contain 2 bits for label, 2 * 15 bits for coordinates (x, y)

@block
def distance(train_vector, test_vector, distance_vector):

    @always_seq(clk, reset)
    def logic():

        distance_val_1 = (train_vector[30:15] - test_vector[30:15])**2
        distance_val_2 = ((train_vector[15:0] - test_vector[15:0])>>10)*((train_vector[15:0] - test_vector[15:0])>>1024)
        distance_val = distance_val_1 + distance_val_2

        distance_vector.next = ConcatSignal(train_vector[32:30], distance_val)

    return logic

@block
def assignLabel(distance_vector_list, test_vector, k, clk, reset):

    labels = [0 for i in range(3)]
    #neighbors = [Signal(intbv(0)[8:0]) for i in range(3)]
    #maxi = Signal(intbv(0)[8:0])
    #temp_label = Signal(intbv(0)[2:0])
    #label = Signal(intbv(0)[2:0])

    @always_seq(clk.posedge, reset=reset)
    def logic():
        # add neighbors
        for i in range(k):
            #print('Neighbor[' + str(i) + '] label: ' + str(int(distance_vector_list[i][32:30])))
            temp_label = distance_vector_list[i][32:30]
            labels[temp_label] = labels[temp_label] + 1

        # check label
        print(labels)
        maxi = 0
        label = 0
        for i in range(3):
            if labels[i] > maxi:
                label = i
                #print('label= ' + str(label))
                maxi = labels[i]
                #print('maxi= ' + str(maxi))

        # return new value
        test_vector.next = ConcatSignal(intbv(label)[2:0], intbv(test_vector[30:0]))
    return instances()

@block
def assignLabel2(data_in, data_out, k, clk, reset):

    state               = enum('READ_TEST', 'CALC_NEIGH', 'CALC_LABEL', 'STOP')
    calc_state          = enum('READ_DATA', 'CALC_NEIGH')
    actual_state        = Signal(state.CALC_NEIGH)
    actual_calc_state   = Signal(calc_state.READ_DATA)
    distance_vector     = Signal(intbv(0)[32:0])
    test_vector         = Signal(intbv(0)[32:0])
    labels              = [Signal(intbv(0)[8:0]) for i in range(3)]
    counter             = Signal(intbv(k)[8:0])
    calc_counter        = Signal(intbv(3)[8:0])
    maxi                = Signal(intbv(0)[8:0])
    label               = Signal(intbv(0)[2:0])

    @always_seq(clk.posedge, reset=reset)
    def logic():
        # add neighbors
        if actual_state == state.READ_TEST:
            data_out.tvalid.next = 0
            data_out.tlast.next = 0
            data_in.tready.next = 1
            if data_in.tvalid == 1:
                test_vector.next = data_in.tdata
                if data_in.tlast == 1:
                    data_in.tready.next = 0
                    state.next = state.CALC_NEIGH
        elif actual_state == state.CALC_NEIGH:
            data_in.tready.next = 1
            data_out.tvalid.next = 0
            data_out.tlast.next = 0
            if actual_calc_state == calc_state.READ_DATA:
                distance_vector.next = data_in.tdata
            elif actual_calc_state == calc_state.CALC_NEIGH:
                if counter < k:
                    labels[int(distance_vector[32:30])].next = labels[int(distance_vector[32:30])] + 1
                    counter.next = counter + 1
                    actual_calc_state.next = calc_state.READ_DATA
                elif counter == k:
                    counter.next = 0
                    state.next = state.CALC_LABRL
        elif actual_state == state.CALC_LABEL:
            if int(calc_counter) < 3:
                if labels[int(calc_counter)] > int(maxi):
                    label.next = calc_counter
                    maxi.next = labels[int(calc_counter)]
            elif int(calc_counter) == 3:
                calc_counter.next = 0
                label.next = 0
                maxi.next = 0
                state.next = state.STOP
        elif actual_state == state.STOP:
            test_vector.next = ConcatSignal(label, test_vector[30:0])
    return instances()