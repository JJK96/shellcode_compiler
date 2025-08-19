const win32 = @import("win32");
extern fn printf(format: [*:0]const u8, ...) void;

pub fn main() void {
    printf("Hello, world!\n");
    _ = win32.system.threading.WinExec("calc.exe", win32.everything.SW_SHOW.SHOWNORMAL);
}
