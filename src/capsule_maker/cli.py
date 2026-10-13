"""CLI; inspecting and importing never execute capsule code."""

import argparse
import json
import sys

from . import (
    CapsuleError,
    Goal,
    LocalFileAdapter,
    approve_capsule,
    create_capsule,
    export_capsule,
    import_capsule,
    inspect_capsule,
    resume_knowledge,
    retrieve_content,
    verify_capsule,
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
    imp = commands.add_parser("import")
    imp.add_argument("archive")
    imp.add_argument("destination")
    plugin = commands.add_parser(
        "prepare-plugin", help="Prepare a local workspace-bound plugin"
    )
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
            result
            if isinstance(result, str)
            else json.dumps(result, indent=2, ensure_ascii=False)
        )
        return 0
    except (CapsuleError, OSError) as exc:
        print(f"capsule-maker: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
