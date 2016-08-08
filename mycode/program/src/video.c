#include <unistd.h>
#include <assert.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <linux/videodev2.h>

int fd;
//判断是否是字符设备
void  *get_dev(char *arg)
{
    struct stat stat;
    char *ptr;
    if(lstat(arg,&stat) < 0){
        perror("lstat");
        exit(1);
    }
    if(S_ISCHR(stat.st_mode)){
        ptr = "the file is chracter sepecail file";
    printf("%s\n",ptr);
    }else{
        printf("** error mode **\n");
    }
}

//打开设备
void open_dev(char *arg, int camraFd)
{
   // int     camraFd;
    
    camraFd = open(arg,O_RDWR);
    if(camraFd < 0){
        perror("open");
        exit(1);
    }
    printf("camraFd:%d\n",camraFd);
}

//查看驱动功能
void get_capability(int fd)
{
    struct v4l2_capability cap;
    memset(&cap,0,sizeof(cap));
    char driver[16] = {'\0'};
    char card[32] = {'\0'};
    char bus_info[32] = {'\0'};
    unsigned int version = 0;

    if(ioctl(fd,VIDIOC_QUERYCAP,&cap) < 0){
        perror("querycap");
        exit(1);
    }
    strcpy(driver,cap.driver);
    strcpy(card,cap.card);
    strcpy(bus_info,cap.bus_info);
    version = cap.version;
    printf("name of driver %s\n",driver);
    printf("name of deviece %s\n",card);
    printf("location of deviece %s\n",bus_info);
    printf("version :%d\n",version);
}

//选择输入
void select_input(int fd)
{
    struct v4l2_input input;
    unsigned int index = 0;

    if(ioctl(fd,VIDIOC_G_INPUT,&index) < 0){
        perror("VIDIOC_G_INPUT");
        exit(1);
    }
    memset(&input,0,sizeof(input));
    if(ioctl(fd,VIDIOC_ENUMINPUT,&input) < 0){
        perror("VIDIOC_ENUMINPUT");
        exit(1);
    }
    printf("current input:%s\n",input.name);

}
/*
void select_input(int fd)
{
    struct v4l2_input input;
    unsigned int index = 0;
    if(-1 == ioctl(fd,VIDIOC_S_INPUT,&index)){
        perror("VIDIOC_S_INPUT");
        exit(1);
    }
    printf("current input: %s\n",input.name);
}
*/
//查看标准制士
void get_standard(int fd)
{
    struct v4l2_standard std;
    v4l2_std_id     id;
/*    if(ioctl(fd,VIDIOC_G_STD,&id) < 0){
        perror("VIDIOC_G_STD");
        exit(1);
    }
    memset(&std,0,sizeof(std));
    std.index = 0;
    while(ioctl(fd,VIDIOC_ENUMSTD,&std) == 0){
        if(std.id & id){
            printf("current video standard:%s\n",std.name);
            exit(0);
        }
        std.index++;
    }
    if(errno = EINVAL || std.index == 0){
        perror("VIDIOC_ENUMSTD");
        exit(1);
    }
    */
    int ret;
    do{
        ret = ioctl(fd,VIDIOC_QUERYSTD,&id);
    }while(ret == -1 && errno == EAGAIN);
    switch(id){
        case V4L2_STD_NTSC:
            printf("current standard is V4L2_STD_NTSC\n");
            break;
        case V4L2_STD_PAL:
            printf("current standard is V4L2_STD_PAL\n");
            break;
        default:
            printf("can't find current standard\n");
    }
}

//设置贞格式
void set_frame(int fd)
{
    struct v4l2_format fmt;
    memset(&fmt,0,sizeof(fmt));
    fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    fmt.fmt.pix.width = 720;
    fmt.fmt.pix.height = 540;
    fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_MJPEG;
    fmt.fmt.pix.field = V4L2_FIELD_ANY;
    if(-1 == ioctl(fd,VIDIOC_S_FMT,&fmt)){
        perror("VIDIOC_S_FMT");
        exit(1);
    }
}


void do_frame(int fd)
{
//向驱动申请空间
    struct v4l2_requestbuffers req;
    memset(&req,0,sizeof(req));
    req.count = 5;
    req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    req.memory = V4L2_MEMORY_MMAP;
    if(ioctl(fd,VIDIOC_REQBUFS,&req) < 0){
        perror("VIDIOC_REQBUFS");
        exit(1);
    }
//获取贞缓冲的物理空间。
    typedef struct videoBuffer{
        void *start;
        size_t length;
    }VideoBuffer;
    VideoBuffer  *buffers = (VideoBuffer*)calloc(req.count,sizeof(buffers));
    assert(buffers != NULL);
    struct v4l2_buffer  buf;
    int i;
    for(i = 0; i < req.count;i++){
        memset(&buf,0,sizeof(buf));
        buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf.memory = V4L2_MEMORY_MMAP;
        buf.index = i;
        //读缓存
        if(ioctl(fd,VIDIOC_QUERYBUF,&buf) == -1){
            perror("QUERYBUF");
            exit(1);
        }
        //映射用户空间
        buffers[i].length = buf.length;
        buffers[i].start = mmap(NULL,buf.length,PROT_READ|PROT_WRITE,MAP_SHARED,fd,buf.m.offset);
        if(buffers[i].start ==  MAP_FAILED){
            perror("mmap");
            exit(1);
        }
    }
    //放入缓存队列
    if(ioctl(fd,VIDIOC_QBUF,&buf) < 0){
        perror("VIDIOC_QBUF");
        exit(1);
    }
    //采集视频
    enum v4l2_buf_type type;
    type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    if(ioctl(fd,VIDIOC_STREAMON,&type) < 0){
        perror("VIDIOC_STREAON");
        exit(1);
    }
    //出队
    buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    if(ioctl(fd,VIDIOC_DQBUF,&buf) < 0){
        perror("VIDIOC_DQBUF");
    exit(1);
    }
    //dayin
    buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    buf.memory = V4L2_MEMORY_MMAP;
    unsigned char *p = buffers[buf.index].start;
    int pfd;
    pfd = open("mpeg.pig",O_WRONLY|O_CREAT|O_TRUNC,0777);
    if(pfd < 0){
        perror("open");
        exit(1);
    }
    print_picture(pfd,p,buffers[buf.index].length);
    close(pfd);
    //重新入队
    if(ioctl(fd,VIDIOC_QBUF,&buf) < 0){
        perror("VIDIOC_QBUF");
        exit(1);
    }
  /*  //关闭流
    if(ioctl(fd,VIDIOC_STREAMOFF,&buf) < 0){
        perror("VIDIOC_STREAMOFF");
        exit(1);
    }
    */
    int j = 0;
    for(; j < req.count; j++){
        munmap(buffers[j].start,buffers[j].length);
    }
    close(fd);
    exit(0);
}




