#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <wchar.h>
#include <windows.h>
#include <winternl.h>

int main(void) {
  WinExec("calc.exe", SW_SHOWNORMAL);
  return 0;
}
