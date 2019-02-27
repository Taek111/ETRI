import AiR
import os




path="F:/KA-C003"
new_path = "F:/result/C003_filter/"


def main():
     for v in os.listdir(path):
        if v.split(".")[1] == "joints":
            new_body_info = transform_body_info(path+"/"+v)

            AiR.write_body(new_path+v, new_body_info)
            print(v)

def transform_body_info(file):
    isChanged = False
    ref = None
    error_frame= None
    body_info = AiR.read_body(file)
    robot = []
    human = []
    unused = []
    unused_id = []
    body_id = []


    for b in range(6):
        for f in range(len(body_info)):
            if body_info[f][b]["joints"][20]["trackingState"]:
                body_id.append(b)
                break

        if len(body_id) == 2:
            break


    if len(body_id) == 1:
        return body_info

    for i in range(6):
        if i not in body_id:
            unused_id.append(i)



    for f in range(len(body_info)):
        if body_info[f][body_id[0]]["joints"][20]["trackingState"] and body_info[f][body_id[1]]["joints"][20]["trackingState"]:
            if body_info[f][body_id[0]]["joints"][20]["depthX"] < body_info[f][body_id[1]]["joints"][20]["depthX"]:
                body_id.reverse()

            if f:
                for i in range(2):
                    if body_info[f-1][body_id[i]]["joints"][20]["trackingState"]:
                        ref = i

                if abs(body_info[f][body_id[ref]]["joints"][20]["depthX"]-body_info[f-1][body_id[ref]]["joints"][20]["depthX"])\
                    > abs(body_info[f][body_id[ref-1]]["joints"][20]["depthX"]-body_info[f-1][body_id[ref]]["joints"][20]["depthX"]):
                    isChanged = True
                    error_frame = f
            break

    for f in range(len(body_info)):
        if isChanged:
            body_id.reverse()
            isChanged = False
        if f == error_frame:
            body_id.reverse()

        robot.append(body_info[f][body_id[0]])
        human.append(body_info[f][body_id[1]])
        unused.append(body_info[f][unused_id[0]])

    for f in range(len(body_info)):
        body_info[f][0] = robot[f]
        body_info[f][1] = human[f]

        for b in range(2, 6):
            if b not in unused_id:
                body_info[f][b] = unused[f]


    return body_info


if __name__== "__main__":
    main()












