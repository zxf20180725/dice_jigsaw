"""
    @File        : main.py
    @Author      : 狡猾的皮球
    @Date        : 2021/1/30 10:39
    @QQ          : 871245007
    @Description :
        模拟使用骰子🎲进行拼图，骰子默认大小为1cm*1cm*1cm
        操作方式：
            1.使用鼠标拖拽可以移动生成的骰子图片
            2.使用鼠标滚轮可以进行缩放
            3.按下键盘的s键可以保存缩放的图片到当前目录下，文件名为target.png
            4.修改image_path可以更换图片，注意：一定要黑白的图片（可以使用ps的去色功能），并且尺寸不要太大（建议长宽不要超过100像素）
"""

import sys

import pygame

from sprite import DrawAPI


class Game:
    def __init__(self, title, width, height, fps=60, image_path="./1.bmp"):
        """
        :param title: 游戏窗口的标题
        :param width: 游戏窗口的宽度
        :param height: 游戏窗口的高度
        :param fps: 游戏每秒刷新次数
        """
        self.title = title
        self.width = width
        self.height = height
        self.screen_surf: pygame.Surface = None
        self.fps = fps
        self.__init_pygame()
        self.__init_game(image_path)
        self.update()

    def __init_pygame(self):
        pygame.init()
        pygame.display.set_caption(self.title)
        self.screen_surf = pygame.display.set_mode([self.width, self.height])
        self.clock = pygame.time.Clock()
        self.offset_x = 0
        self.offset_y = 0
        # 鼠标是否按下
        self.pressed = False
        # 鼠标按下时的坐标
        self.px = 0
        self.py = 0
        # 鼠标按下时与面板的距离
        self.dx = 0
        self.dy = 0
        # 实时的缩放比例
        self.k = 1.0
        self.cell_x = 0
        self.cell_y = 0

    def __init_game(self, image_path):
        # 加载原图
        self.image: pygame.Surface = pygame.image.load(image_path)
        w = self.image.get_width()
        h = self.image.get_height()
        # 加载骰子图片
        self.dice_list = [pygame.image.load(f"./touzi/{i}.png").convert_alpha() for i in range(6)]
        # 读取灰度
        pixarr = pygame.PixelArray(self.image)
        shape = pixarr.shape
        # 创建Surface
        self.raw_target_surface = pygame.Surface(
            (w * 100 + 100, h * 100 + 100),
            flags=pygame.SRCALPHA
        )
        self.raw_target_surface.fill((30, 30, 30))
        # 画最终图片
        for y in range(shape[1]):
            for x in range(shape[0]):
                color = pixarr[x, y]
                b = color & 255
                g = (color >> 8) & 255
                r = (color >> 16) & 255
                num = int(b / 42.67)
                self.raw_target_surface.blit(self.dice_list[num], (100 + x * 100, 100 + y * 100))
        self.target_surface = self.raw_target_surface
        self.w = w
        self.h = h
        self.font = pygame.font.SysFont("fangsong", 28)
        self.rel_size = 0.01  # 10号骰子 1cm
        # 标号
        for i in range(1, self.w + 1):
            DrawAPI.draw_text(self.raw_target_surface, 100 + 100 * i - 50, 50, str(i), self.font, (255, 255, 255))

        for i in range(1, self.h + 1):
            DrawAPI.draw_text(self.raw_target_surface, 50, 100 + 100 * i - 50, str(i), self.font, (255, 255, 255))

    def update(self):
        while True:
            self.clock.tick(self.fps)
            # TODO:逻辑更新
            self.event_handler()
            # TODO:画面更新
            self.render()

    def render(self):
        self.screen_surf.fill((150, 150, 150))
        self.screen_surf.blit(self.target_surface, (self.offset_x + 100, self.offset_y + 100))
        # DrawAPI.draw_fill_rect(self.target_surface, self.cell_x * 100 * self.k, self.cell_y * 100 * self.k,
        #                        self.target_surface.get_width(), 100 * self.k, (0, 255, 0, 200))
        self.screen_surf.blit(self.image, (10, 10))
        for i in range(6):
            self.screen_surf.blit(self.dice_list[i], (100 + 100 * i, 0))
        DrawAPI.draw_src_text(self.screen_surf, 30, 150, f"宽：{self.w}个骰子", self.font, (20, 255, 20))
        DrawAPI.draw_src_text(self.screen_surf, 30, 200, f"高：{self.h}个骰子", self.font, (20, 255, 20))
        DrawAPI.draw_src_text(self.screen_surf, 30, 250, f"一共需要：{self.w * self.h}个骰子", self.font, (0, 255, 0))

        DrawAPI.draw_src_text(self.screen_surf, 30, 300, f"真实宽：{self.w * self.rel_size}米", self.font, (255, 255, 0))
        DrawAPI.draw_src_text(self.screen_surf, 30, 350, f"真实高：{self.h * self.rel_size}米", self.font, (255, 255, 0))
        DrawAPI.draw_src_text(self.screen_surf, 30, 400, f"面积：{(self.w * self.rel_size) * (self.h * self.rel_size)}平方米",
                              self.font, (255, 255, 0))
        DrawAPI.draw_src_text(self.screen_surf, 30, 450, f"预计耗时：{(self.w * self.h) * 8 / 60}分钟",
                              self.font, (255, 255, 0))

        DrawAPI.draw_src_text(self.screen_surf, 30, 500, f"作者：狡猾的皮球",
                              self.font, (255, 0, 0))
        pygame.display.update()

    def mouse_move(self, x, y):
        if self.pressed:
            # 拖动窗口
            self.offset_x = x - self.dx
            self.offset_y = y - self.dy
        self.k = self.target_surface.get_width() / self.raw_target_surface.get_width()
        mx = x - self.offset_x - 100
        my = y - self.offset_y - 100
        # cell_x = int(mx / (self.k * 100))
        # cell_y = int(my / (self.k * 100))

    def mouse_up(self, x, y):
        self.pressed = False

    def mouse_down(self, x, y, pressed):
        self.pressed = True
        self.dx = x - self.offset_x
        self.dy = y - self.offset_y

    def event_handler(self):
        x, y = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.offset_x -= 10
                elif event.key == pygame.K_RIGHT:
                    self.offset_x += 10
                elif event.key == pygame.K_UP:
                    self.offset_y -= 10
                elif event.key == pygame.K_DOWN:
                    self.offset_y += 10
                elif event.key == pygame.K_s:
                    # 保存图片
                    pygame.image.save(self.target_surface, "./target.png")
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_move(x, y)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pressed = pygame.mouse.get_pressed()
                self.mouse_down(x, y, pressed)
                if event.button == 4:
                    self.target_surface = pygame.transform.smoothscale(
                        self.raw_target_surface,
                        (
                            int(self.target_surface.get_width() * 1.05),
                            int(self.target_surface.get_height() * 1.05)
                        )
                    )
                elif event.button == 5:
                    self.target_surface = pygame.transform.smoothscale(
                        self.raw_target_surface,
                        (
                            int(self.target_surface.get_width() * 0.95),
                            int(self.target_surface.get_height() * 0.95)
                        )
                    )
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_up(x, y)


if __name__ == '__main__':
    Game("骰子拼图仿真-狡猾的皮球", 800, 600, fps=30, image_path="./1.bmp")
