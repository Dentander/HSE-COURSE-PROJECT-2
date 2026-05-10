import asyncio
import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

import httpx
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)

USER_CSPROJ = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>
</Project>
"""

app = FastAPI(title="C# code runner", version="0.2.0")


class RunIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    job_id: int = Field(alias="jobId")
    code: str
    inputs: list[str]
    outputs: list[str]
    callback_url: str = Field(alias="callbackUrl")
    callback_secret: str = Field(alias="callbackSecret")
    time_limit_ms: int = Field(default=10_000, alias="timeLimitMs")


def norm_out(s: str) -> str:
    if not s:
        return ""
    return s.replace("\r\n", "\n").replace("\r", "\n").rstrip(" \t\n\r")


def run_user_program(
    code: str,
    inputs: list[str],
    outputs: list[str],
    time_limit_ms: int,
) -> tuple[str, str]:
    tmp = tempfile.mkdtemp(prefix="csrun-")
    try:
        Path(tmp, "Program.cs").write_text(code, encoding="utf-8")
        csproj_path = Path(tmp, "UserApp.csproj")
        csproj_path.write_text(USER_CSPROJ, encoding="utf-8")

        build = subprocess.run(
            ["dotnet", "build", str(csproj_path), "-c", "Release", "-v:m"],
            cwd=tmp,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if build.returncode != 0:
            snippet = (build.stderr + build.stdout).strip()
            if len(snippet) > 2000:
                snippet = snippet[:2000] + "…"
            return "CE", snippet if snippet else "dotnet build failed"

        limit_sec = max(1.0, time_limit_ms / 1000.0) if time_limit_ms > 0 else 10.0

        for i, (inp, exp) in enumerate(zip(inputs, outputs)):
            proc = subprocess.Popen(
                [
                    "dotnet",
                    "run",
                    "--no-build",
                    "-c",
                    "Release",
                    "--project",
                    str(csproj_path),
                ],
                cwd=tmp,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            try:
                out, err = proc.communicate(input=inp, timeout=limit_sec)
            except subprocess.TimeoutExpired:
                proc.kill()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                return "TL", f"test #{i + 1}: time limit"

            if proc.returncode == 137 or "outofmemory" in (err or "").lower():
                return "ML", f"test #{i + 1}: out of memory"

            if proc.returncode != 0:
                msg = ((err or "") + (out or "")).strip()
                if len(msg) > 800:
                    msg = msg[:800] + "…"
                return "RE", f"test #{i + 1}: exit {proc.returncode} {msg}"

            if norm_out(out or "") != norm_out(exp):
                return "WA", f"test #{i + 1}: wrong output"

        return "OK", ""
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/run")
async def run_tests(body: RunIn):
    verdict, detail = "OK", ""
    try:
        if len(body.inputs) != len(body.outputs) or not body.inputs:
            verdict, detail = "CE", "inputs/outputs length mismatch or empty"
        else:
            verdict, detail = await asyncio.to_thread(
                run_user_program,
                body.code,
                body.inputs,
                body.outputs,
                body.time_limit_ms,
            )
    except Exception as e:
        logger.exception("run failed")
        verdict, detail = "CE", str(e)

    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(
            body.callback_url,
            json={"jobId": body.job_id, "verdict": verdict, "detail": detail},
            headers={"X-Code-Run-Secret": body.callback_secret},
        )
        r.raise_for_status()
    return {"ok": True}
