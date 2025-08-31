import tkinter as tk
from typing import Dict, List
from PIL import Image, ImageTk, ImageSequence


class DogPet:
    def __init__(self, role_actions: Dict[str, List[dict]]):
        # 初始化属性
        self.role_actions = role_actions
        self.flat_gifs = self._flatten_gifs()
        self.current_gif_index = 0
        self.dragging = False
        self.start_x = 0
        self.start_y = 0

        # 状态属性
        self.max_hunger = 10
        self.hunger = self.max_hunger
        self.max_health = 10
        self.health = self.max_health
        self.is_full_hunger = False

        # 初始化UI组件
        self.root = self._create_root_window()
        self.menu = self._create_context_menu()
        self.canvas, self.indicators = self._create_canvas()

        # 加载初始GIF
        self.load_gif(self.flat_gifs[self.current_gif_index])

        # 设置定时任务
        self._setup_timers()
        self.root.mainloop()

    def _flatten_gifs(self) -> List[str]:
        """将角色动作展平为GIF路径列表"""
        return [action["path"] for role in self.role_actions.values() for action in role]

    def _create_root_window(self) -> tk.Tk:
        """创建主窗口"""
        root = tk.Tk()
        root.overrideredirect(True)
        root.attributes('-topmost', True)
        root.attributes('-transparentcolor', 'gray15')
        return root

    def _create_context_menu(self) -> tk.Menu:
        """创建右键上下文菜单"""
        menu = tk.Menu(self.root, tearoff=0)

        # 添加角色子菜单
        for role_name, actions in self.role_actions.items():
            role_menu = tk.Menu(menu, tearoff=0)
            for action in actions:
                role_menu.add_command(
                    label=action["name"],
                    command=lambda p=action["path"]: self.switch_gif(p)
                )
            menu.add_cascade(label=role_name, menu=role_menu)

        # 添加功能菜单项
        menu.add_separator()
        menu.add_command(label="🦴 喂食", command=self.feed_pet)
        menu.add_command(label="❌ 退出", command=self.root.destroy)

        return menu

    def _create_canvas(self) -> tuple[tk.Canvas, dict]:
        """创建画布和状态指示器"""
        canvas = tk.Canvas(
            self.root,
            width=100,  # 初始占位尺寸，加载GIF后会更新
            height=100,
            bg='gray15',
            highlightthickness=0
        )

        # 状态指示器
        indicators = {
            'health': canvas.create_text(35, 35, anchor="nw", text='❤' * 10, fill='red'),
            'hunger': canvas.create_text(35, 50, anchor="nw", text='🍖' * 10, fill='yellow')
        }

        # 事件绑定
        canvas.bind("<ButtonPress-1>", self._start_drag)
        canvas.bind("<B1-Motion>", self._on_drag)
        canvas.bind("<Button-3>", self._show_context_menu)

        canvas.pack()
        return canvas, indicators

    def _setup_timers(self):
        """初始化所有定时任务"""
        self.animate_gif()
        self.root.after(5000, self._update_health)
        self.root.after(10000, self._update_hunger)

    def load_gif(self, gif_path: str):
        """加载并解析GIF文件"""
        try:
            gif = Image.open(gif_path)
            self.frames = [
                ImageTk.PhotoImage(frame.convert('RGBA'))
                for frame in ImageSequence.Iterator(gif)
            ]
            self.delays = [
                frame.info.get('duration', 100)
                for frame in ImageSequence.Iterator(gif)
            ]

            # 更新窗口尺寸
            self._update_window_size()

        except Exception as e:
            print(f"加载GIF失败: {str(e)}")
            self.root.destroy()

    def _update_window_size(self):
        """根据当前帧更新窗口尺寸"""
        new_width = self.frames[0].width()
        new_height = self.frames[0].height()
        self.canvas.config(width=new_width, height=new_height)
        self.root.geometry(f"{new_width}x{new_height}")

    def switch_gif(self, gif_path: str):
        """切换显示的GIF动画"""
        try:
            self.current_gif_index = self.flat_gifs.index(gif_path)
            self.load_gif(gif_path)
            self.current_frame = 0
            self.canvas.itemconfig(self.pet_image, image=self.frames[0])
        except ValueError:
            print(f"未找到指定的GIF路径: {gif_path}")

    def animate_gif(self):
        """播放GIF动画"""
        if hasattr(self, 'frames'):
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.canvas.itemconfig(self.pet_image, image=self.frames[self.current_frame])
            self.root.after(self.delays[self.current_frame], self.animate_gif)

    def _update_health(self):
        """更新健康状态"""
        if self.hunger <= 0 and self.health > 0:
            self.health -= 1
            self.canvas.itemconfig(
                self.indicators['health'],
                text='❤' * self.health
            )

            if self.health <= 0:
                self._handle_death()
                return

        self.root.after(5000, self._update_health)

    def _update_hunger(self):
        """更新饥饿状态"""
        if self.hunger > 0:
            self.hunger -= 1
            self.canvas.itemconfig(
                self.indicators['hunger'],
                text='🍖' * self.hunger
            )

            if self.hunger < 3:
                self.change_state("hungry")

        self.root.after(10000, self._update_hunger)

    def feed_pet(self):
        """喂食操作"""
        self.hunger = self.max_hunger
        self.canvas.itemconfig(
            self.indicators['hunger'],
            text='🍖' * self.hunger
        )
        self.change_state("eat")
        print("宠物已喂食！")

    def change_state(self, state_name: str):
        """根据状态名称切换动画"""
        for role in self.role_actions.values():
            for action in role:
                if action["name"] == state_name:
                    self.switch_gif(action["path"])
                    return
        print(f"未找到状态: {state_name}")

    def _handle_death(self):
        """处理死亡状态"""
        self.change_state("dead")
        self.root.after(3000, self.root.destroy)

    def _start_drag(self, event):
        """开始拖动窗口"""
        self.start_x = event.x
        self.start_y = event.y
        self.dragging = True

    def _on_drag(self, event):
        """处理拖动事件"""
        if self.dragging:
            dx = event.x - self.start_x
            dy = event.y - self.start_y
            x = self.root.winfo_x() + dx
            y = self.root.winfo_y() + dy
            self.root.geometry(f"+{x}+{y}")

    def _show_context_menu(self, event):
        """显示右键菜单"""
        self.menu.post(event.x_root, event.y_root)


if __name__ == "__main__":
    role_config = {
        "whileDog": [
            {"name": "happy", "path": "gifs/white_dog_happy.gif"},
            {"name": "job", "path": "gifs/white_dog_job.gif"},
            {"name": "dead", "path": "gifs/white_dog_bigcry_1.gif"},
            {"name": "hungry", "path": "gifs/white_dog_cry.gif"},
        ],
        "yellowDog": [
            {"name": "eat", "path": "gifs/white_dog_eat.gif"},
            {"name": "sleep", "path": "gifs/dog_sleep.gif"},
        ]
    }

    DogPet(role_config)