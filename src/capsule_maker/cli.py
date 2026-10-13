"""CLI; inspecting and importing never execute capsule code."""

import argparse
import json
import sys

from . import (
    CapsuleError,
    Goal,
    LocalFileAdapter,
    approve_capsule,
    capsule_size,
    compare_capsules,
    create_capsule,
    export_capsule,
    extend_capsule,
    import_capsule,
    inspect_capsule,
    resume_knowledge,
    retrieve_content,
    verify_capsule,
    verify_external_artifact,
    verify_parent,
)
from .plugin import prepare_local_plugin


def parser():
    root = argparse.ArgumentParser(prog="capsule-maker")
    commands = root.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create")
    create.add_argument("memory")
    create.add_argument("destination")
    create.add_argument("--goal", required=True)
    create.add_argument("--tag", action="append", default=[])
    for name in ("inspect", "approve", "export", "verify", "resume", "contents"):
        sub = commands.add_parser(name)
        sub.add_argument("capsule")
        if name == "approve":
            sub.add_argument("--reviewer", required=True)
        elif name == "export":
            sub.add_argument("archive")
        elif name == "verify":
            sub.add_argument("--integrity-only", action="store_true")
            sub.add_argument(
                "--trust-code",
                action="store_true",
                help="Run bundled tests with your OS privileges; NOT sandboxed",
            )
        elif name == "resume":
            sub.add_argument("--goal")
            sub.add_argument("--tag", action="append", default=[])
        elif name == "contents":
            sub.add_argument("--path", help="Read an inventoried UTF-8 file")
    extend = commands.add_parser("extend", help="Create an unapproved child; preserve its parent")
    extend.add_argument("parent")
    extend.add_argument("memory")
    extend.add_argument("destination")
    extend.add_argument("--goal", required=True)
    extend.add_argument("--tag", action="append", default=[])
    compare = commands.add_parser("compare")
    compare.add_argument("before")
    compare.add_argument("after")
    parent = commands.add_parser("verify-parent")
    parent.add_argument("capsule")
    parent.add_argument("parent")
    size = commands.add_parser("size")
    size.add_argument("capsule")
    external = commands.add_parser("verify-external")
    external.add_argument("capsule")
    external.add_argument("artifact_id")
    external.add_argument("local_file")
    imp = commands.add_parser("import")
    imp.add_argument("archive")
    imp.add_argument("destination")
    plugin = commands.add_parser("prepare-plugin", help="Prepare a local workspace-bound plugin")
    plugin.add_argument("--workspace", required=True)
    plugin.add_argument("--marketplace", required=True)
    return root


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == "prepare-plugin":
            result = prepare_local_plugin(args.workspace, args.marketplace)
        elif args.command == "create":
            result = create_capsule(
                LocalFileAdapter(args.memory),
                Goal(args.goal, tuple(args.tag)),
                args.destination,
            )
        elif args.command == "extend":
            result = extend_capsule(
                args.parent,
                LocalFileAdapter(args.memory),
                Goal(args.goal, tuple(args.tag)),
                args.destination,
            )
        elif args.command == "compare":
            result = compare_capsules(args.before, args.after)
        elif args.command == "verify-parent":
            result = verify_parent(args.capsule, args.parent)
        elif args.command == "size":
            result = capsule_size(args.capsule)
        elif args.command == "verify-external":
            result = verify_external_artifact(args.capsule, args.artifact_id, args.local_file)
        elif args.command == "inspect":
            result = inspect_capsule(args.capsule)
        elif args.command == "approve":
            result = approve_capsule(args.capsule, args.reviewer)
        elif args.command == "export":
            result = {"archive": str(export_capsule(args.capsule, args.archive))}
        elif args.command == "import":
            result = import_capsule(args.archive, args.destination)
        elif args.command == "verify":
            result = verify_capsule(
                args.capsule,
                environment=not args.integrity_only,
                trust_code=args.trust_code,
            )
        elif args.command == "resume":
            result = resume_knowledge(
                args.capsule, Goal(args.goal, tuple(args.tag)) if args.goal else None
            )
        elif args.command == "contents":
            result = (
                retrieve_content(args.capsule, args.path)
                if args.path
                else inspect_capsule(args.capsule)["inventory"]
            )
        print(
            result if isinstance(result, str) else json.dumps(result, indent=2, ensure_ascii=False)
        )
        return 0
    except (CapsuleError, OSError) as exc:
        print(f"capsule-maker: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
