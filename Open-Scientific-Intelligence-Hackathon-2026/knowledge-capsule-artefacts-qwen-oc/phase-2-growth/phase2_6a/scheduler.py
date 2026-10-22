#!/usr/bin/env python3
"""Phase 2 (6a) runner: 24 PBE grid-convergence single points (OMP) + PBE0 single points (MPI probe chain).

Memory model
- PBE job estimates: serial peak from the C1 dry run (bigdft-tool), C1/bigdft/dryrun/dryrun_summary.json.
- PBE jobs: OMP only, 12 threads (8 threads if est >= 40 GB), at most 2 concurrent, pre-launch gate.
- PBE0 jobs: MPICH 24 ranks x 1 OMP, run alone, RSS kill threshold 40 GB total (probe mode per C1's
  fail-pbe0-oom: hybrid memory must be measured, not trusted); grid fallback chain
  h0.35_r6-9 -> h0.40_r6-9 -> h0.45_r6-9.
Outputs: progress.json (machine), scheduler.log (human). All times UTC ISO.
"""
import json
import os
import re
import signal
import subprocess
import time
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.abspath(__file__))
C1 = "/home/user/Work/osi-hackathon-2026/C1"
BIGDFT = "/home/user/Work/build/install/bin/bigdft"
MPIEXEC = "/usr/bin/mpiexec"
PROG = os.path.join(BASE, "progress.json")
LOGF = os.path.join(BASE, "scheduler.log")
MPI_N = 24
OMP_N = 12
BIG_THREADS = 8          # threads for jobs with est >= BIG_EST_GB
BIG_EST_GB = 40.0
PROBE_KILL_GB = 40.0     # total RSS threshold for MPI PBE0 probes
POLL_S = 20

DRYRUN = json.load(open(os.path.join(C1, "bigdft/dryrun/dryrun_summary.json")))

def est_gb(name):
    return round(DRYRUN[name]["memory_peak_MB"] / 1024.0, 3)

# queue: PBE grid study dropped per user direction 2026-10-21 (minimal triplet-energy
# path: PBE0 pair only). The 24 PBE inputs remain staged in runs/ for a later grid study.
JOBS = []
for grid in ("h0.35_r6-9", "h0.40_r6-9", "h0.45_r6-9"):
    for st in ("S0", "T1"):
        n = f"6a_S1_{st}_pbe0_at_S1_{grid}"
        JOBS.append({"name": n, "dir": f"pbe0/runs/{n}", "est": None, "kind": "mpi", "threads": 1})

def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def log(msg):
    line = f"[{now()}] {msg}"
    with open(LOGF, "a") as f:
        f.write(line + "\n")
    print(line, flush=True)

def mem_available_gb():
    for line in open("/proc/meminfo"):
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) / 1e6
    return 0.0

def proc_rss_gb(pid):
    try:
        with open(f"/proc/{pid}/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) / 1e6
    except (FileNotFoundError, ProcessLookupError):
        pass
    return None

def _proc_fields(pid):
    """(ppid, pgrp, rss_gb) for a pid, or None if gone. rsplit(')') because comm may contain spaces."""
    try:
        with open(f"/proc/{pid}/stat") as f:
            f_ = f.read().rsplit(")", 1)[1].split()
        rss = 0.0
        with open(f"/proc/{pid}/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    rss = int(line.split()[1]) / 1e6
        return int(f_[1]), int(f_[2]), rss
    except (FileNotFoundError, ProcessLookupError, IndexError, ValueError):
        return None

def tree_pids(root):
    """All pids in the process tree rooted at root (inclusive). MPICH gives each rank its own
    process group, so pgrp-based scanning misses the ranks; a ppid tree walk is authoritative."""
    out, stack = [], [root]
    while stack:
        pid = stack.pop()
        try:
            with open(f"/proc/{pid}/stat") as f:
                f.read()
        except (FileNotFoundError, ProcessLookupError):
            continue
        out.append(pid)
        wanted = str(pid)
        for p in os.listdir("/proc"):
            if not p.isdigit():
                continue
            try:
                with open(f"/proc/{p}/stat") as f:
                    if f.read().rsplit(")", 1)[1].split()[1] == wanted:
                        stack.append(int(p))
            except (FileNotFoundError, ProcessLookupError, IndexError):
                continue
    return out

def tree_rss_gb(root):
    total = 0.0
    for pid in tree_pids(root):
        got = _proc_fields(pid)
        if got:
            total += got[2]
    return total

def log_final(path):
    """Return (final_eks, has_final_flag)."""
    if not os.path.exists(path):
        return None, False
    final, last = None, None
    with open(path) as f:
        for line in f:
            m = re.search(r"EKS:\s*(-?\d+\.?\d*(?:[eE][+-]?\d+)?)", line)
            if m:
                last = float(m.group(1))
                if "#FINAL" in line:
                    final = float(m.group(1))
    if final is not None:
        return final, True
    return last, False

def job_log(job):
    return os.path.join(BASE, job["dir"], f"log-{job['name']}.yaml")

def console(job):
    return os.path.join(BASE, job["dir"], "console.log")

def launch(job):
    d = os.path.join(BASE, job["dir"])
    env = dict(os.environ, OMP_NUM_THREADS=str(job["threads"]))
    if job["kind"] == "omp":
        cmd = ["bash", "-c", f"cd {d} && ulimit -s unlimited && {BIGDFT} -n {job['name']}"]
    else:
        cmd = ["bash", "-c", f"cd {d} && ulimit -s unlimited && {MPIEXEC} -n {MPI_N} {BIGDFT} -n {job['name']}"]
    cf = open(console(job), "ab")
    proc = subprocess.Popen(cmd, stdout=cf, stderr=subprocess.STDOUT, start_new_session=True)
    return proc

state = {}          # name -> dict
pending = []
running = {}        # name -> dict(proc, ...)

def init():
    for job in JOBS:
        name, path = job["name"], job_log(job)
        eks, final = log_final(path)
        if final:
            state[name] = {"name": name, "state": "done", "est_gb": job["est"],
                           "threads": job["threads"], "kind": job["kind"], "EKS_Ha": eks,
                           "note": "completed in a previous scheduler run"}
        else:
            state[name] = {"name": name, "state": "pending", "est_gb": job["est"],
                           "threads": job["threads"], "kind": job["kind"]}
            pending.append(name)

def write_progress():
    data = {"ts": now(), "mem_available_gb": round(mem_available_gb(), 2),
            "running": sorted(running), "pending": list(pending),
            "done": sorted(n for n, s in state.items() if s["state"] == "done"),
            "failed": sorted(n for n, s in state.items() if s["state"].startswith("failed")),
            "jobs": {n: state[n] for n in state}}
    with open(PROG, "w") as f:
        json.dump(data, f, indent=1)

def main():
    init()
    log(f"scheduler start: {len(pending)} pending, "
        f"{sum(1 for s in state.values() if s['state'] == 'done')} already done")
    while pending or running:
        # --- reap finished jobs ---
        for name in list(running):
            info = running[name]
            rc = info["proc"].poll()
            if rc is None:
                # RSS over the full process tree. bash -c exec-optimizes to the last command,
                # so the launched pid is the tree root (bigdft for OMP; mpiexec for MPI).
                info["rss_gb"] = round(tree_rss_gb(info["proc"].pid), 2)
                if info["kind"] == "mpi" and info["rss_gb"] > PROBE_KILL_GB:
                    # 60 s grace: C1's thioxanthone PBE0 peaked during transient input-guess
                    # generation; only sustained exceedance triggers the kill.
                    if info.get("over_since") is None:
                        info["over_since"] = time.time()
                        log(f"PROBE-WATCH {name}: rss {info['rss_gb']} GB > {PROBE_KILL_GB} GB; 60 s grace")
                    elif time.time() - info["over_since"] > 60:
                        log(f"PROBE-KILL {name}: rss {info['rss_gb']} GB > {PROBE_KILL_GB} GB sustained; terminating")
                        try:
                            os.kill(info["proc"].pid, signal.SIGTERM)
                        except ProcessLookupError:
                            pass
                        info["kill_at"] = time.time()
                        continue
                else:
                    info.pop("over_since", None)
                state[name]["rss_gb"] = info["rss_gb"]
                state[name]["pid"] = info["proc"].pid
                continue
            eks, final = log_final(job_log_by_name(name))
            state[name]["ended"] = now()
            state[name]["rc"] = rc
            if rc == 0 and final:
                state[name]["state"] = "done"
                state[name]["EKS_Ha"] = eks
            else:
                state[name]["state"] = f"failed(rc={rc},final={final})"
            running.pop(name)
            log(f"job {name}: state={state[name]['state']}"
                + (f" EKS={eks}" if eks is not None else ""))
        # --- kill follow-up ---
        for name in list(running):
            info = running[name]
            if info.get("kill_at") and time.time() - info["kill_at"] > 15:
                for pid in tree_pids(info["proc"].pid):
                    try:
                        os.kill(pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                info["proc"].wait()
                state[name]["ended"] = now()
                state[name]["state"] = "failed(killed-probe-rss)"
                running.pop(name)
                log(f"job {name}: SIGKILL after SIGTERM; marked failed(killed-probe-rss)")
        # --- launch new jobs ---
        omp_running = [n for n in running if state[n]["kind"] == "omp"]
        mpi_running = [n for n in running if state[n]["kind"] == "mpi"]
        if not mpi_running and len(omp_running) < 2:
            for name in list(pending):
                job = next(j for j in JOBS if j["name"] == name)
                avail = mem_available_gb()
                if job["kind"] == "mpi":
                    if omp_running or avail < 40.0:
                        continue
                else:
                    running_est = sum(state[n]["est_gb"] or 0 for n in omp_running)
                    factor, margin = (1.05, 2.0) if job["est"] >= BIG_EST_GB else (1.1, 3.0)
                    if avail < running_est + job["est"] * factor + margin:
                        continue
                proc = launch(job)
                running[name] = {"proc": proc, "kind": job["kind"], "started": now()}
                state[name]["state"] = "running"
                state[name]["pid"] = proc.pid
                state[name]["started"] = now()
                pending.remove(name)
                log(f"launched {name}: kind={job['kind']} threads={job['threads']} "
                    f"est={job['est']} GB mem_avail={avail:.1f} GB pid={proc.pid}")
                break
        write_progress()
        if pending or running:
            time.sleep(POLL_S)
    write_progress()
    log("scheduler finished: all jobs settled")

def job_log_by_name(name):
    job = next(j for j in JOBS if j["name"] == name)
    return job_log(job)

if __name__ == "__main__":
    main()
