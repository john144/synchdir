
foops.dll: dlldata.obj foo_p.obj foo_i.obj
	link /dll /out:foops.dll /def:foops.def /entry:DllMain dlldata.obj foo_p.obj foo_i.obj \
		kernel32.lib rpcndr.lib rpcns4.lib rpcrt4.lib oleaut32.lib uuid.lib \

.c.obj:
	cl /c /Ox /DWIN32 /D_WIN32_WINNT=0x0400 /DREGISTER_PROXY_DLL \
		$<

clean:
	@del foops.dll
	@del foops.lib
	@del foops.exp
	@del dlldata.obj
	@del foo_p.obj
	@del foo_i.obj
