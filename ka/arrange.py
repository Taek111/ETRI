import AiR_2017

BODY_COUNT = 6
JOINT_COUNT = 25

def arrange(file):
    body_info = AiR_2017.read_body(file)
    file_mode = file.split("/")[-1][0:4]
    if file_mode == "C001" or file_mode == "C002":
        n_max_skeletons = 1
    elif file_mode == "C003":
        n_max_skeletons = 2
    else:
        print("잘못된 파일입니다.")
        return

    #detect available body ID
    available_body_id = list()
    for b in range(BODY_COUNT):
        for f in range(len(body_info)):
            if body_info[f][b]["joints"][20]["depthX"]:
                available_body_id.append(b)
                break
        if len(available_body_id) == 2:
            break

    #make empty body info
    empty_joint = dict()
    empty_joint["depthX"] = 0
    empty_joint["depthY"] = 0
    empty_joint["unknown_z"] = 0
    empty_joints = list()
    for j in range(JOINT_COUNT):
        empty_joints.append(empty_joint)
    empty_body = dict()
    empty_body["joints"] = empty_joints



    #available_body_id[0]: right one, available_body_id[1]: left one
    if len(available_body_id) == 2:
        for f in range(len(body_info)):
            if body_info[f][available_body_id[0]]["joints"][20]["depthX"] and \
               body_info[f][available_body_id[1]]["joints"][20]["depthX"]:
                if body_info[f][available_body_id[0]]["joints"][20]["depthX"] < \
                        body_info[f][available_body_id[1]]["joints"][20]["depthX"]:
                    available_body_id.reverse()
                break

    n_skeletons = min(n_max_skeletons, len(available_body_id))

    #make arranged body_info
    new_body_info = list()
    for f in range(len(body_info)):
        new_body_frame = list()
        for a in range(n_skeletons):
            new_body_frame.append(body_info[f][available_body_id[a]])
        for e in range(n_skeletons, 6):
            new_body_frame.append(empty_body)
        new_body_info.append(new_body_frame)

    return new_body_info





