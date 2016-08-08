#ifndef __PV_H__
#define __PV_H__

extern void I(int semid,int val);
extern void D(int semid);
extern void P(int semid,int val);
extern void V(int semid,int val);
#endif
