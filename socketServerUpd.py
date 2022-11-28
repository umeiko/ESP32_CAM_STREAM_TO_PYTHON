import socketserver
import pygame
import pygame.image
import io
import pygame.time


pygame.init()
clock = pygame.time.Clock()
display = None
imgbuffer = b""


def render(img_bytes):
    """渲染图像"""
    global display
    picture_stream = io.BytesIO(img_bytes)
    img = pygame.image.load(picture_stream, ".JPEG")
    if display is None:
        display = pygame.display.set_mode(img.get_size())
    
    display.blit(img, (0,0))
    clock.tick()
    pygame.display.flip()
    pygame.display.set_caption(f"FPS: {clock.get_fps():.3}")
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()


class MyUDPHandler(socketserver.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """

    def handle(self):
        global imgbuffer

        data:bytes = self.request[0]
        socket = self.request[1]
        if data[-1]!=0xFF :#0xFF代表一张图片的数据发送结束
            imgbuffer += data[:-1]
        else:
            imgbuffer += data[:-1]
            try:
                render(imgbuffer)
            except Exception as e:
                print(e)
            imgbuffer = b""

    
if __name__ == "__main__":
    HOST, PORT = "192.168.1.105", 1234
    with socketserver.UDPServer((HOST, PORT), MyUDPHandler) as server:
        server.serve_forever()