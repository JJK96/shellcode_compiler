#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <wchar.h>
#include <windows.h>
#include <winternl.h>

typedef struct _MY_LDR_DATA_TABLE_ENTRY {
  PVOID Reserved1[2];
  LIST_ENTRY InMemoryOrderLinks;
  PVOID Reserved2[2];
  PVOID DllBase;
  PVOID Reserved3[2];
  UNICODE_STRING FullDllName;
  UNICODE_STRING BaseDllName;
  PVOID Reserved5[3];
  __C89_NAMELESS union {
    ULONG CheckSum;
    PVOID Reserved6;
  };
  ULONG TimeDateStamp;
} MY_LDR_DATA_TABLE_ENTRY,*PMY_LDR_DATA_TABLE_ENTRY;

uint64_t getDllBase(unsigned long);
uint64_t loadDll(unsigned long);
uint64_t parseHdrForPtr(uint64_t, unsigned long);

unsigned long djb2(unsigned char*);
unsigned long unicode_djb2(const wchar_t* str);
WCHAR* toLower(WCHAR* str);

//Based on https://github.com/FalconForceTeam/BOF2shellcode/blob/master/ApiResolve.c
uint64_t 
getFunctionPtr(unsigned long dll_hash, unsigned long function_hash) {

	uint64_t dll_base = 0x00;
	uint64_t ptr_function = 0x00;

	dll_base = getDllBase(dll_hash);
	// if (dll_base == 0) {
	// 	dll_base = loadDll(dll_hash);
	// 	if (dll_base == 0)
	// 		return 0;
	// }

	ptr_function = parseHdrForPtr(dll_base, function_hash);

	return ptr_function;
}


uint64_t 
parseHdrForPtr(uint64_t dll_base, unsigned long function_hash) {

	PIMAGE_NT_HEADERS nt_hdrs = NULL;
	PIMAGE_DATA_DIRECTORY data_dir= NULL;
	PIMAGE_EXPORT_DIRECTORY export_dir= NULL;

	uint32_t* ptr_exportadrtable = 0x00;
	uint32_t* ptr_namepointertable = 0x00;
	uint16_t* ptr_ordinaltable = 0x00;

	uint32_t idx_functions = 0x00;

	unsigned char* ptr_function_name = NULL;


	nt_hdrs = (PIMAGE_NT_HEADERS)(dll_base + (uint64_t)((PIMAGE_DOS_HEADER)(size_t)dll_base)->e_lfanew);
	data_dir = (PIMAGE_DATA_DIRECTORY)&nt_hdrs->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT];
	export_dir = (PIMAGE_EXPORT_DIRECTORY)(dll_base + (uint64_t)data_dir->VirtualAddress);

	ptr_exportadrtable = (uint32_t*)(dll_base + (uint64_t)export_dir->AddressOfFunctions);
	ptr_namepointertable = (uint32_t*)(dll_base + (uint64_t)export_dir->AddressOfNames);
	ptr_ordinaltable = (uint16_t*)(dll_base + (uint64_t)export_dir->AddressOfNameOrdinals);

	for(idx_functions = 0; idx_functions < export_dir->NumberOfNames; idx_functions++){

		ptr_function_name = (unsigned char*)dll_base + (ptr_namepointertable[idx_functions]);
		if (djb2(ptr_function_name) == function_hash) {
			WORD nameord = ptr_ordinaltable[idx_functions];
			DWORD rva = ptr_exportadrtable[nameord];
			return dll_base + rva;
		}

	}

	return 0;
}

uint64_t 
getDllBase(unsigned long dll_hash) {

	PPEB peb = (PPEB)__readgsqword(0x60);
  PPEB_LDR_DATA ldr = peb->Ldr;
  PLIST_ENTRY item = ldr->InMemoryOrderModuleList.Blink;
  PMY_LDR_DATA_TABLE_ENTRY dll = NULL;

  do {
    dll = CONTAINING_RECORD(item, MY_LDR_DATA_TABLE_ENTRY, InMemoryOrderLinks);

		if (dll->BaseDllName.Buffer == NULL)
			return 0;

		if (unicode_djb2(toLower(dll->BaseDllName.Buffer)) == dll_hash)
			return (uint64_t)dll->DllBase;

      item = item->Blink;
	} while (item != NULL);

	return 0;
}

unsigned long
djb2(unsigned char* str)
{
	unsigned long hash = 5381;
	int c;

	while ((c = *str++))
		hash = ((hash << 5) + hash) + c;

	return hash;
}

unsigned long 
unicode_djb2(const wchar_t* str)
{

	unsigned long hash = 5381;
	DWORD val;

	while (*str != 0) {
		val = (DWORD)*str++;
		hash = ((hash << 5) + hash) + val;
	}

	return hash;

}

WCHAR* 
toLower(WCHAR *str)
{

	WCHAR* start = str;

	while (*str) {

		if (*str <= L'Z' && *str >= 'A') {
			*str += 32;
		}

		str += 1;

	}

	return start;

}

{% for dll in dlls %}
#define HASH_{{dll[:-4]}} {{dll | hash}}
{% endfor %}

{% for entry in entries %}
{{entry}}
{% endfor %}
