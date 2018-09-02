// CMyObject.h : Declaration of the CCMyObject

#ifndef __CMYOBJECT_H_
#define __CMYOBJECT_H_

#include "resource.h"       // main symbols

/////////////////////////////////////////////////////////////////////////////
// CCMyObject
class ATL_NO_VTABLE CCMyObject : 
	public CComObjectRootEx<CComSingleThreadModel>,
	public CComCoClass<CCMyObject, &CLSID_CMyObject>,
	public IDispatchImpl<ICMyObject, &IID_ICMyObject, &LIBID_FOOLib>
{
public:
	CCMyObject()
	{
	}

DECLARE_REGISTRY_RESOURCEID(IDR_CMYOBJECT)

DECLARE_PROTECT_FINAL_CONSTRUCT()

BEGIN_COM_MAP(CCMyObject)
	COM_INTERFACE_ENTRY(ICMyObject)
	COM_INTERFACE_ENTRY(IDispatch)
END_COM_MAP()

// ICMyObject
public:
	STDMETHOD(Connect)();
};

#endif //__CMYOBJECT_H_
