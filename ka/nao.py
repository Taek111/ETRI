import AiR_2017
import sys
import struct
import os
sys.path.insert(0, 'C:/Users/wrko/Desktop/project-2018-HumanCare/act2act/pre_processing/utils/')
import body
import AiR


def make_nao(file):
    file_name = file.split("/")[-1]
    file_format = file_name.split(".")[-1]
    directory = file.replace(file_name, "")

    if file_format == "joints":
        body_info = AiR.read_body(file)
    elif file_format == "dat":
        body_info = AiR_2017.read_body(file)
    else:
        print("wrong file loaded")

    nao_name = file_name.replace(file_format, "nao")

    with open (directory+nao_name, 'wb+') as fp:

        for f in range(len(body_info)):
            nao = body.convert_to_nao(body_info[f][0]["joints"])
            for angle in nao:
                fp.write(struct.pack('f', angle))


def read_nao(file):
    with open(file, 'rb') as fp:

        frame_count = int(os.path.getsize(file)/40)
        nao_info = list()
        for f in range(frame_count):
            nao = list()
            for i in range(10):
                nao.append(struct.unpack('f', fp.read(4))[0])
            nao_info.append(nao)

        return nao_info

