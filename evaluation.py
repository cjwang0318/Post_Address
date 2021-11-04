from joblib.numpy_pickle_utils import xrange


def cal_accuracy_chars(test_str, groundtruth_str):
    right = 0
    wrong = 0

    test_chars = list(test_str)
    groundtruth_chars = list(groundtruth_str)
    if len(test_chars) == len(groundtruth_str):
        for i in xrange(len(test_chars)):
            if test_chars[i] == groundtruth_chars[i]:
                right = right + 1
            else:
                wrong = wrong + 1
    else:
        print(test_str + "," + groundtruth_str)
    result = [right, wrong]  # [# of right chars, # of wrong chars]
    return result


def cal_accuracy_rate(eval_result):
    accuracy_rate = eval_result[0] / (eval_result[0] + eval_result[1])
    return accuracy_rate


if __name__ == '__main__':
    test_address_str = "高雄市三民區北平一街173巷6號"
    groundtruth_address_str = "高雄市三民區北平一街173巷72號"
    eval_result = cal_accuracy_chars(test_address_str, groundtruth_address_str)
    print(eval_result)
    print(cal_accuracy_rate(eval_result))
