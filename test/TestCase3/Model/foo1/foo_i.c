/* this file contains the actual definitions of */
/* the IIDs and CLSIDs */

/* link this file in with the server and any clients */


/* File created by MIDL compiler version 5.01.0164 */
/* at Thu Mar 25 11:32:20 2004
 */
/* Compiler settings for F:\Projects\foo\foo.idl:
    Oicf (OptLev=i2), W1, Zp8, env=Win32, ms_ext, c_ext
    error checks: allocation ref bounds_check enum stub_data 
*/
//@@MIDL_FILE_HEADING(  )
#ifdef __cplusplus
extern "C"{
#endif 


#ifndef __IID_DEFINED__
#define __IID_DEFINED__

typedef struct _IID
{
    unsigned long x;
    unsigned short s1;
    unsigned short s2;
    unsigned char  c[8];
} IID;

#endif // __IID_DEFINED__

#ifndef CLSID_DEFINED
#define CLSID_DEFINED
typedef IID CLSID;
#endif // CLSID_DEFINED

const IID IID_ICMyObject = {0xEC45FE4F,0xE070,0x4100,{0x96,0xC9,0xB3,0x93,0x43,0x69,0x77,0x75}};


const IID LIBID_FOOLib = {0xD236B5A8,0x05F9,0x44F8,{0xA3,0x8C,0x06,0x93,0x99,0x27,0xC3,0x00}};


const CLSID CLSID_CMyObject = {0x8FE3894C,0x8516,0x4534,{0x9A,0x99,0x0C,0xF6,0xEA,0x42,0x00,0xFB}};


#ifdef __cplusplus
}
#endif

