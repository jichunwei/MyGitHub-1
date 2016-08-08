#ifndef __VIDEO_H__
#define __VIDEO_H__

extern void get_dev(char *arg);
extern void open_dev(char *arg,int cameraFd);
extern void get_capability(int fd);
extern void select_input(int fd);
extern void get_standard(int fd);
extern void set_frame(int fd);
extern void do_frame(int fd);
#endif


