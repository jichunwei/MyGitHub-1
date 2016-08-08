#ifndef __VECTOR_FD__
#define __VECTOR_FD__

typedef struct {
    int  *fd;
    int  counter;
    int  max_counter;
}VectorFD;

extern VectorFD *create_vector_fd(void);
extern void destroy_vector_fd(VectorFD*);
extern int get_fd(VectorFD*,int index);
extern void remove_fd(VectorFD *,int fd);
extern void add_fd(VectorFD*,int fd);

#endif
