#ifndef __MSTDIO_H__
#define __MSTDIO_H__
#include <sys/types.h>
#define MEOF -1
enum mode{READ,WRITE,APPEND};
typedef struct{
	int _fd;
	char *_buffer;
	int _mode;
	char *_nextc;
	off_t _left;
}MFILE;

extern MFILE* mfopen(const char * const pathname,
		const char * const mode);
extern int   mfclose(MFILE *fp);
extern int 	mfgetc(MFILE *fp);
extern int mfputc(int character ,MFILE *fp);
extern int mungetc(int character ,MFILE *fp);
extern char* mfgets(char *buff,int size ,MFILE *fp);
extern char* mfputs(char *buff,MFILE *fp);
extern size_t mfread(void *buff,size_t size,size_t counter,MFILE *fp);
extern size_t mfwriter(void *buff,size_t size,size_t counter,MFILE *fp);
extern MFILE * mfdopen(int fd,char const* mode);
extern void mfflush(MFILE *fp);
#endif

