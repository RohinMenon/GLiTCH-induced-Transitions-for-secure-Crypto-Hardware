import numpy as np


def round_off_fn(round_off_option,sizes):
    print(f'Info: round_off_fn(): Rounding sizes by {round_off_option} method')
    if(round_off_option == "no_round_off"):
        pass
    elif(round_off_option == "half_integer_sizes"):
        sizes_half_integer = sizes * 2
        sizes_half_integer = np.around(sizes_half_integer)
        sizes = sizes_half_integer / 2
    elif(round_off_option == "integer_sizes"):
        sizes = np.around(sizes)
    elif(round_off_option == "library_sizes"):
        for i in range(len(sizes)):
            if (sizes[i] >= 1 and sizes[i] <= 1.5):
                sizes[i] = 1
            elif (sizes[i] > 1.5 and sizes[i] <= 2.5):
                sizes[i] = 2
            elif (sizes[i] > 2.5 and sizes[i] <= 3.5):
                sizes[i] = 3                        
            elif (sizes[i] > 3.5 and sizes[i] <= 5):
                sizes[i] = 4                        
            elif (sizes[i] > 5 and sizes[i] <= 7):
                sizes[i] = 6
            elif (sizes[i] > 7):
                sizes[i] = 8

    return sizes
