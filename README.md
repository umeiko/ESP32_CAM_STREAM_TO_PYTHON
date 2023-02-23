# ESP32_CAM_STREAM_TO_PYTHON
ESP32_CAM模块，利用UPD协议实时传输图像到python客户端，基于Arduino实现


![image](https://user-images.githubusercontent.com/58870893/204182474-693a78bd-fac9-484c-955e-9de03c7a891d.png)

## 项目特性
- 利用`Pygame`实现接收端界面，代码简洁，第三方库依赖少
- 提供了两种UPD服务的连接方案
- 基于多线程，失去连接时界面不会卡死
- 注释丰富，适合学习
- 提供了将ESP32-CAM图像传输到Python中的方案，适合二次开发

## 用法
查看窗口中的ip地址
- ![image](https://user-images.githubusercontent.com/58870893/218300911-6b291afc-5d9e-4e0c-9886-52260afabd21.png)

通过串口发送ip地址
- ![image](https://user-images.githubusercontent.com/58870893/218300957-3239f88c-7691-4427-b41a-bf06423cd805.png)

成功连接到图像
- ![image](https://user-images.githubusercontent.com/58870893/218301010-224bd39e-3038-49dc-bb3c-2ce036b4625d.png)



## 鸣谢
感谢[博主](https://gitlab.ifengyu.com/tianshuaikang/espcam2pc)提供的技术思路
