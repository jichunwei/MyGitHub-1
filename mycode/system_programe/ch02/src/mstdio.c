#include <assert.h>
#include <sys/types.h>
#include <fcntl.h>
#include <errno.h>
#include <unistd.h>
#include "mstdio.h"
#include <string.h>
#include <stdlib.h>

#define  BUFFER_LEN 4096
MFILE* mfopen(const char * const pathname,
		const char * const mode)
{
	int fd;
	if(!strcmp(mode,"r")){
		fd = open (pathname,O_RDONLY);
	}
	else if(!strcmp(mode,"w")){
		fd = open ( pathname,O_WRONLY | O_CREAT | O_TRUNC,0777);
	}
	else if(!strcmp(mode,"a")){
		fd = open ( pathname,O_WRONLY | O_CREAT | O_APPEND,0777);
	}
	else {
		return NULL;
	}	
	if(fd < 0){
		return NULL;
	}
	return mfdopen(fd,mode);
}

int   mfclose(MFILE *fp)
{
	mfflush(fp);
	int res = close (fp->_fd);
	free(fp->_buffer);
	free(fp);
	return res;
}

int 	mfgetc(MFILE *fp)
{
	assert(fp->_mode == READ);
	if(fp->_left == 0){
		ssize_t size = read(fp->_fd,fp->_buffer,BUFFER_LEN);
		assert (size >= 0);
		if(size == 0){
			return MEOF;
		}
		fp->_nextc = fp->_buffer;
		fp->_left = size ;
	}
	char c= *(fp->_nextc);
	fp->_nextc++;
	fp->_left -=1;
	return c;
}

int mfputc(int character ,MFILE *fp)
{
	assert((fp->_mode == WRITE ||fp->_mode == APPEND));
	if(fp->_left == 0){
		if(write(fp->_fd,fp->_buffer,BUFFER_LEN) !=BUFFER_LEN){
			perror(write);
			return -1;
		}
		fp->_nextc = fp->_buffer;
		fp->_left = BUFFER_LEN;
	}
	*fp->_nextc = (char)character;
	fp->_nextc++;
	fp->_left -=1;
	return 1;
}
int mungetc(int character ,MFILE *fp);
char* mfgets(char *buff,int size ,MFILE *fp);
char* mfputs(char *buff,MFILE *fp);
size_t mfread(void *buff,size_t size,size_t counter,MFILE *fp);
size_t mfwriter(void *buff,size_t size,size_t counter,MFILE *fp);
MFILE * mfdopen(int fd,char const* mode)
{
	MFILE *fp = (MFILE *) malloc (sizeof(MFILE));
	assert(fp != NULL);
	fp->_buffer = (char *)malloc(BUFFER_LEN);
	assert(fp->_buffer != NULL);
	fp->_fd = fd;
	fp->_nextc = fp->_buffer;
	fp->_left = 0;
	if(!strcmp(mode,"r")){
		fp->_mode = READ;
		fp->_left = 0;
	}
	else if(!strcmp(mode,"w")){
		fp->_mode = WRITE;
		fp->_left = BUFFER_LEN;
	}
	else if(!strcmp(mode,"a")){
		fp->_mode = APPEND;
	}
	return fp;
}
void mfflush(MFILE *fp)
{
	if(fp->_mode == READ) {
		fp->_nextc = fp->_buffer;
		fp->_left = 0L;
	}
	else {
		write(fp->_fd,fp->_buffer,(BUFFER_LEN-fp->_left));
        fp->_nextc = fp->_buffer;
        fp->_left = BUFFER_LEN;
	}
}
