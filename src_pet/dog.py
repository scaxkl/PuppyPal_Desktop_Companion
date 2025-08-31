import tkinter as tk
from PIL import Image, ImageTk, ImageSequence


class DogPet:
    def __init__(self, role_actions):
        self.role_actions = role_actions
        self.flat_gifs = [
            action["path"]
            for role in self.role_actions.values()
            for action in role
        ]
        # 初始化主窗口
        self.root = tk.Tk()
        self.root.overrideredirect(True)  # 隐藏窗口边框
        self.root.attributes('-topmost', True)  # 窗口置顶
        self.transparent_color = 'gray15'  # 不要使用白色
        self.root.attributes('-transparentcolor', self.transparent_color)  # 设置gray15为透明色

        # 创建菜单系统
        self.menu = tk.Menu(self.root, tearoff=0)
        self._build_menu()  # 分离菜单构建逻辑

        # 加载第一个GIF（使用展平列表的第一个元素）
        self.current_gif_index = 0
        self.load_gif(self.flat_gifs[self.current_gif_index])

        # 窗口位置设置
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.x = screen_width - self.width - 50  # 右边距50像素
        self.y = screen_height - self.height - 100  # 底边距100像素
        self.root.geometry(f'{self.width}x{self.height}+{self.x}+{self.y}')

        # 创建画布
        self.canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            bg=self.transparent_color,
            highlightthickness=0
        )
        self.canvas.pack()

        # 显示 GIF
        self.current_frame = 0
        self.pet_image = self.canvas.create_image(0, 0, anchor='nw', image=self.frames[0])

        # 血条
        self.max_health = 10
        self.health = self.max_health
        self.health_indicator = self.canvas.create_text(35, 35, anchor="nw", text='❤' * self.health, fill='red')

        # 饥饿值
        self.hunger =8
        self.hunger_indicator = self.canvas.create_text(35, 50, anchor="nw", text='🍔' * self.hunger, fill='yellow')

        # 绑定事件
        self.canvas.bind("<ButtonPress-1>", self.on_press)  # 左键点击拖动
        self.canvas.bind("<B1-Motion>", self.on_drag)  # 左键拖动
        self.canvas.bind("<Button-3>", self.show_menu)  # 右键菜单

        # 启动动画
        self.animate_gif()
        self.root.mainloop()

    def load_gif(self, gif_path):
        """加载 GIF 文件并提取帧"""
        self.gif = Image.open(gif_path)
        self.frames = []
        self.delays = []

        # 提取所有帧和延迟时间
        for frame in ImageSequence.Iterator(self.gif):
            self.frames.append(ImageTk.PhotoImage(frame.convert('RGBA')))
            try:
                self.delays.append(frame.info['duration'])
            except KeyError:
                self.delays.append(100)  # 默认延迟 100ms

        # 设置窗口大小
        self.width = self.frames[0].width()
        self.height = self.frames[0].height()

    def _build_menu(self):
        """构建层级式右键菜单"""
        # 清除现有菜单项
        self.menu.delete(0, "end")
        # 为每个角色创建子菜单
        for role_name, actions in self.role_actions.items():
            role_menu = tk.Menu(self.menu, tearoff=0)
            # 添加动作项
            for action in actions:
                role_menu.add_command(label=action["name"],
                                      command=lambda p=action["path"]: self.switch_gif_by_path(p))
            self.menu.add_cascade(label=role_name, menu=role_menu)

        # 添加退出项
        self.menu.add_separator()
        self.menu.add_command(label="Exit", command=self.root.destroy)

    def switch_gif_by_path(self, gif_path):
        """切换 GIF 动画"""
        # 更新当前索引
        self.current_gif_index = self.flat_gifs.index(gif_path)
        # 加载新 GIF
        self.load_gif(gif_path)
        # 显示新 GIF
        self.canvas.itemconfig(self.pet_image, image=self.frames[0])
        self.current_frame = 0
        # 调整窗口位置保持原位
        current_x = self.root.winfo_x()
        current_y = self.root.winfo_y()
        self.root.geometry(f"{self.width}x{self.height}+{current_x}+{current_y}")

    def on_press(self, event):
        """鼠标按下事件"""
        # 记录鼠标点击的起始位置
        self.start_x = event.x_root
        self.start_y = event.y_root

    def on_drag(self, event):
        if self.start_x and self.start_y:
            # 计算鼠标移动的距离
            dx = event.x_root - self.start_x
            dy = event.y_root - self.start_y

            # 移动整个窗口
            current_x = self.root.winfo_x()
            current_y = self.root.winfo_y()
            self.root.geometry(f"+{current_x + dx}+{current_y + dy}")

            # 更新起始位置
            self.start_x = event.x_root
            self.start_y = event.y_root

    def show_menu(self, event):
        """显示右键菜单"""
        self.menu.post(event.x_root, event.y_root)

    def animate_gif(self):
        """播放 GIF 动画"""
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.canvas.itemconfig(self.pet_image, image=self.frames[self.current_frame])
        self.root.after(self.delays[self.current_frame], self.animate_gif)


if __name__ == "__main__":
    # 替换为你的 GIF 文件路径列表
    # 数据结构
    role_actions = {
        "yellowDog": [
            {"name": "exercise", "path": r"D:\PythonProjects\fist\table_pet\pet\gif\dog_exercise.gif"},
            {"name": "eat", "path": r"D:\PythonProjects\fist\table_pet\pet\gif\dog_eat.gif"},
            {"name": "sleep", "path": r"D:\PythonProjects\fist\table_pet\pet\gif\dog_sleep.gif"}
        ],
        "whileDog": [
            {"name": "job", "path": r"D:\PythonProjects\fist\table_pet\pet\gif\white_dog_job.gif"},
            {"name": "happy", "path": r"D:\PythonProjects\fist\table_pet\pet\gif\white_dog_happy.gif"},
            {"name": "cry", "path": r"D:\PythonProjects\fist\table_pet\pet\gif\white_dog_cry.gif"},
            {"name": "fear", "path": r"D:\PythonProjects\fist\table_pet\pet\gif\white_dog_fear.gif"},
            {"name": "blow", "path": r"D:\PythonProjects\fist\table_pet\pet\gif\white_dog_blow.gif"},
            {"name": "love", "path": r"D:\PythonProjects\fist\table_pet\pet\gif\white_dog_love.gif"}
        ]
    }

    pet = DogPet(role_actions)
