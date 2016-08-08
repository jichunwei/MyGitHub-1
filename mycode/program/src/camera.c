#include <unistd.h>
#include <sys/types.h>
#include <fcntl.h>
#include <malloc.h>
#include <sys/stat.h>
#include <sys/mman.h>
#include <linux/videodev2.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

int main(int argc,char **argv)
{
    int             cameraFd;

    if(argc != 2){
        fprintf(stderr,"usgae:%s devname\n",argv[0]);
        exit(1);
    }
    struct stat  stat;
    char         *ptr;
    if(lstat(argv[1],&stat) < 0)
    {
        perror("lstat");
        exit(1);
    }
    if(S_ISCHR(stat.st_mode))
        ptr = "the file is character specail file:";
    else 
        ptr = "** errno mode **";
    printf("*** camera start ***\n");
    printf("%s\ndevname:%s\n",ptr,argv[1]);
    //1，打开视频设备。
    if((cameraFd = open(argv[1],O_RDWR)) < 0){
        perror("open");
        exit(1);
    }
    printf("cameraFd:%d\n",cameraFd);

    //查看设备的功能
    struct v4l2_capability cap;
  //  memset(&capab,0,sizeof(cap));
    char driver[16] = {'\0'};
    char card[32] = {'\0'};
    char bus_info[32] = {'\0'};
    int  version = 0;
    if(ioctl(cameraFd,VIDIOC_QUERYCAP,&cap) == -1){
        perror("querycap");
        exit(1);
    }
    strcpy(driver,cap.driver);
    strcpy(card,cap.card);
    strcpy(bus_info,cap.bus_info);
    version = cap.version;
    printf("name of dirver:%s\n",driver);
    printf("name of device: %s\n",card);
    printf("location of deviece :%s\n",bus_info);
    printf("name of version: %d\n",version);

    struct v4l2_input input;
    unsigned int        index = 0;
    char                name[32]= {"xuhongshabi"};
    unsigned int        Type = 0;
    unsigned int        audioset = 0;
    unsigned int        tuner = 0;

//    memset(&input,0,sizeof(input));
    if(ioctl(cameraFd,VIDIOC_ENUMSTD,&input) == -1){
        perror("input");
    }
    index = input.index;
    strcpy(name,input.name);
    Type = input.type;
    audioset = input.audioset;
    tuner = input.tuner;
    printf("index:%d\n",index);
    printf("name:%s\n",name);
    printf("type:%d\n",Type);
    printf("audioset:%d\n",audioset);
    printf("tuner:%d\n",tuner);
    //2.1检查当前视频设备的标准
    struct v4l2_standard std;
    v4l2_std_id  id;
    int ret;
    do{
        ret = ioctl(cameraFd,VIDIOC_QUERYSTD,&id);//检查当前视频设备支持的标准
    }while(ret == -1 && errno == EAGAIN);
    switch(id){
        case V4L2_STD_NTSC://欧洲使用标准
            printf("the normlal is V4L2_STD_NTSC!\n");
        case V4L2_STD_PAL://亚洲使用
            printf("the normalal is V4L2_STD_PAL\n");
        default:
            printf("can't find the normal!\n");
    }
    //2.2设置视频捕获格式
    struct v4l2_format fmt;
    memset(&fmt,0,sizeof(fmt));
    fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;//数据流类型
    fmt.fmt.pix.width = 720;
    fmt.fmt.pix.height = 576;
    fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_MJPEG;//视频数据存储类型(压缩格式)
    fmt.fmt.pix.field = V4L2_FIELD_ANY;
    if(ioctl(cameraFd,VIDIOC_S_FMT,&fmt) == -1){//设置当前驱动的捕获格式
        perror("fmt");
        exit(1);
    }

    //设置桢率(每秒钟传多少图i)
    struct v4l2_streamparm streamparm;
    if(ioctl(cameraFd,VIDIOC_S_PARM,&streamparm) == -1){
        perror("parm");
        exit(1);
    }

    //2.3向驱动申请桢缓冲
    struct v4l2_requestbuffers req;
    memset(&req,0,sizeof(req));
    req.count = 5;
    req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    req.memory = V4L2_MEMORY_MMAP;
    if(ioctl(cameraFd,VIDIOC_REQBUFS,&req) == -1){//分配内存
        perror("requbufs");
        exit(1);
    }
    //2.4获取并记录缓存的物理空间
    typedef struct videoBuffer{
        void    *start;
        size_t  length;
    }VideoBuffer;
    VideoBuffer* buffers = (VideoBuffer *)calloc(req.count,sizeof(*buffers));
    struct v4l2_buffer buf;
    int numBufs;
    for(numBufs = 0; numBufs < req.count; numBufs++){
        memset(&buf,0,sizeof(buf));
        buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf.memory = V4L2_MEMORY_MMAP;
        buf.index = numBufs;
        //读取缓存
        if(ioctl(cameraFd,VIDIOC_QUERYBUF,&buf) == -1){
            //把VIDIOC_REQBUFS中的数据缓存转换成物理地址
            perror("querybuf");
            exit(1);
        }
        buffers[numBufs].length = buf.length;
        //映射到用户空间
        buffers[numBufs].start = mmap(0, buf.length,
                PROT_READ|PROT_WRITE,MAP_SHARED,cameraFd,buf.m.offset); 
        if(buffers[numBufs].start == MAP_FAILED){
            perror("mmap");
            exit(1);
        }
    }
    //放入缓存队列
    if(ioctl(cameraFd,VIDIOC_QBUF,&buf) == -1){//把数据放入缓存队列
        perror("qbuf");
        exit(1);
    }
    //采集视频
    enum v4l2_buf_type type;
    type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    if(ioctl(cameraFd,VIDIOC_STREAMON,&type) < 0){
        perror("stramon");
        exit(1);
    }
    //读取缓存(出队)
    buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    char *a[] = {"1.pig","2.pig","3.pig","4.pig"};
    int  j;
    for(j = 0; j < req.count; j++){
    if(ioctl(cameraFd,VIDIOC_DQBUF,&buf) == -1){
        perror("dqbuf");
        exit(1);
    }
    buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    buf.memory = V4L2_MEMORY_MMAP;
    unsigned char *ptcur = buffers[buf.index].start;
    int pfd;
    if((pfd = open("1.pig",O_WRONLY|O_CREAT|O_TRUNC,0777)) < 0){
        perror("open");
        exit(1);
    }
    //打印
    print_picture(pfd,ptcur,buffers[buf.index].length);
    close(pfd);
    //重新放入缓存队列
    if(ioctl(cameraFd,VIDIOC_QBUF,&buf) == -1){
        perror("qbuf");
    }
    }
    //关闭采集流
   // buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    if(ioctl(cameraFd,VIDIOC_STREAMOFF,&buf) == -1)
    {
        perror("streamoff");
        exit(1);
    }
    int i = 0;
    for(; i < numBufs; i++){
        munmap(buffers[i].start,buffers[i].length);
    }
    close(cameraFd);
    return 0;
}
