import io
import queue
import socket
import threading
import time

import pygame
import pygame.display
import pygame.event
import pygame.image
import pygame.time

HOST, PORT = socket.gethostbyname(socket.gethostname()), 1234
# HOST, PORT = "192.168.1.116", 1234

RECT    = None
RECT_DRAWING = False


pygame.init()
clock = pygame.time.Clock()
Que = queue.Queue(25)
size = (500, 500)
display = pygame.display.set_mode(size)
imgbuffer = b""
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)


thread_running = True
address = (HOST, PORT)
server_socket.bind(address)


def render(img_bytes):
    """渲染图像"""
    global display, size
    picture_stream = io.BytesIO(img_bytes)
    img = pygame.image.load(picture_stream, ".JPEG")
    if img.get_size() != size:
        size = img.get_size()
        display = pygame.display.set_mode(size)
    display.blit(img, (0,0))
    clock.tick()
    if RECT is not None:
        pygame.draw.rect(display, "red", RECT, 10)
    pygame.display.flip()
    pygame.display.set_caption(f"FPS: {clock.get_fps():.3}")

def no_signal():
    display.fill((50,50,128))
    clock.tick(10)
    pygame.display.flip()
    pygame.display.set_caption(f"No Signal, Listening On {HOST}:{PORT}")

def upd_handler():
    """处理Upd连接"""
    global imgbuffer, Que, thread_running
    while thread_running:
        data, _ = server_socket.recvfrom(500*1024, )#接受数据
        if data[-1]!=0xFF:#0xFF代表一张图片的数据发送结束
            imgbuffer += data[:-1]
        else:
            imgbuffer += data[:-1]
        
            if not Que.full():
                Que.put_nowait(imgbuffer)
            imgbuffer = b""

def stop_block():
    """启用客户端连接连接upd,中断监听阻塞"""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        client_socket.connect((HOST, PORT))
        client_socket.send(b"q")
        client_socket.close()
    except Exception as e:
        print('except at run client: ', e)


def main():
    global Que, thread_running, RECT, RECT_DRAWING
    upd_task = threading.Thread(target=upd_handler)
    upd_task.start()
    time_cnt = time.time()
    while True:
        if not Que.empty():
            frame_bytes = Que.get()
            time_cnt = time.time()
            try:
                render(frame_bytes)
            except Exception as e:
                print(e)
        else:
            if time.time() - time_cnt > 1.:
                no_signal()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                thread_running = False
                stop_block()
                upd_task.join()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                RECT_DRAWING = True
                RECT = [event.pos[0], event.pos[1], 0, 0]
            elif event.type == pygame.MOUSEMOTION:
                if RECT_DRAWING:
                    w = RECT[0] - event.pos[0]
                    h = RECT[1] - event.pos[1]
                    RECT[0] = event.pos[0] if w > 0 else RECT[0]
                    RECT[1] = event.pos[1] if h > 0 else RECT[1]
                    RECT = [RECT[0], RECT[1], abs(w), abs(h)]
            elif event.type == pygame.MOUSEBUTTONUP:
                RECT_DRAWING = False


if __name__ == "__main__":
    main()