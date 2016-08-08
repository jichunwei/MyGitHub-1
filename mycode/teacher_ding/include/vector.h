#ifndef __VECTOR_H__
#define __VECTOR_H__
typedef  int ElementType ; 
typedef struct{
    ElementType       *_array;
    int               _counter;
    int               _max_counter;
}vector;

extern  vector* create_vector(int max_size);
extern void destroy_vector(vector* v);
extern void add_vector(vector* v, ElementType e);
extern int remove_vector(vector* v, ElementType e);
extern ElementType get_vector(vector* v,int index);
extern void set_vector(vector* v, int index, ElementType e); 
#endif
