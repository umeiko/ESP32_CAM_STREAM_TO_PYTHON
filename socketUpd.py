import socket
import threading
import pygame
import pygame.image
import pygame.display
import pygame.event
import io
import pygame.time
import queue
import time


HOST, PORT = "192.168.1.105", 1234

pygame.init()
clock = pygame.time.Clock()
Que = queue.Queue(25)
size = (500, 500)
display = pygame.display.set_mode(size)
imgbuffer = b""
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
thread_running = True
address = (HOST, PORT)
server_socket.bind(address)


def render(img_bytes):
    """渲染图像"""
    global display
    picture_stream = io.BytesIO(img_bytes)
    img = pygame.image.load(picture_stream, ".JPEG")
    if img.get_size() != size:
        display = pygame.display.set_mode(img.get_size())
    display.blit(img, (0,0))
    clock.tick()
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
        data, _ = server_socket.recvfrom(500*1024)#接受数据
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
    global Que, thread_running
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

if __name__ == "__main__":
    main()