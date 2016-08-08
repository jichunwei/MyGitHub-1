#include "video.h"
#include <fcntl.h>
#include "print.h"
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <linux/videodev2.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <errno.h>
#include <signal.h>

int sockfd;
int cameraFd;
char unsigned *devconfp;
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t  cond = PTHREAD_COND_INITIALIZER;

void sig_handler(int signo)
{
    if(SIGINT == signo){
        printf("SIGINT will be exist!\n");
        close(sockfd);
        exit(1);
    }
}

unsigned char   *temp;
ssize_t         length;
void get_frame(int cameraFd)
{
    typedef struct  videoBuffer{
        void *start;
        size_t length;
    }VideoBuffer;
    VideoBuffer *buffers;
    struct v4l2_buffer buf;
    buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    buf.memory = V4L2_MEMORY_MMAP;
    if(ioctl(cameraFd,VIDIOC_DQBUF,&buf) == -1){
        perror("dqbuf");
        exit(1);
    }
    length = buf.bytesused;
    temp = (unsigned char *)malloc(length);
    memset(temp,0,sizeof(temp));
    memcpy(temp,buffers[buf.index].start,length);

    buf.type =  V4L2_BUF_TYPE_VIDEO_CAPTURE;
    buf.memory = V4L2_MEMORY_MMAP;
    if(ioctl(cameraFd,VIDIOC_QBUF,&buf) == -1){
        perror("qbuf");
        exit(1);
    }
    exit(0);
}

int stop = 0;
void *th_fn1(void *arg)
{
    int cameraFd = (int)arg;
    enum v4l2_buf_type  type;
    type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    while(!stop){
        get_frame(cameraFd);
        devconfp = (unsigned char*)malloc(length);
        memset(devconfp,0,length);
        pthread_mutex_lock(&mutex);
        memcpy(devconfp,temp,length);
        pthread_mutex_unlock(&mutex);
        pthread_cond_broadcast(&cond);
        usleep(1500);
        free(temp);
    }
    if(ioctl(cameraFd,VIDIOC_STREAMOFF,&type) == -1){
        perror("streamoff");
        exit(1);
    }
    return (void*)0;
}

void send_msg(int fd)
{
    ssize_t size;
    char readbuffer[1024] = {'\0'};
    char writebuffer[1024] = {'\0'};
    if((size = read(fd,readbuffer,1024)) < 0){
        perror("read");
        exit(1);
    }
    char respbuffer[1024] = "HTTP/1.0.200 OK\r\nConnetctiion:close\r\nServer:Net-camera-1-0\r\nCache=Control:no-store,no-cache,muset-revalidate, pre-check=0;post-check=0,max-age=0\r\nPragma:no-cache\r\nContent-type: multipart/x-mixed-replace;boundarpy = www.briup.com\r\n\r\n";
    if(write(fd,respbuffer,strlen(respbuffer)) != size){
        perror("write");
        exit(1);
    }
    printf("read: %s\n",readbuffer);
    printf("size: %d\n",size);
    printf("%s\n",respbuffer);

    //判断是要张图片还是要连续的多张图片
    if(strstr(readbuffer,"snapshot"))//发送一张图片
    {
        sprintf(writebuffer,"--www.briup.com\nContent-type:image/jpeg\nContern-Length:%d\n\n",length+432);
        if(write(fd,writebuffer,strlen(writebuffer)) != size){
            printf("size: %d\n",size);
            perror("write");
            exit(1);
        }
        printf("writebuffer:%s",writebuffer);
        pthread_mutex_lock(&mutex);
        if(pthread_cond_wait(&cond,&mutex) != 0){
            perror("condwait");
            exit(1);
        }

        int file = open("mpge.pig",O_CREAT|O_RDWR|O_TRUNC,0777);
        if(file < 0){
            perror("open");
            exit(1);
        }
        print_picture(fd,devconfp,length);
        free(devconfp);
        pthread_mutex_unlock(&mutex);
    }else{
        while(1){
            memset(writebuffer,0,sizeof(writebuffer));
            sprintf(writebuffer,"--www.briup.com\nContent-type:image/jpeg\nContent-Length:%d\n\n",length+432);
            pthread_mutex_lock(&mutex);
            if(pthread_cond_wait(&cond,&mutex) != 0){
                perror("condwait");
                exit(1);
            }
            write(fd,writebuffer,strlen(writebuffer));
            print_picture(fd,devconfp,length);
            sleep(1);
            free(devconfp);
            pthread_mutex_unlock(&mutex);
        }
    }

}

void *th_fn2(void *arg)
{
    int fd = (int)arg;
    send_msg(fd);
    close(fd);
    exit(0);
}

void *service_fn(void *arg)
{
    int fd = (int)arg;
    pthread_t th1,th2;
    int err;
    pthread_attr_t          attr;
    pthread_attr_init(&attr);
    pthread_attr_setdetachstate(&attr,PTHREAD_CREATE_DETACHED);
    err = pthread_create(&th1,&attr,th_fn1,(void*)fd);
    if(err < 0){
        perror("pthread_create");
        exit(1);
    }
    err = pthread_create(&th2,&attr,th_fn2,(void*)fd);
    if(err < 0){
        perror("pthread_create");
        exit(1);
    }
    return (void*)0;
}

int main(int argc,char *argv[])
{

    if(argc != 3){
        fprintf(stderr,"-usage:%s devname\n",argv[0]);
        exit(1);
    }
    printf("***program begin***\n");
    get_dev(argv[1]);
    printf("devname:%s\n",argv[1]);
    if((cameraFd = open(argv[1],O_RDWR)) < 0){
        perror("open");
        exit(1);
    }
    printf("cameraFd:%d\n",cameraFd);
    get_capability(cameraFd);
    select_input(cameraFd);
    // get_stanard(cameraFd);
    set_frame(cameraFd);
    do_frame(cameraFd);

    sockfd = socket(AF_INET,SOCK_STREAM,0);
    if(sockfd < 0){
        perror("sockfd");
        exit(1);
    }
    if(signal(SIGINT,sig_handler) == SIG_ERR){
        perror("signal");
        exit(1);
    }
    int                     err;
    pthread_t               th;
    pthread_attr_t          attr;
    pthread_attr_init(&attr);
    pthread_attr_setdetachstate(&attr,PTHREAD_CREATE_DETACHED);

    struct sockaddr_in      saddr;
    memset(&saddr,0,sizeof(saddr));
    saddr.sin_family = AF_INET;
    saddr.sin_port = htons(atoi(argv[2]));
    saddr.sin_addr.s_addr = INADDR_ANY;
    if(bind(sockfd,(struct sockaddr *)&saddr,sizeof(saddr)) < 0){
        perror("bind");
        exit(1);
    }
    if(listen(sockfd,10) <0){
        perror("listen");
        exit(1);
    }
    if(signal(SIGINT,sig_handler) == SIG_ERR){
        perror("signal");
        exit(1);
    }
    while(1){
        int fd = accept(sockfd,NULL,NULL);
        if(fd < 0){
            perror("accept");
            exit(1);
        }else {
            err = pthread_create(&th,&attr,service_fn,(void*)fd);
            if(err != 0){
                fprintf(stderr,"usage:%s\n",strerror(err));
            }
        }
    }
    exit(1);
}
