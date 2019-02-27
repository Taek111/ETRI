from tkinter import ttk
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import filedialog
import os
import cv2
import pre_processing.Ka.AiR_2017 as AiR_2017
import pre_processing.utils.AiR as AiR
import struct
import numpy as np
from constants import connecting_joint, offset, body_colors, joint_colors, nMax

############
# *Command*
# <space-bar>: start or pause,
# <r>or<R>: activate or deactivate robot view,
# <h>or<H>: activate or deactivate human view
# <Enter>or<Double-click>: open video file
############


class MainWindow():
    def __init__(self):
        self.root = tk.Tk('Skeleton Viewer')
        self.root.geometry("1500x800+100+100")
        self.root.title("Kinect Skeleton Viewer")
        self.cur_tree_id = None
        self.video = None
        self.depth = None

        self.frame_count = 1000
        self.frame = None
        self.depth_frame = None
        self.play = False
        self.cur_image = None
        self.cur_depth = None
        self.speed = 1   # frame speed per 1ms
        self.view_mode = [False, False]  # [robot view, human view]]
        self.video_path = None
        self.active_tab = None
        self.make_frame()

    def make_frame(self):

        # Initialize main frame
        self.root.rowconfigure(0, weight=3)
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0,weight=1)

        # Initialize video frame

        self.top_frame = tk.Frame(self.root, bg='#e9e9e9')
        self.top_frame.grid(row=0, column=0, sticky='nsew')
        self.top_frame.rowconfigure(0, weight=1)
        self.notebook = ttk.Notebook(self.top_frame)
        self.notebook.place(relx=0.15, relwidth=0.85, relheight=1)
        self.notebook.bind('<<NotebookTabChanged>>', self.tab_changer)
        self.video_frame = video_frame(self)
        self.directory_box = directory_box(self)
        self.control_frame = control_frame(self)
        self.menubar = menu_frame(self)

        # Add command
        self.root.bind("<space>", self.control_frame.start_or_pause)
        self.root.bind("<r>", self.control_frame.toggle_robot)
        self.root.bind("<R>", self.control_frame.toggle_robot)
        self.root.bind("<h>", self.control_frame.toggle_human)
        self.root.bind("<H>", self.control_frame.toggle_human)

        self.video_loop()

    def video_loop(self):

        if self.play and self.video:

            if self.control_frame.trackbar.get() == self.frame_count:
                self.control_frame.trackbar.set(0)
                self.video.set(0)
                self.depth.set(0)

            available, self.cur_image = self.video.read()
            if available:
                if not self.control_frame.drag_bar:
                    self.control_frame.trackbar.set(self.video.get(cv2.CAP_PROP_POS_FRAMES)-1)
                # RGB Viewer
                self.frame = Image.fromarray(self.cur_image)
                self.frame = ImageTk.PhotoImage(image=self.frame)
                self.video_frame.frame_image["image"] = self.frame
                self.video_frame.frame_image.photo = self.frame

                # RGB-Depth Viewer
                if self.active_tab == "RGB-Depth":
                    self.video_frame.frame_RGB["image"] = self.frame
                    self.video_frame.frame_RGB.photo = self.frame
                    self.cur_depth = self.depth.read()
                    self.depth_frame = Image.fromarray(self.cur_depth)
                    self.depth_frame = ImageTk.PhotoImage(image=self.depth_frame)
                    self.video_frame.frame_Depth["image"] = self.depth_frame
                    self.video_frame.frame_Depth.photo = self.depth_frame

                if self.control_frame.trackbar.get() == self.frame_count:
                    #auto play
                    #self.auto_play()

                    #play one by one
                    self.play = False

        self.root.after(self.speed, self.video_loop)

    def auto_play(self):
        next_id = "I" + ("%03X" %(int(self.cur_tree_id.split("I")[1], 16)+1))
        if not self.directory_box.tree.exists(next_id):
            self.play = False
            return
        self.directory_box.tree.selection_set(next_id)
        self.cur_tree_id = next_id
        self.video_path= ' '.join(self.directory_box.tree.item(next_id)['values'])
        self.video = video_stream(self)
        self.control_frame.update_video_location(self)

    def tab_changer(self,event):
        index = event.widget.index("current")
        if index == 0:
            self.active_tab = "RGB"
            self.play = False
        elif index == 1:
            self.active_tab = "RGB-Depth"
            self.play = False
            self.control_frame.update_video_location(self)


class video_frame:
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(self.parent.notebook, bg='black')
        self.parent.notebook.add(self.frame, text='RGB viewer')
        self.frame_2 = tk.Frame(self.parent.notebook, bg='black')
        self.parent.notebook.add(self.frame_2, text='RGB-Depth viewer')
        self.frame_2.rowconfigure(0, weight=1)
        self.frame_2.columnconfigure(0,weight=1)
        self.frame_2.columnconfigure(1, weight=1)

        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        self.frame_image = tk.Label(self.frame, bd=0, highlightthickness=0, relief='flat', bg='black')
        self.frame_image.grid(row=0, column=0)

        self.frame_RGB = tk.Label(self.frame_2, bd=0, highlightthickness=0, relief='flat', bg='black')
        self.frame_Depth = tk.Label(self.frame_2, bd=0, highlightthickness=0, relief='flat', bg='black')
        self.frame_RGB.grid(row=0, column=0)
        self.frame_Depth.grid(row=0, column=1)

class directory_box:
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(self.parent.top_frame, width=1000, bg="#FFFFFF")
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.place(x=0, y=0, relwidth=0.15, relheight=1)
        self.tree = ttk.Treeview(self.frame, selectmode='extended')
        self.tree.grid(row=0, column=0, sticky='nsew')
        self.tree.heading('#0', text='Video List', anchor='w')
        self.tree.column('#0', width=500)
        self.xsb = ttk.Scrollbar(self.frame, orient='horizontal', command=self.tree.xview)
        self.ysb = ttk.Scrollbar(self.frame, orient='vertical', command=self.tree.yview)
        self.xsb.grid(row=1, column=0, sticky='nsew')
        self.ysb.grid(row=0, column=1, sticky='nsew')
        self.tree.configure(xscroll=self.xsb.set, yscroll=self.ysb.set)

        self.tree.bind("<Double-Button-1>", self.onClick)
        self.tree.bind("<Return>", self.onClick)
        self.child = None

    # Add directory
    def add_tree(self,path):
        self.tree.delete(*self.tree.get_children())
        for v in os.listdir(path):
            abspath = path + "/" + v
            if v.split(".")[-1] == "avi":
                self.tree.insert('', 'end', text=v, values=str(abspath), open=False)

    # Open video file
    def onClick(self, event):
        self.parent.video_path = ' '.join(self.tree.item(self.tree.selection())['values'])
        self.parent.cur_tree_id = self.tree.identify("item", event.x, event.y)
        self.parent.video = video_stream(self.parent)
        self.parent.depth = depth_info(self.parent)
        self.parent.control_frame.update_video_location(self)


class control_frame:
    def __init__(self,parent):

        self.parent = parent
        self.frame = tk.Frame(self.parent.root, bg="#01243f")
        self.frame.grid(row=1, column=0, sticky='nsew')
        self.drag_bar = False

        # Create track bar
        self.trackbar = tk.Scale(self.frame, from_=0, to=self.parent.frame_count, orient= 'horizontal')
        self.trackbar.pack(fill="x", padx=10, pady=10)
        self.trackbar.bind("<Button-1>", self.drag_trackbar)
        self.trackbar.bind("<ButtonRelease-1>", self.update_video_location)

        # Create PLAY/PAUSE button
        self.play_photo = tk.PhotoImage(file="play.png")
        self.pause_photo = tk.PhotoImage(file="pause.png")
        self.play_button = tk.Button(self.frame, text="재생", command=self.start_playing, image=self.play_photo)
        self.pause_button = tk.Button(self.frame, text="일시정지", command=self.pause_playing, image=self.pause_photo)
        self.play_button.place(relx=0.03, rely=0.5, relwidth=0.1, relheight=0.3)
        self.pause_button.place(relx=0.15, rely=0.5, relwidth=0.1, relheight=0.3)

        # Create filtering box
        self.filtering_box = tk.Frame(self.frame, bg='white')
        self.filtering_box.place(relx=0.3, rely=0.5, relwidth=0.1, relheight=0.4)
        self.filtering_label = tk.Label(self.frame,text="Displaying skeleton",bg='white')
        self.filtering_label.place(relx=0.30, rely=0.4, relwidth=0.1, relheight=0.05)
        self.chkValue_1 = tk.BooleanVar()
        self.chkValue_2 = tk.BooleanVar()
        self.check_robot = tk.Checkbutton(self.filtering_box, text="Robot", var=self.chkValue_1,
                                          command=self.robot_view)
        self.check_human = tk.Checkbutton(self.filtering_box, text="Human", var=self.chkValue_2,
                                          command=self.human_view)
        self.check_robot.pack(anchor='w', pady=10)
        self.check_human.pack(anchor='w',pady=10)


    def drag_trackbar(self, _):
        self.drag_bar = True

    # Synchronize location of video with trackbar
    def update_video_location(self,_):
        if self.parent.video:
            self.trackbar.set(self.trackbar.get())
            self.parent.video.set(self.trackbar.get())
            self.drag_bar = False

            new_frame_available, new_frame = self.parent.video.read()
            if new_frame_available:
                self.parent.cur_image = new_frame
                self.parent.frame = Image.fromarray(self.parent.cur_image)
                self.parent.frame = ImageTk.PhotoImage(image=self.parent.frame)
                # RGB Viewer
                if self.parent.active_tab == 'RGB':
                    self.parent.video_frame.frame_image["image"] = self.parent.frame
                    self.parent.video_frame.frame_image.photo = self.parent.frame
                # RGB-Depth Viewer
                elif self.parent.active_tab == 'RGB-Depth':
                    self.parent.depth.set(self.trackbar.get())
                    self.parent.cur_depth = self.parent.depth.read()
                    self.parent.depth_frame = Image.fromarray(self.parent.cur_depth)
                    self.parent.depth_frame = ImageTk.PhotoImage(image=self.parent.depth_frame)
                    self.parent.video_frame.frame_Depth["image"] = self.parent.depth_frame
                    self.parent.video_frame.frame_Depth.photo = self.parent.depth_frame
                    self.parent.video_frame.frame_RGB["image"]= self.parent.frame
                    self.parent.video_frame.frame_RGB.photo = self.parent.frame
            else:
                self.trackbar.set(0)
        else:
            self.trackbar.set(0)

    def start_playing(self):
        self.parent.play = True

    def pause_playing(self):
        self.parent.play = False

    def robot_view(self):
        if self.chkValue_1.get():
            self.parent.view_mode[0] = True
        else:
            self.parent.view_mode[0] = False
        self.update_video_location(self)

    def human_view(self):
        if self.chkValue_2.get():
            self.parent.view_mode[1] = True
        else:
            self.parent.view_mode[1] = False
        self.update_video_location(self)

    def toggle_robot(self, _):
        if self.chkValue_1.get():
            self.chkValue_1.set(False)
        else:
            self.chkValue_1.set(True)
        self.robot_view()

    def toggle_human(self, _):
        if self.chkValue_2.get():
            self.chkValue_2.set(False)
        else:
            self.chkValue_2.set(True)
        self.human_view()

    def start_or_pause(self,_):
        if not self.parent.play:
            self.parent.play = True
        else:
            self.parent.play = False

class menu_frame:
    def __init__(self, parent):
        self.parent = parent
        self.menubar = tk.Menu(self.parent.root)
        self.file_menu = tk.Menu(self.menubar, tearoff=False)
        self.file_menu.add_command(label="Open directory", command=self.open_directory)
        self.option_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.menubar.add_cascade(label="Option", menu=self.option_menu)
        self.parent.root.config(menu=self.menubar)

    # Open directory explorer
    def open_directory(self):
        folder_path = filedialog.askdirectory()
        self.parent.directory_box.add_tree(folder_path)


class video_stream:
    def __init__(self, parent):
        self.parent = parent
        self.path = self.parent.video_path
        self.stream = cv2.VideoCapture(self.path)
        self.body_info = body_info(self)
        self.parent.frame_count = self.stream.get(cv2.CAP_PROP_FRAME_COUNT) - 1
        self.parent.control_frame.trackbar["to"] = self.parent.frame_count
        self.parent.control_frame.trackbar.set(0)

        # max size of video for resizing
        self.max_w = self.parent.video_frame.frame.winfo_width()
        if self.max_w ==1:
            self.max_w = 1200
        self.max_h = self.parent.video_frame.frame.winfo_height()
        if self.max_h ==1:
            self.max_h = 553
        self.resize = None

    # Calculating size of video for resizing
    def calc_resize(self, input_image):
        # RGB Viewer
        if self.parent.active_tab == 'RGB':
            (h, w) = input_image.shape[:2]
            if 0 not in [h, w]:
                resize_x = self.max_w / w
                resize_y = self.max_h / h
                if resize_x > resize_y:
                    self.resize = tuple((int(w * resize_y), self.max_h))
                else:
                    self.resize = tuple((self.max_w, int(h * resize_x)))
        # RGB-Depth Viewer
        elif self.parent.active_tab == 'RGB-Depth':
            self.resize = tuple((int(self.max_w/2), int(self.max_w*424/1024)))
            return

    # Read 1 frame of video
    def read(self):
        available, new_frame = self.stream.read()
        new_frame = new_frame[0:1081, 234:1716]
        if available:
            new_frame = cv2.cvtColor(new_frame, cv2.COLOR_BGR2RGB)
            if not self.resize:
                self.calc_resize(new_frame)
            # Display skeleton
            for b in range(2):
                if self.parent.view_mode[b]:
                    self.draw_skeleton(new_frame, b, int(self.get(cv2.CAP_PROP_POS_FRAMES) - 1))
            new_frame = cv2.resize(new_frame, self.resize, interpolation=cv2.INTER_LINEAR)
        return available, new_frame

    def get(self, _):
        return self.stream.get(cv2.CAP_PROP_POS_FRAMES)

    def set(self, frame_num):
        self.stream.set(cv2.CAP_PROP_POS_FRAMES, frame_num)

    def release(self):
        self.stream.release()

    # Synchronize depth space with RGB space
    def vectorize_xy(self, f, b, j):
        try:
            return (int(self.body_info.filtered_data[f][b]["joints"][j]["depthX"]*1482/512+offset['x']),
                    int(self.body_info.filtered_data[f][b]["joints"][j]["depthY"]*1482/512+offset['y']))
        #스켈레톤 좌표값이 -inf가 나올 때 스켈레톤을 표시하지 않음
        except:
            return False

    def draw_skeleton(self, frame, b, f):
        try:
            for j in range(25):
                k = connecting_joint[j]
                cv2.line(frame, self.vectorize_xy(f, b, j), self.vectorize_xy(f, b, k), body_colors[b], 4)
                cv2.circle(frame, self.vectorize_xy(f, b, j), 8, joint_colors[j], -1)
        # 스켈레톤 좌표값이 -inf가 나올 때 스켈레톤을 표시하지 않음
        except:
            pass


class body_info:
    def __init__(self, parent):
        self.parent = parent
        self.path = self.parent.path.replace("avi", "joints")
        if os.path.isfile(self.path):
            self.body_data = AiR.read_body(self.path)
        else:
            self.path = self.parent.path.replace("avi", "dat")
            self.body_data = AiR_2017.read_body(self.path)
        self.body_id = self.detect_body_id()
        self.filtered_data = []
        self.correct_data()

    # Detect available body id
    def detect_body_id(self):
        body_id = []
        # 목관절의 depth값이 있는 body id를 추적
        for b in range(len(self.body_data[0])):
            for f in range(len(self.body_data)):
                if self.body_data[f][b]["joints"][20]["depthX"]:
                    body_id.append(b)
                    break
            if len(body_id) == nMax:
                break
        return body_id

    # 감지된 id를 토대로 filtered_data에 유효한 body값을 넣어주는 함수
    def correct_data(self):
        isChanged = False
        ref = None
        error_frame = None
        unused_id = None
        # body의 개수가 1개일 때
        if len(self.body_id) == 1:
            for i in range(6):
                if i not in self.body_id:
                    unused_id = i
                    break
            for f in range(len(self.body_data)):
                self.filtered_data.append([self.body_data[f][self.body_id[0]], self.body_data[f][unused_id]])
            return
         # body의 개수가 2개일 때
        for f in range(len(self.body_data)):
            # body_id[0]이 오른쪽에 오게함
            if self.body_data[f][self.body_id[0]]["joints"][20]["depthX"]\
                    and self.body_data[f][self.body_id[1]]["joints"][20]["depthX"]:
                if self.body_data[f][self.body_id[0]]["joints"][20]["depthX"]\
                        < self.body_data[f][self.body_id[1]]["joints"][20]["depthX"]:
                    self.body_id.reverse()
                # 오류 프레임 f에서 두 스켈레톤의 body id 가 바뀌었을 때를 감지
                if f:
                    for i in range(2):
                        if self.body_data[f-1][self.body_id[i]]["joints"][20]["depthX"]:
                            ref = i
                    if abs(self.body_data[f][self.body_id[ref]]["joints"][20]["depthX"]-self.body_data[f-1][self.body_id[ref]]["joints"][20]["depthX"])\
                        > abs(self.body_data[f][self.body_id[ref-1]]["joints"][20]["depthX"]-self.body_data[f-1][self.body_id[ref]]["joints"][20]["depthX"]):
                        isChanged = True
                        error_frame = f
                break

        for f in range(len(self.body_data)):
            if isChanged:
                self.body_id.reverse()
                isChanged = False
            if f == error_frame:
                self.body_id.reverse()

            self.filtered_data.append([self.body_data[f][self.body_id[0]], self.body_data[f][self.body_id[1]]])


class depth_info:
    def __init__(self,parent):
        self.frame_size = 512 * 424 * 2
        self.parent = parent
        self.path = self.parent.video_path.replace("avi", "bin")
        if os.path.isfile(self.path):
            self.file = open(self.path, 'rb')
        else:
            self.path = self.path.replace("bin", "dat")
            self.file = open(self.path, 'rb')
        self.max_w = self.parent.video_frame.frame.winfo_width()
        self.resize = tuple((int(self.max_w/2), int(self.max_w*424/1024)))

    def get(self):
        return int(self.file.tell()/self.frame_size)

    def set(self, frame_num):
        self.file.seek(self.frame_size*frame_num, 0)

    # Read 1 frame of depth video
    def read(self):
        frame_data = self.file.read(self.frame_size)
        if frame_data ==b'':
            return
        data = struct.unpack('H'* int(self.frame_size/2), frame_data)
        fixed_data = [i/8000*255 for i in data]
        image = np.reshape(fixed_data, (424,512))
        image = image.astype(np.uint8)
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        # Draw skeleton on depth video
        for b in range(2):
            if self.parent.view_mode[b]:
                self.draw_skeleton(image, b, int(self.get())-1)
        image = cv2.resize(image, self.resize, interpolation=cv2.INTER_LINEAR)
        return image

    def vectorize_xy(self, f, b, j):
        return (int(self.parent.video.body_info.filtered_data[f][b]["joints"][j]["depthX"]),
                int(self.parent.video.body_info.filtered_data[f][b]["joints"][j]["depthY"]))

    def draw_skeleton(self, frame, b, f):
        for j in range(25):
            k = connecting_joint[j]
            cv2.line(frame, self.vectorize_xy(f, b, j), self.vectorize_xy(f, b, k), body_colors[b], 2)
            cv2.circle(frame, self.vectorize_xy(f, b, j), 4, joint_colors[j], -1)


if __name__ == '__main__':
    app = MainWindow()
    app.root.mainloop()

