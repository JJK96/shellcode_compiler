const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const zigwin32_dep = b.dependency("zigwin32", .{});

    const mod = b.addModule("payload", .{
        .root_source_file = b.path("payload.zig"),
        .target = target,
        .optimize = optimize,
        .unwind_tables = std.builtin.UnwindTables.none,
        .strip = true,
        .pic = true,
    });

    mod.addImport("win32", zigwin32_dep.module("win32"));

    const obj = b.addObject(.{
        .name = "payload",
        .root_module = mod,
    });

    const write = b.addInstallFile(obj.getEmittedBin(), "payload.o");

    b.getInstallStep().dependOn(&write.step);
}
