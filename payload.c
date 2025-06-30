#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <wchar.h>
#include <windows.h>
#include <winternl.h>

#define FUNC __attribute__((section(".func")))

#define ALIGN_STACK()                                                          \
  __asm__ __volatile__(                                                        \
      "mov %%rsp, %%rax;" /* Move stack pointer to rax */                      \
      "and $0xF, %%rax;"  /* Check if aligned to 16 bytes */                   \
      "jz aligned;"       /* If aligned, jump to aligned If not aligned,       \
                             adjust the stack pointer */                       \
      "sub $8, %%rsp;"    /* Decrease stack pointer by 8 bytes */              \
      "xor %0, %0;"       /* Optionally zero out the allocated space */        \
      "aligned:"                                                               \
      :        /* No output operands */                                        \
      : "r"(0) /* Input operand (to zero out) */                               \
      : "%rax" /* Clobbered register */                                        \
  );

typedef UINT(WINAPI *WinExecPtr)(LPCSTR lpCmdLine, UINT uCmdShow);

FUNC int my_wcscmp(const wchar_t *s1, const wchar_t *s2) {
  while (*s1 != L'\0' && *s2 != L'\0') {
    if (*s1 != *s2) {
      return (*s1 < *s2) ? -1 : 1;
    }

    s1++;
    s2++;
  }

  if (*s1 == L'\0' && *s2 == L'\0') {
    return 0;
  }

  return (*s1 == L'\0') ? -1 : 1;
}

FUNC int my_strcmp(const char *str1, const char *str2) {
  while (*str1 != '\0' && *str2 != '\0') {
    if (*str1 != *str2) {
      return (*str1 < *str2) ? -1 : 1;
    }
    str1++;
    str2++;
  }

  if (*str1 == '\0' && *str2 == '\0') {
    return 0;
  }

  return (*str1 == '\0') ? -1 : 1;
}

FUNC PLDR_DATA_TABLE_ENTRY GetDllLdr(PPEB_LDR_DATA ldr, wchar_t *name) {
  PLIST_ENTRY item = ldr->InMemoryOrderModuleList.Blink;
  PLDR_DATA_TABLE_ENTRY dll = NULL;

  do {
    dll = CONTAINING_RECORD(item, LDR_DATA_TABLE_ENTRY, InMemoryOrderLinks);

    if (my_wcscmp(dll->FullDllName.Buffer, name) == 0) {
      return dll;
    }

    item = item->Blink;
  } while (item != NULL);

  return NULL;
}

FUNC PPEB GetPEB(void) {
  uint64_t value = 0;

  // Inline assembly to read from the GS segment
  asm volatile("movq %%gs:%1, %0"
               : "=r"(value)            // output
               : "m"(*(uint64_t *)0x60) // input
               :                        // no clobbered registers
  );

  return (PPEB)value;
}

int start(void) {
  PPEB peb = GetPEB();

  wchar_t dll_name[] = {
      L'C', L':', L'\\', L'W', L'I', L'N', L'D', L'O', L'W',  L'S', L'\\',
      L'S', L'y', L's',  L't', L'e', L'm', L'3', L'2', L'\\', L'K', L'E',
      L'R', L'N', L'E',  L'L', L'3', L'2', L'.', L'D', L'L',  L'L', L'\0',
  };

  // Get address of kernel32.dll
  PLDR_DATA_TABLE_ENTRY kernel32_ldr = GetDllLdr(peb->Ldr, dll_name);
  PIMAGE_DOS_HEADER kernel32 = (PIMAGE_DOS_HEADER)kernel32_ldr->DllBase;

  // Get address of PE headers
  PVOID pe_hdrs = (PVOID)((PVOID)kernel32 + kernel32->e_lfanew);

  // Get Export Address Table RVA
  DWORD eat_rva = *(PDWORD)(pe_hdrs + 0x88);

  // Get address of Export Address Table
  PIMAGE_EXPORT_DIRECTORY eat =
      (PIMAGE_EXPORT_DIRECTORY)((PVOID)kernel32 + eat_rva);

  // Get address of function names table
  PDWORD name_rva = (PDWORD)((PVOID)kernel32 + eat->AddressOfNames);

  // Get function name
  char func_name[] = {'W', 'i', 'n', 'E', 'x', 'e', 'c', '\0'};
  uint64_t i = 0;

  do {
    char *tmp = (char *)((PVOID)kernel32 + name_rva[i]);

    if (my_strcmp(tmp, func_name) == 0) {
      break;
    }
    i++;
  } while (true);

  // Get function ordinal
  PWORD ordinals = (PWORD)((PVOID)kernel32 + eat->AddressOfNameOrdinals);
  WORD ordinal = ordinals[i];

  // Get function pointer
  PDWORD func_rvas = (PDWORD)((PVOID)kernel32 + eat->AddressOfFunctions);
  DWORD func_rva = func_rvas[ordinal];
  WinExecPtr winExecPtr = (WinExecPtr)((PVOID)kernel32 + func_rva);

  // Run WinAPI function
  char path[] = {'c', 'a', 'l', 'c', '.', 'e', 'x', 'e', '\0'};
  ALIGN_STACK();
  winExecPtr(path, SW_SHOWNORMAL);

  return 0;
}
