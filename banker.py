from typing import List
import numpy as np

"""
>>> alloc [0 0 1 2;1 0 0 0;1 3 5 4;0 6 3 2;0 0 1 4]
>>> max   [0 0 1 2;1 7 5 0;2 3 5 6;0 6 5 2;0 6 5 6]
>>> avail [1 5 2 0]
>>> request [0 4 2 0]

"""

def get_input_matrix(msg: str, example: str = None) -> str:
    try:
        print(msg)
        if example is not None:
            print(example)
        line = input(">>> ")
        return line
    except ValueError as e:
        print("Invalid input syntax, try again")
        return get_input_matrix(msg, example)


def form_matrix(string: str, shape: List[int]) -> np.ndarray:
    list_of_lists = [[int(x) for x in row.strip().split()]
                     for row in string[1:-1].split(";")]
    array = np.array(list_of_lists)
    if(array.shape[0] != shape[0] or array.shape[1] != shape[1] or len(shape) != len(array.shape)):
        raise ValueError("Wrong shape for matrix or vector")
    print(array)
    return array

def iter_processes(
    finished_list: List[bool],
    allocation_matrix: np.ndarray,
    need_matrix: np.ndarray,
    available_vector: np.ndarray,
    ids:List[str] = None) -> List[str]:
    if ids == None:
        ids = ["P{}".format(x) for x in range(len(finished_list))]
    sub_sequence = []
    for i, f in enumerate(finished_list):
        if not f and (need_matrix[i, :] <= available_vector).all():
            available_vector += allocation_matrix[i, :]
            sub_sequence.append(ids[i])
            finished_list[i] = True
    if len(sub_sequence) > 0:
        return sub_sequence + iter_processes(finished_list, allocation_matrix, need_matrix, available_vector, ids)
    else:
        
        return sub_sequence


def check_request_validity(
    av_vec : np.ndarray,
    alloc_mat : np.ndarray,
    need_mat: np.ndarray,
    vector : np.ndarray,
    idx : int,
    n_processes:int):
    if (vector > need_mat[idx, :]).all():
        return False, []
    
    if (vector > av_vec).all():
        return False, []

    av_vec -= vector
    alloc_mat[idx, :] += vector
    need_mat[idx, :] -= vector
    finished_list = [False for _ in range(n_processes)]
    need_mat[[idx, 0]] = need_mat[[0, idx]]
    alloc_mat[[idx, 0]] = alloc_mat[[0, idx]]
    ids = ["P{}".format(x) for x in range(len(finished_list))]
    ids[idx] = "P0"
    ids[0] = "P{}req".format(idx)
    sequence = iter_processes(finished_list, alloc_mat, need_mat, av_vec, ids)
    if len(sequence) == n_processes:
        return True, sequence
    else:
        return False, []




while True:
    try:
        n_resources = int(input("Insert number of resources (R): "))
        n_processes = int(input("Insert number of processes (P): "))

        matrix_line = get_input_matrix(
            "Insert the Allocation matrix of shape {} x {}".format(
                n_processes, n_resources),
            "example format of 3 x 2: [1 2;3 4;5 6]"
        )

        alloc_mat = form_matrix(matrix_line, [n_processes, n_resources])

        matrix_line = get_input_matrix(
            "Insert the Max matrix of shape {} x {}".format(
                n_processes, n_resources),
            "example format of 3 x 2: [1 2;3 4;5 6]"
        )

        max_mat = form_matrix(matrix_line, [n_processes, n_resources])

        need_mat = max_mat - alloc_mat

        print("========================= Need Matrix ========================")
        print(need_mat)

        matrix_line = get_input_matrix(
            "Insert the available vector of shape 1 x R", "example of vector of length 3: [3 4 2]")

        av_vec = form_matrix(matrix_line, [1, n_resources])

        finished = [False for _ in range(n_processes)]
        sequence = iter_processes(finished, alloc_mat, need_mat, av_vec)

        command = "D"
        while True:
            print("Enquiry safe state (S) or make a request (R) or quit (Q)")
            command = str(input("[S / R]: ")).upper()

            if command == "S":
                if len(sequence) == n_processes:
                    print("Yes")
                    print(sequence)
                else:
                    print("No")
            elif command == "R":
                idx = int(input("Insert process index: "))
                matrix_line = get_input_matrix(
                    "Insert the extra resources vector of shape 1 x R",
                    "example of vector of length 3: [3 4 2]"
                )

                vector = form_matrix(matrix_line, [1, n_resources]).reshape((n_resources,))

                valid, sequence = check_request_validity(av_vec, alloc_mat, need_mat, vector, idx, n_processes)
                if valid:
                    print("Granted safe sequence is: {}".format(sequence))
                else:
                    print("Request cannot be granted")

            elif command == "Q":
                break
            else:
                continue

    except ValueError as e:
        print(e)
        continue
