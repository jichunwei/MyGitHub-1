#include "vector.h"
#include <assert.h>
#include <malloc.h>
#include <stdlib.h>
#include <memory.h>

vector *create_vector(int max_size)
{
    vector *v = (vector*)malloc(sizeof(vector));
    assert(v != NULL);
    v->_array = (ElementType *)malloc(max_size*sizeof(ElementType));
    assert(v->_array != NULL);
    v->_counter = 0;
    v->_max_counter = max_size;
    return v;
}

void destroy_vector(vector* v)
{
    assert(v != NULL);
    free(v->_array);
    free(v);
}

static void encapacity(vector *v)
{
    if(v->_counter >= v->_max_counter)
    {
	ElementType *oarray = v->_array;
	v->_array = (ElementType *)
	    malloc(sizeof(ElementType)*(v->_max_counter +10));
	memcpy(v->_array,oarray,v->_counter*sizeof(ElementType));
	v->_max_counter += 10;
	free(oarray);
    }
}

void add_vector(vector* v, ElementType e)
{
    assert(v != NULL);
    encapacity(v);
    v->_array[v->_counter++] = e; 
}

static int indexof(vector *v,ElementType e)
{
    int index = -1;
    int i = 0;
    for(; i < v->_counter; i++)
    {
	if(v->_array[i] == e)
	{
	    index = i;
	    break;
	}
    }
    return index;
}

int remove_vector(vector* v, ElementType e)
{
    assert(v != NULL);
    int index = indexof(v,e);
    if(index == -1) return 0;
    int i;
    for(i = index; i < v->_counter -1; i++)
    {
	v->_array[i] = v->_array[i+1];
    }
    v->_counter -= 1;
    return 1;
}

ElementType get_vector(vector* v,int index)
{
    assert(v !=NULL);
    assert((index >= 0) && (index < v->_counter)); 
    return v->_array[index];

}
    
void set_vector(vector* v, int index, ElementType e)
{
    assert(v != NULL);
    assert((index >= 0) && (index < v->_counter));
    v->_array[index] = e;

}

   
