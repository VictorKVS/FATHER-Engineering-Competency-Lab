from __future__ import annotations

import ctypes
import os
import shutil
import subprocess  # nosec B404 - sandbox intentionally launches an exact allowlisted executable
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


class SandboxExecutionError(RuntimeError):
    pass


@dataclass(frozen=True)
class ProcessSandboxResult:
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool
    workdir: str


class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_int64),
        ("PerJobUserTimeLimit", ctypes.c_int64),
        ("LimitFlags", ctypes.c_uint32),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", ctypes.c_uint32),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", ctypes.c_uint32),
        ("SchedulingClass", ctypes.c_uint32),
    ]


class IO_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("ReadOperationCount", ctypes.c_uint64),
        ("WriteOperationCount", ctypes.c_uint64),
        ("OtherOperationCount", ctypes.c_uint64),
        ("ReadTransferCount", ctypes.c_uint64),
        ("WriteTransferCount", ctypes.c_uint64),
        ("OtherTransferCount", ctypes.c_uint64),
    ]


class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
        ("IoInfo", IO_COUNTERS),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]


class _WindowsJob:
    JOB_OBJECT_LIMIT_ACTIVE_PROCESS = 0x00000008
    JOB_OBJECT_LIMIT_PROCESS_MEMORY = 0x00000100
    JOB_OBJECT_LIMIT_JOB_MEMORY = 0x00000200
    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
    JobObjectExtendedLimitInformation = 9

    def __init__(
        self,
        *,
        active_process_limit: int | None = None,
        process_memory_limit_bytes: int | None = None,
        job_memory_limit_bytes: int | None = None,
    ) -> None:
        if os.name != "nt":
            self.handle = None
            return
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateJobObjectW.restype = ctypes.c_void_p
        self._kernel32 = kernel32
        self.handle = kernel32.CreateJobObjectW(None, None)
        if not self.handle:
            raise OSError(ctypes.get_last_error(), "CreateJobObjectW failed")

        info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        flags = self.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE

        if active_process_limit is not None:
            if active_process_limit <= 0:
                raise ValueError("active_process_limit must be positive")
            info.BasicLimitInformation.ActiveProcessLimit = active_process_limit
            flags |= self.JOB_OBJECT_LIMIT_ACTIVE_PROCESS

        if process_memory_limit_bytes is not None:
            if process_memory_limit_bytes <= 0:
                raise ValueError("process_memory_limit_bytes must be positive")
            info.ProcessMemoryLimit = process_memory_limit_bytes
            flags |= self.JOB_OBJECT_LIMIT_PROCESS_MEMORY

        if job_memory_limit_bytes is not None:
            if job_memory_limit_bytes <= 0:
                raise ValueError("job_memory_limit_bytes must be positive")
            info.JobMemoryLimit = job_memory_limit_bytes
            flags |= self.JOB_OBJECT_LIMIT_JOB_MEMORY

        info.BasicLimitInformation.LimitFlags = flags
        ok = kernel32.SetInformationJobObject(
            ctypes.c_void_p(self.handle),
            self.JobObjectExtendedLimitInformation,
            ctypes.byref(info),
            ctypes.sizeof(info),
        )
        if not ok:
            err = ctypes.get_last_error()
            kernel32.CloseHandle(ctypes.c_void_p(self.handle))
            self.handle = None
            raise OSError(err, "SetInformationJobObject failed")

    def assign(self, process_handle: int) -> None:
        if not self.handle:
            return
        ok = self._kernel32.AssignProcessToJobObject(
            ctypes.c_void_p(self.handle), ctypes.c_void_p(process_handle)
        )
        if not ok:
            raise OSError(ctypes.get_last_error(), "AssignProcessToJobObject failed")

    def close(self) -> None:
        if self.handle:
            self._kernel32.CloseHandle(ctypes.c_void_p(self.handle))
            self.handle = None


class WindowsProcessSandbox:
    def __init__(
        self,
        *,
        allowed_executables: Sequence[str],
        timeout_seconds: float = 10.0,
        max_output_chars: int = 100_000,
        active_process_limit: int | None = 2,
        process_memory_limit_mb: int | None = 256,
        job_memory_limit_mb: int | None = 384,
    ) -> None:
        self.allowed_executables = {str(Path(p).resolve()).lower() for p in allowed_executables}
        self.timeout_seconds = timeout_seconds
        self.max_output_chars = max_output_chars
        self.active_process_limit = active_process_limit
        self.process_memory_limit_mb = process_memory_limit_mb
        self.job_memory_limit_mb = job_memory_limit_mb

        for name, value in (
            ("active_process_limit", active_process_limit),
            ("process_memory_limit_mb", process_memory_limit_mb),
            ("job_memory_limit_mb", job_memory_limit_mb),
        ):
            if value is not None and value <= 0:
                raise ValueError(f"{name} must be positive")

    def run(self, executable: str, args: Sequence[str] = ()) -> ProcessSandboxResult:
        exe = str(Path(executable).resolve())
        if exe.lower() not in self.allowed_executables:
            raise PermissionError("executable is not allowlisted")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.max_output_chars <= 0:
            raise ValueError("max_output_chars must be positive")

        workdir = tempfile.mkdtemp(prefix="fua-sandbox-")
        env = {
            "PATH": os.environ.get("SystemRoot", r"C:\\Windows") + r"\\System32;" + str(Path(exe).parent),
            "SystemRoot": os.environ.get("SystemRoot", r"C:\\Windows"),
            "WINDIR": os.environ.get("WINDIR", os.environ.get("SystemRoot", r"C:\\Windows")),
            "TEMP": workdir,
            "TMP": workdir,
            "PYTHONNOUSERSITE": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "FUA_SANDBOX": "1",
        }

        creationflags = 0
        if os.name == "nt":
            creationflags = subprocess.CREATE_NO_WINDOW

        job = _WindowsJob(
            active_process_limit=self.active_process_limit,
            process_memory_limit_bytes=(
                None
                if self.process_memory_limit_mb is None
                else self.process_memory_limit_mb * 1024 * 1024
            ),
            job_memory_limit_bytes=(
                None
                if self.job_memory_limit_mb is None
                else self.job_memory_limit_mb * 1024 * 1024
            ),
        )
        proc = None
        timed_out = False
        try:
            proc = subprocess.Popen(  # nosec B603 - exe is resolved and checked against exact allowlist; shell=False
                [exe, *args],
                cwd=workdir,
                env=env,
                shell=False,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=creationflags,
            )
            if os.name == "nt":
                job.assign(int(proc._handle))
            try:
                stdout, stderr = proc.communicate(timeout=self.timeout_seconds)
            except subprocess.TimeoutExpired:
                timed_out = True
                job.close()
                kill_error = None
                try:
                    proc.kill()
                except Exception as exc:
                    kill_error = exc
                stdout, stderr = proc.communicate(timeout=5)
                if kill_error is not None and proc.poll() is None:
                    raise SandboxExecutionError(
                        f"timed-out process could not be terminated: {kill_error}"
                    )

            stdout = stdout[: self.max_output_chars]
            stderr = stderr[: self.max_output_chars]
            return ProcessSandboxResult(
                returncode=proc.returncode if proc.returncode is not None else -1,
                stdout=stdout,
                stderr=stderr,
                timed_out=timed_out,
                workdir=workdir,
            )
        finally:
            job.close()
            shutil.rmtree(workdir, ignore_errors=True)
