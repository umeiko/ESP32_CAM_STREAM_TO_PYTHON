#include "WiFi.h"
#include "AsyncUDP.h"
#include "camera_pins.h"
#include "esp_camera.h"

//UDP传输大小有限制，因此一个包最大1400+1位引导位
#define max_packet_byte 1399
#define LED_PIN 4

const char * ssid = "218-2";
const char * password = "218520520";
IPAddress serverIP(192, 168, 1, 105); //欲访问的地址
uint16_t serverPort = 1234;              //服务器端口号

AsyncUDP udp;
String serial_input = "";
camera_fb_t *fb = NULL;



uint8_t onePacket[max_packet_byte+1];

void sendImgAray(uint8_t * img,uint16_t lenth,uint8_t index){
/*
*一张图片大概是3K~10K之间
*每个包数据大小为1024，增加一位索引位，告诉服务器我是第几个包
*索引位为0xff时代表是最后一个包，便于上位机处理
*/
  memset(onePacket,0x00,max_packet_byte+1);
  memcpy(onePacket,fb->buf,lenth);
  onePacket[lenth]=index;
  udp.write(onePacket, lenth+1);
}

void startCamera(){
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sscb_sda = SIOD_GPIO_NUM;
    config.pin_sscb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.frame_size = FRAMESIZE_VGA;
    config.pixel_format = PIXFORMAT_JPEG; 
    // config.pixel_format = PIXFORMAT_RGB565; // for face detection/recognition
    config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
    config.fb_location = CAMERA_FB_IN_PSRAM;
    config.jpeg_quality = 12;
    config.fb_count = 1;

    if(psramFound()){
        config.jpeg_quality = 32;
        config.fb_count = 2;
        config.frame_size = FRAMESIZE_VGA;
        config.grab_mode = CAMERA_GRAB_LATEST;
        Serial.println("psramFound!");
    } else {
        // Limit the frame size when PSRAM is not available
        config.frame_size = FRAMESIZE_QVGA;
        config.fb_location = CAMERA_FB_IN_DRAM;
    }

    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Camera init failed with error 0x%x", err);
        while (1){
            digitalWrite(LED_PIN, HIGH);
            delay(500);
            digitalWrite(LED_PIN, LOW);
            delay(2000);
        }
        return;
    }else{
        Serial.printf("\nCamera init success\n");
    }
}

void blink(int pin_num, int dark_time, int light_time){
    delay(dark_time);
    digitalWrite(pin_num, HIGH);
    delay(light_time);
    digitalWrite(pin_num, LOW);
}

void setup()
{
    Serial.begin(115200);
    pinMode(LED_PIN, OUTPUT);
    blink(LED_PIN, 0, 200);
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    if(WiFi.waitForConnectResult() != WL_CONNECTED){
        Serial.println("WiFi Failed");
        while (1){
            blink(LED_PIN, 200, 200);
        }
    }
    Serial.println("WiFi Connected");
    for(int i=0; i<2; i++){
        blink(LED_PIN, 200, 200);
    }
    startCamera();
    for(int i=0; i<3; i++){
        blink(LED_PIN, 100, 100);
    }
}

void loop()
{
    if(!udp.connected()){
        udp.connect(serverIP, serverPort);
        for(int i=0; i<1; i++){
            blink(LED_PIN, 200, 100);
        }
        delay(1000); 
    }else{
        // Serial.println("udp connected!");
        // 串口通讯测试
        // if(Serial.available()){
        //     serial_input = Serial.readStringUntil('\n');
        //     Serial.println(serial_input);
        //     udp.broadcastTo(serial_input.c_str(), 1234);
        // }
        delay(10);
        fb = esp_camera_fb_get();
        if(!fb){
            Serial.println("cam read fail!");
            blink(LED_PIN, 200, 1000);
        }else{
            uint8_t *P_temp = fb->buf;//暂存指针初始位置
            int pic_length = fb->len;//获取图片字节数量
            int pic_pack_quantity = pic_length / max_packet_byte;//将图片分包时可以分几个整包
            int remine_byte = pic_length % max_packet_byte;//余值,即最后一个包的大小
            //发送图片信息,这是按分包循环发送,每一次循环发送一个包
            for (int j = 0; j < pic_pack_quantity; j++) {
                sendImgAray(fb->buf, max_packet_byte, j); //将图片分包发送
                fb->buf+=max_packet_byte; //图片内存指针移动到相应位置
                delay(5);  //给上位机预留时间接收数据包
            }
            sendImgAray(fb->buf, remine_byte, 0xFF); //发送最后一个包，剩余的数据
            fb->buf = P_temp;         //将当时保存的指针重新返还最初位置
            esp_camera_fb_return(fb);
        }
    }
    
}
