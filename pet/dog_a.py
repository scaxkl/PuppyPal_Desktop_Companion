import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import os
import sys
import winreg
import ctypes
import platform


class DogPet:
    def __init__(self, role_actions):
        self.role_actions = role_actions
        self.flat_gifs = [
            action["path"]
            for role in self.role_actions.values()
            for action in role
        ]
        #
        self.heal_interval = 5000
        self.heal_timer = None
        self.is_full_hunger = False
        # 初始化主窗口
        self.root = tk.Tk()
        self.root.overrideredirect(True)  # 隐藏窗口边框
        self.root.attributes('-topmost', True)  # 窗口置顶
        self.transparent_color = 'gray15'  # 不要使用白色
        self.root.attributes('-transparentcolor', self.transparent_color)  # 设置gray15为透明色

        # 检查并设置开机自启动
        self.check_auto_start()

        # 创建菜单系统
        self.menu = tk.Menu(self.root, tearoff=0)
        self._build_menu()  # 分离菜单构建逻辑

        # 加载第一个GIF（使用展平列表的第一个元素）
        self.current_gif_index = 0
        self.load_gif(self.flat_gifs[self.current_gif_index])

        # GIF 文件列表
        self.current_gif_index = 0

        # 加载初始 GIF
        self.role_actions = role_actions
        self.flat_gifs = [
            action["path"]
            for role in role_actions.values()
            for action in role
        ]
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

        # 饥饿值
        self.max_hunger = 10
        self.hunger = self.max_hunger
        self.hunger_indicator = self.canvas.create_text(35, 50, anchor="nw", text='🍖' * self.hunger, fill='yellow')

        # 血条
        self.max_health = 10
        self.health = self.max_health
        self.health_indicator = self.canvas.create_text(35, 35, anchor="nw", text='❤' * self.health, fill='red')

        # 绑定事件
        # self.canvas.bind("<ButtonPress-1>", self.on_press)  # 左键点击拖动
        self.canvas.bind("<B1-Motion>", self.on_drag)  # 左键拖动
        self.canvas.bind("<Button-3>", self.show_menu)  # 右键菜单

        # 启动动画(定时器）
        self.update_hunger()
        self.update_health()
        self.animate_gif()
        self.root.mainloop()

    def check_auto_start(self):
        """检查并设置开机自启动"""
        try:
            # 获取当前脚本路径
            script_path = sys.argv[0]
            # 如果是打包后的exe文件，使用sys.executable
            if getattr(sys, 'frozen', False):
                script_path = sys.executable

            # 自启动注册表项名称
            key_name = "DesktopPet"

            # 检查是否已经设置自启动
            if not self.is_auto_start_enabled(key_name):
                # 询问用户是否设置开机自启动
                result = self.ask_user_auto_start()
                if result:
                    self.set_auto_start(key_name, script_path)
        except Exception as e:
            print(f"设置开机自启动时出错: {e}")

    def is_admin(self):
        """检查程序是否以管理员权限运行"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def ask_user_auto_start(self):
        """询问用户是否设置开机自启动"""
        # 创建一个简单的对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("开机自启动")
        dialog.geometry("2500x1500")
        dialog.transient(self.root)
        dialog.grab_set()

        # 确保对话框在最前面
        dialog.attributes('-topmost', True)

        # 居中显示
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))

        # 显示消息
        message = tk.Label(
            dialog,
            text="是否设置桌面宠物开机自启动？",
            wraplength=200,
            padx=20,
            pady=20
        )
        message.pack(fill=tk.BOTH, expand=True)

        # 创建按钮框架
        button_frame = tk.Frame(dialog)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=10)

        # 是按钮
        yes_button = tk.Button(
            button_frame,
            text="是",
            command=lambda: dialog.quit()
        )
        yes_button.pack(side=tk.RIGHT, padx=(5, 0))

        # 否按钮
        no_button = tk.Button(
            button_frame,
            text="否",
            command=lambda: [dialog.quit(), setattr(dialog, 'result', False)]
        )
        no_button.pack(side=tk.RIGHT)

        # 设置默认结果为True
        dialog.result = True

        # 运行对话框
        dialog.mainloop()

        # 销毁对话框
        dialog.destroy()

        # 返回用户选择
        return dialog.result

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

    # 菜单生成
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
        # 新增喂食菜单项
        self.menu.add_separator()
        self.menu.add_command(
            label="🦴 喂食",
            command=self.feed_pet,
            accelerator="Ctrl+F")
        # 添加自启动设置菜单项
        self.menu.add_separator()
        # 添加退出项
        self.menu.add_separator()
        self.menu.add_command(label="Exit", command=self.root.destroy)

    def toggle_auto_start(self):
        """切换开机自启动状态"""
        key_name = "DesktopPet"
        script_path = sys.argv[0]
        if getattr(sys, 'frozen', False):
            script_path = sys.executable

        if self.is_auto_start_enabled(key_name):
            # 禁用自启动
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                     r"Software\Microsoft\Windows\CurrentVersion\Run",
                                     0, winreg.KEY_SET_VALUE)
                winreg.DeleteValue(key, key_name)
                winreg.CloseKey(key)
                print("已禁用开机自启动")
            except Exception as e:
                print(f"禁用开机自启动失败: {e}")
        else:
            # 启用自启动
            self.set_auto_start(key_name, script_path)

    def switch_gif_by_path(self, gif_path):
        """切换 GIF 动画"""
        try:  # 更新当前索引
            self.current_gif_index = self.flat_gifs.index(gif_path)
            # 加载新 GIF
            self.load_gif(gif_path)
            # 显示新 GIF
            self.canvas.itemconfig(self.pet_image, image=self.frames[0])
            self.current_frame = 0
        except ValueError:
            print(f"未找到 GIF 文件：{gif_path}")
        # 调整窗口位置保持原位
        current_x = self.root.winfo_x()
        current_y = self.root.winfo_y()
        self.root.geometry(f"{self.width}x{self.height}+{current_x}+{current_y}")

    def on_press(self, event):
        """鼠标按下事件"""
        # 记录鼠标点击的起始位置
        self.start_x = event.x
        self.start_y = event.y

    def on_drag(self, event):
        if self.start_x and self.start_y:
            # 计算鼠标移动的距离
            dx = event.x - self.start_x
            dy = event.y - self.start_y

            # 移动整个窗口
            current_x = self.root.winfo_x()
            current_y = self.root.winfo_y()
            self.root.geometry(f"+{current_x + dx}+{current_y + dy}")

            # 更新起始位置
            self.start_x = event.x
            self.start_y = event.y

    def show_menu(self, event):
        """显示右键菜单"""
        self.menu.post(event.x_root, event.y_root)

    def animate_gif(self):
        """播放 GIF 动画"""
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.canvas.itemconfig(self.pet_image, image=self.frames[self.current_frame])
        self.root.after(self.delays[self.current_frame], self.animate_gif)

    def update_health(self):
        """更新血量并更新UI"""
        if self.hunger <= 0 and self.health > 0:
            self.health -= 1
            self.canvas.itemconfig(self.health_indicator, anchor="nw", text='♥' * self.health)
            if self.health <= 0:
                self.health = 0
                self.handle_death()  # 分离死亡逻辑
        self.root.after(5000, self.update_health)

    def handle_death(self):
        """处理死亡逻辑"""
        # 1.切换到死亡状态的GIF（需提前在role_actions中定义"dead"）
        self.change_state("dead")
        # 2. 等待死亡动画播放完毕（假设动画总时长1秒，或固定等待1秒）
        #    使用after()代替time.sleep()，避免阻塞
        self.root.after(3000, self.destroy_app)
        # 切换状态

    def destroy_app(self):
        """销毁窗口"""
        self.root.destroy()

    def feed_pet(self):
        """喂食逻辑"""
        self.hunger = self.max_hunger
        self.canvas.itemconfig(
            self.hunger_indicator,
            text='🍖' * self.hunger,
            fill='yellow'
        )
        self.change_state("eat")
        self.is_full_hunger = False  # 强制触发状态变化检测
        self.update_hunger()  # 立即执行一次饥饿值逻辑（含回血判断）
        print("已喂食，饥饿值回满！")

    def update_hunger(self):
        """每10秒减少1点饥饿值，并更新UI"""
        # 检查是否需要停止回血
        if self.hunger < self.max_hunger and self.is_full_hunger:
            self.is_full_hunger = False
            self.cancel_healing()

        if self.hunger > 0:
            self.hunger -= 1
            self.canvas.itemconfig(self.hunger_indicator, text='🍖' * self.hunger)
            if self.hunger < 3:
                self.change_state("hungry")

            # 检查是否需要开始回血
            if self.hunger == self.max_hunger and not self.is_full_hunger:
                self.is_full_hunger = True
                self.start_healing()

        self.root.after(60000, self.update_hunger)

    def start_healing(self):
        """启动5秒间隔回血（满饥饿时触发）"""
        if self.health < self.max_health:
            self.health += 1
            self.canvas.itemconfig(
                self.health_indicator,
                anchor="nw",
                text='♥' * self.health,
                fill='pink' if self.health > 5 else 'red'
            )
            print(f"血量恢复：{self.health}/{self.max_health}")
            # 回血满切换状态
            if self.health == self.max_health:
                self.change_state("happy")
                self.cancel_healing()
                return  # 已经恢复到最大血量，不需要再恢复

        self.heal_timer = self.root.after(self.heal_interval, self.start_healing)
        print(f"定时器创建：{self.heal_timer}")

    def cancel_healing(self):
        """安全停止回血定时器"""
        if self.heal_timer:
            self.root.after_cancel(self.heal_timer)
            self.heal_timer = None

    # 切换状态
    def change_state(self, state):
        if state == "dead":
            self.load_gif(r".\gif\white_dog_bigcry_1.gif")
        elif state == "hungry":
            self.load_gif(r".\gif\white_dog_cry.gif")
        elif state == "eat":
            self.load_gif(r".\gif\white_dog_eat.gif")
        elif state == "happy":
            # 确保有happy状态的GIF，如果没有则使用默认
            for role in self.role_actions.values():
                for action in role:
                    if action["name"] == "happy":
                        self.load_gif(action["path"])
                        return
            # 如果没有找到happy状态的GIF，使用第一个GIF
            if self.flat_gifs:
                self.load_gif(self.flat_gifs[0])


if __name__ == "__main__":
    # 数据结构
    role_actions = {

        "whileDog": [
            {"name": "happy", "path": r".\gif\white_dog_happy.gif"},
            {"name": "job", "path": r".\gif\white_dog_job.gif"},
            {"name": "cry", "path": r".\gif\white_dog_cry.gif"},
            {"name": "fear", "path": r".\gif\white_dog_fear.gif"},
            {"name": "blow", "path": r".\gif\white_dog_blow.gif"},
            {"name": "love", "path": r".\gif\white_dog_love.gif"},
        ],
        "yellowDog": [
            {"name": "exercise", "path": r".\gif\dog_exercise.gif"},
            {"name": "eat", "path": r".\gif\white_dog_eat.gif"},
            {"name": "sleep", "path": r".\gif\dog_sleep.gif"},
            {"name": "like", "path": r".\gif\dog_like.gif"},
        ]
    }
    pet = DogPet(role_actions)